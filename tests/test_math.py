import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from mathserver import add, subtract, multiply


def test_add():
    assert add(2, 5) == 7


def test_substract():
    assert subtract(9, 8) == 1


def test_multiply():
    assert multiply(4, 5) == 20
