from synkai.verification import CheckResult, classify, reconcile


def check(outcome="passed", assertion=None, collected=1):
    return CheckResult(outcome=outcome, assertion=assertion, collected=collected)


def test_only_expected_original_failure_and_candidate_pass_verify():
    assert classify(check("failed", "discount_once"), check(), check(), "discount_once") == "VERIFIED"


def test_green_repository_suite_does_not_override_behavioral_failure():
    assert classify(check("failed", "discount_once"), check("failed", "discount_once"), check(), "discount_once") == "REJECTED"


def test_placebo_check_cannot_establish_a_fix():
    assert classify(check(), check(), check(), "discount_once") == "INCONCLUSIVE"


def test_unrelated_original_failure_is_not_reproduction():
    assert classify(check("failed", "other"), check(), check(), "discount_once") == "INCONCLUSIVE"


def test_setup_failure_timeout_skip_and_empty_collection_never_verify():
    for result in [check("error"), check("timeout"), check("skipped"), check(collected=0)]:
        assert classify(result, check(), check(), "discount_once") == "INCONCLUSIVE"
        assert classify(check("failed", "discount_once"), result, check(), "discount_once") == "INCONCLUSIVE"


def test_adjacent_regression_rejects_candidate():
    assert classify(check("failed", "discount_once"), check(), check("failed", "empty_cart"), "discount_once") == "REJECTED"


def test_contradictory_replay_cannot_be_erased_by_later_success():
    assert reconcile(["VERIFIED", "REJECTED", "VERIFIED"]) == "INCONCLUSIVE"


def test_incomplete_current_run_does_not_borrow_previous_green_status():
    assert reconcile(["VERIFIED", "INCONCLUSIVE"]) == "INCONCLUSIVE"
