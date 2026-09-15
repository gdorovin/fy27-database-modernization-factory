"""Deterministic scoring: assessment rules, target comparison, wave planning."""

from __future__ import annotations

from dbmodernize.scoring.assessment import assess
from dbmodernize.scoring.classification import (
    classify,
    requires_application_change,
    requires_conversion,
)
from dbmodernize.scoring.plan import build_plan
from dbmodernize.scoring.reference import REVALIDATION_NOTE, VERIFIED_ON
from dbmodernize.scoring.targets import evaluate, recommend, recommend_all
from dbmodernize.scoring.validation_plan import build_validation_plan
from dbmodernize.scoring.waves import plan_waves

__all__ = [
    "REVALIDATION_NOTE",
    "VERIFIED_ON",
    "assess",
    "build_plan",
    "build_validation_plan",
    "classify",
    "evaluate",
    "plan_waves",
    "recommend",
    "recommend_all",
    "requires_application_change",
    "requires_conversion",
]
