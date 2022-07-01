"""Test the lexer."""

import pytest

from steps.compiler.lexer import tokenize


def test_lexer_01() -> None:
    tokens = list(tokenize('''
        if x
            while x100 y_thing _not_relevant
    '''))
    assert tokens == []
