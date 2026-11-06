import json
from pathlib import Path
import pytest

calls = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    report.synkai_assertion = bool(
        call.when == "call" and call.excinfo and call.excinfo.type is AssertionError
        and Path(call.excinfo.traceback[-1].path).resolve() == Path(item.path).resolve())


def pytest_runtest_logreport(report):
    calls.append(report)


def pytest_sessionfinish(session, exitstatus):
    skipped = sum(report.skipped for report in calls)
    errors = sum(report.failed and not getattr(report, "synkai_assertion", False) for report in calls)
    failures = [report.nodeid.split("::")[-1] for report in calls if report.failed and getattr(report, "synkai_assertion", False)]
    outcome = "failed" if failures else "passed"
    if exitstatus not in (0, 1) or not session.testscollected:
        outcome = "error"
    print("\nSYNKAI_REPORT:" + json.dumps({"outcome": outcome, "assertion": failures[0] if failures else None,
        "collected": session.testscollected, "skipped": skipped, "errors": errors}))
