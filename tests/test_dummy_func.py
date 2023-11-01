import pytest
from PyCustomCollections.CustomDataStructures import dummy_func


def test_dummy_func_is_callable():
    assert callable(dummy_func) is True


def test_dummy_func_without_args():
    assert dummy_func() is None


def test_dummy_func_default():
    output = "Test"
    assert dummy_func(_default=output) == output
