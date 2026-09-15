#!/usr/bin/env python
"""Convert a real assessment export into a synthetic fixture.

Replaces identifiers with stable pseudonyms and scrubs free text. The mapping is
deterministic within a run, so relationships between records survive while the underlying
values do not.

This is an aid, not a guarantee. Review the output before committing it. Redaction cannot
know that a database called "Project Hummingbird" is the customer's unannounced product.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.utils.redaction import redact  # noqa: E402

#: Fields replaced with a stable pseudonym rather than a mask, so joins still work.
PSEUDONYM_FIELDS = frozenset(
    {
        "name",
        "databaseName",
        "instanceName",
        "host",
        "hostAlias",
        "hostname",
        "server",
        "serverName",
        "owner",
        "customer",
        "customerName",
        "sourceSchema",
        "workloadName",
    }
)

#: Fields whose free text is scrubbed but whose shape is kept.
FREE_TEXT_FIELDS = frozenset({"notes", "description", "comment", "comments", "justification"})

DROP_FIELDS = frozenset(
    {"connectionString", "password", "secret", "token", "apiKey", "subscriptionId", "tenantId"}
)

_FQDN = re.compile(r"\b[\w-]+(\.[\w-]+){2,}\b")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", re.IGNORECASE)
_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


class Pseudonymiser:
    """Stable, deterministic pseudonyms. The same input always yields the same alias."""

    def __init__(self, prefix: str = "alias") -> None:
        self.prefix = prefix
        self._seen: dict[str, str] = {}

    def __call__(self, value: str) -> str:
        key = value.strip().lower()
        if key not in self._seen:
            digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:6]
            self._seen[key] = f"{self.prefix}-{len(self._seen) + 1:02d}-{digest}"
        return self._seen[key]

    @property
    def mapping(self) -> dict[str, str]:
        return dict(self._seen)


def scrub_text(text: str) -> str:
    text = redact(text)
    text = _EMAIL.sub("person@contoso.example", text)
    text = _FQDN.sub("host.contoso.example", text)
    text = _IPV4.sub("203.0.113.1", text)
    return text


def transform(node: Any, alias: Pseudonymiser) -> Any:
    if isinstance(node, dict):
        result: dict[str, Any] = {}
        for key, value in node.items():
            if key in DROP_FIELDS:
                result[key] = "REDACTED"
            elif key in PSEUDONYM_FIELDS and isinstance(value, str):
                result[key] = alias(value)
            elif key in FREE_TEXT_FIELDS and isinstance(value, str):
                result[key] = scrub_text(value)
            else:
                result[key] = transform(value, alias)
        return result
    if isinstance(node, list):
        return [transform(item, alias) for item in node]
    if isinstance(node, str):
        return scrub_text(node)
    return node


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Real export to redact.")
    parser.add_argument("destination", type=Path, help="Where to write the synthetic fixture.")
    parser.add_argument("--prefix", default="alias", help="Pseudonym prefix.")
    parser.add_argument(
        "--mapping",
        type=Path,
        help="Optional path for the alias mapping. Keep it outside this repository.",
    )
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"Source not found: {args.source}", file=sys.stderr)
        return 3
    if args.destination.exists():
        print(f"Destination already exists: {args.destination}", file=sys.stderr)
        return 4

    alias = Pseudonymiser(args.prefix)
    document = json.loads(args.source.read_text(encoding="utf-8"))
    redacted = transform(document, alias)

    args.destination.parent.mkdir(parents=True, exist_ok=True)
    with args.destination.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(redacted, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    if args.mapping:
        with args.mapping.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(alias.mapping, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"Alias mapping written to {args.mapping}.")
        print("The mapping re-identifies the data. Never commit it to this repository.")

    print(f"Wrote {args.destination} with {len(alias.mapping)} pseudonym(s).")
    print(
        "Review it before committing. Redaction is an aid, not a guarantee: it cannot know "
        "that a project codename is confidential."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
