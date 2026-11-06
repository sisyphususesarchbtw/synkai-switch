"""A result is execution evidence, never an agent's assertion of success."""
from dataclasses import dataclass
from typing import Literal

Outcome = Literal["VERIFIED", "REJECTED", "INCONCLUSIVE"]


@dataclass(frozen=True)
class CheckResult:
    outcome: str
    assertion: str | None = None
    collected: int = 1
    output: str = ""

    @property
    def executable(self) -> bool:
        return self.collected > 0 and self.outcome in {"passed", "failed"}


def classify(base: CheckResult, candidate: CheckResult, regression: CheckResult,
             expected_assertion: str) -> Outcome:
    if not all(x.executable for x in (base, candidate, regression)):
        return "INCONCLUSIVE"
    if base.outcome != "failed" or base.assertion != expected_assertion:
        return "INCONCLUSIVE"
    if candidate.outcome == "failed" or regression.outcome == "failed":
        return "REJECTED"
    return "VERIFIED"


def reconcile(outcomes: list[str]) -> str:
    if not outcomes:
        return "INCONCLUSIVE"
    if {"VERIFIED", "REJECTED"}.issubset(outcomes):
        return "INCONCLUSIVE"
    return outcomes[-1]
