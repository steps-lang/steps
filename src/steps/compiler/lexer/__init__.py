"""Lexical analysis for the STEPS language."""
import typing

from .classes import is_eof
from .token import Token, TokenKind, Tokenizer, TokenizerContext, TokenizerError, EXTRA_TOKENS
from .states import tok_start as _tok_start

def _next_char(source: typing.TextIO) -> str:
    char: str = source.read(1)
    if not char:
        return '\x00'
    return char


def tokenize(source: typing.TextIO, start_state: Tokenizer = _tok_start) -> typing.Iterator[Token]:
    """
    Iterate over all tokens of an input stream.

    :param source: the source stream to be scanned
    :type source: typing.TextIO
    :param start_state: optional start state if you need to start from some unsusual place.
    :type start_state: Tokenizer
    :return: an iterator of :py:class:`tokens <Token>`
    :rtype: typing.Iterator[Token]
    """
    context: TokenizerContext = TokenizerContext()
    state: Tokenizer = start_state
    is_token_unfinished: bool = False
    try:
        while True:
            char: str = _next_char(source)
            tokens, state = state(char, context)
            context.is_at_bof = False
            is_token_unfinished: bool = True
            for token in tokens:
                is_token_unfinished = not bool(token)
                if token and token.kind not in EXTRA_TOKENS:
                    yield token
            if classes.is_eof(char):
                if is_token_unfinished:
                    raise TokenizerError(f'Unexpected end of file', context)
                break
    except TokenizerError as err:
        err.state = state
        raise

