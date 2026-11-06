"""Frozen controlled-fixture contract, independent of candidate test files."""
import importlib.util

spec = importlib.util.spec_from_file_location("subject_cart", "/subject/cart.py")
cart = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cart)


def test_coupon_applies_once():
    assert cart.total_after_coupon(10000, 10) == 9000, "A 10% coupon on 10000 cents must leave 9000, not apply twice."


def test_adjacent_zero_coupon():
    assert cart.total_after_coupon(10000, 0) == 10000


def test_adjacent_empty_cart():
    assert cart.total_after_coupon(0, 10) == 0
