"""Running the lexer feature tests."""
import io
from typing import Sequence, TextIO

from pytest_bdd import (
    given,
    parsers,
    scenario,
    then,
    when,
)

from steps.compiler.lexer import tokenize
from steps.compiler.lexer.token import Token, TokenKind, TokenizerError


@scenario('features/lexer.feature', 'Scan valid input and return a list of tokens')
def test_scan_valid_input_and_return_a_list_of_tokens():
    """Scan valid input and return a list of tokens."""


@given(parsers.parse('the following input: {source_str}'), target_fixture='source')
def the_following_input(source_str: str) -> TextIO:
    """the following input: <input>"""
    return io.StringIO(source_str)

@given('the input consisting only of a BOM character', target_fixture='source')
def the_input_consisting_only_of_a_bom_character() -> TextIO:
    """the input consisting only of a BOM character."""
    return io.StringIO('\uFEFF')

@given('the emptyinput', target_fixture='source')
def the_empty_input() -> TextIO:
    """the empty input."""
    return io.StringIO('')

@when('the `tokenize` function is run', target_fixture='token_list')
def the__tokenize_function_is_run(source: TextIO) -> Sequence[Token]:
    """the `tokenize` function is run"""
    return list(tokenize(source))

@then(parsers.re(r'the token kinds returned by `tokenize` are (?P<token_kinds>[ A-Z0-9_]+)'))
def the_token_kinds_returned_by_tokenize_are_token_kinds(
    token_list: Sequence[Token],
    token_kinds: str,
) -> None:
    """the token kinds resturned by `tokenize` are <token kinds>"""
    actual_token_kinds = [token.kind for token in token_list]
    expected_token_kinds = [TokenKind[kind_name] for kind_name in token_kinds.split()]
    expected_token_kinds.append(TokenKind.EOF)
    assert actual_token_kinds == expected_token_kinds

