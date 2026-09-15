"""JSON Schema loading, registry construction, and artifact validation."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from dbmodernize.errors import Finding, FindingSet, InputNotFoundError
from dbmodernize.utils.io import read_json

CONTRACT_DIR_NAME = "contracts"


def contracts_dir(repo_root: Path) -> Path:
    path = repo_root / CONTRACT_DIR_NAME
    if not path.is_dir():
        raise InputNotFoundError(f"Contracts directory not found at {path}")
    return path


@functools.lru_cache(maxsize=8)
def _load_all(contracts: Path) -> tuple[dict[str, dict[str, Any]], Registry[Any]]:
    """Load every schema and build a registry keyed by each schema's ``$id``.

    Relative ``$ref`` values such as ``common.schema.json#/$defs/identifier`` resolve
    against the referring schema's ``$id``, so registering by ``$id`` is what makes
    cross-file references work without network access.
    """
    schemas: dict[str, dict[str, Any]] = {}
    resources: list[tuple[str, Resource[Any]]] = []

    for path in sorted(contracts.glob("*.schema.json")):
        document = read_json(path)
        schema_id = document.get("$id")
        if not schema_id:
            raise InputNotFoundError(f"{path} has no $id; cross-file $ref cannot resolve")
        stem = path.name.removesuffix(".schema.json")
        schemas[stem] = document
        resources.append((schema_id, DRAFT202012.create_resource(document)))

    registry: Registry[Any] = Registry().with_resources(resources)
    return schemas, registry


def load_schemas(repo_root: Path) -> dict[str, dict[str, Any]]:
    schemas, _ = _load_all(contracts_dir(repo_root))
    return schemas


def get_validator(repo_root: Path, contract: str) -> Draft202012Validator:
    schemas, registry = _load_all(contracts_dir(repo_root))
    if contract not in schemas:
        available = ", ".join(sorted(schemas))
        raise InputNotFoundError(f"No contract named {contract!r}. Available: {available}")
    return Draft202012Validator(schemas[contract], registry=registry)


def validate_instance(
    repo_root: Path,
    contract: str,
    instance: Any,
    source_path: str = "",
) -> FindingSet:
    """Validate one instance against one contract, returning every error found."""
    findings = FindingSet()
    validator = get_validator(repo_root, contract)
    for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        pointer = "/".join(str(part) for part in error.absolute_path)
        location = f"{source_path}#/{pointer}" if pointer else source_path
        findings.add(
            rule=f"SCHEMA-{contract.upper()}",
            message=error.message,
            path=location,
            hint=f"Schema keyword: {error.validator}",
        )
    return findings


def check_schema_self_validity(repo_root: Path) -> FindingSet:
    """Every schema must itself be a valid 2020-12 schema."""
    findings = FindingSet()
    schemas, _ = _load_all(contracts_dir(repo_root))
    for name, document in sorted(schemas.items()):
        try:
            Draft202012Validator.check_schema(document)
        except Exception as exc:  # noqa: BLE001 - surfaced as a finding, not a crash
            findings.add(
                rule="SCHEMA-INVALID",
                message=f"{name}.schema.json is not a valid JSON Schema: {exc}",
                path=f"contracts/{name}.schema.json",
            )
    return findings


def collect_properties(
    schema: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
    _seen: frozenset[str] = frozenset(),
) -> set[str]:
    """Collect every property name a schema accepts, following ``allOf`` and ``$ref``.

    Used by the schema/model alignment test. Only local references into ``contracts/``
    are followed; anything else is ignored because it cannot affect the local shape.
    """
    names: set[str] = set(schema.get("properties", {}))

    for branch in schema.get("allOf", []):
        ref = branch.get("$ref")
        if ref:
            names |= _resolve_ref(ref, schemas, _seen)
        else:
            names |= collect_properties(branch, schemas, _seen)
    return names


def collect_required(schema: dict[str, Any], schemas: dict[str, dict[str, Any]]) -> set[str]:
    """Collect required property names, following ``allOf`` and ``$ref``."""
    required: set[str] = set(schema.get("required", []))
    for branch in schema.get("allOf", []):
        ref = branch.get("$ref")
        if ref:
            target = _dereference(ref, schemas)
            if target:
                required |= set(target.get("required", []))
        else:
            required |= collect_required(branch, schemas)
    return required


def _dereference(ref: str, schemas: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    if "#" not in ref:
        return None
    file_part, pointer = ref.split("#", 1)
    stem = Path(file_part).name.removesuffix(".schema.json") if file_part else None
    document = schemas.get(stem) if stem else None
    if document is None:
        return None
    node: Any = document
    for token in [t for t in pointer.split("/") if t]:
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or token not in node:
            return None
        node = node[token]
    return node if isinstance(node, dict) else None


def _resolve_ref(ref: str, schemas: dict[str, dict[str, Any]], seen: frozenset[str]) -> set[str]:
    if ref in seen:
        return set()
    target = _dereference(ref, schemas)
    if target is None:
        return set()
    return collect_properties(target, schemas, seen | {ref})


def findings_to_exception_message(findings: FindingSet, subject: str) -> str:
    lines = [f"{subject}: {len(findings.errors)} error(s)"]
    lines.extend(f"  {finding.render()}" for finding in findings.errors)
    return "\n".join(lines)


__all__ = [
    "Finding",
    "FindingSet",
    "check_schema_self_validity",
    "collect_properties",
    "collect_required",
    "contracts_dir",
    "findings_to_exception_message",
    "get_validator",
    "load_schemas",
    "validate_instance",
]
