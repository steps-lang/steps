"""Lexical analysis for the STEPS language."""
import typing

from .token import Token, TokenKind, Tokenizer, TokenizerContext
from .states import tok_start as _tok_start


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
            char: str = source.read(1)
            if not char:
                char = '\x00'
            tokens, state = state(char, context)
            context.is_at_bof = False
            is_token_unfinished = True
            for token in tokens:
                if token:
                    yield token
                    is_token_unfinished = False
                else:
                    is_token_unfinished = True

            if is_eof(char):
                break
        if is_token_unfinished:
            raise TokenizerError(f'Unexpected end of file', context)
    except TokenizerError as err:
        err.state = state
        raise

