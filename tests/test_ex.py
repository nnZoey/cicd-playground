import pytest

def test_pass():
    """This test will pass."""
    assert 1 + 1 == 2

def test_fail():
    """This test will fail."""
    assert 1 + 1 == 3

def test_another_fail():
    """Another failing test."""
    assert "hello".upper() == "HELLOO"
