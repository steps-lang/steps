"""
Lexer states for the lexical analysis for STEPS.

This module contains the lexical states defining the lexer for the STEPS language.
"""
import typing

from . import classes
from .token import Token, TokenKind, Tokenizer, TokenizerContext, TokenizerError, TokenizerResult


KEYWORDS: typing.Sequence[str] = (
        'and',
        'as',
        'assert',
        'axiom',
        'case',
        'div',
        'else',
        'emit',
        'enum',
        'extends',
        'finally',
        'fn',
        'forward',
        'forwarder',
        'from',
        'given',
        'if',
        'import',
        'in',
        'inv',
        'initially',
        'lemma',
        'let',
        'mod',
        'new',
        'not',
        'of',
        'op',
        'or',
        'proc',
        'pure',
        'return',
        'spawn',
        'switch',
        'theorem',
        'then',
        'type',
        'var',
        'variant',
        'where',
        'while',
        'xor',
)

def check_keywords(term: str) -> 'TokenKind':
    """
    Determine whether the given term is an identifier or a keyword.

    :param term: the term to be checked
    :type term: str
    :return: the corresponding token kind
    :rtype: TokenKind
    """
    if term in KEYWORDS:
        return TokenKind['KW_' + term.upper()]
    if term.startswith('_'):
        return TokenKind.DUMMY_IDENTIFIER
    return TokenKind.IDENTIFIER


def tok_start(char: str, context: TokenizerContext) -> TokenizerResult:
    """
    Expect a new token.

    :param char: the next character to be read
    :type char: str
    :param context: the current tokenizer context
    :type context: TokenizerContext
    :return: the previously generated token if the current character terminates a token or ``None``
        if no token has been generated plus the :py:type:`Tokenizer` representing the next state.
    :rtype: TokenizerResult
    :raise TokenizerError: if an unexpected character is encountered
    """
    if classes.is_identifier_start(char) or char == '_':
        return tok_identifier(char, context)
    if classes.is_eol(char):
        return tok_eol(char, context)
    if char.isspace():
        return tok_whitespace(char, context)
    if char == '\uFEFF' and context.is_at_bof:
        return ([], tok_start)
    if classes.is_eof(char):
        return (
                [Token(TokenKind.EOF, char, context.current_line, context.current_column)],
                tok_start
        )
    raise TokenizerError(f'Unexpected character {char!r}', context)

def tok_whitespace(char: str, context: TokenizerContext) -> TokenizerResult:
    """
    Scan white space.

    :param char: the next character to be read
    :type char: str
    :param context: the current tokenizer context
    :type context: TokenizerContext
    :return: the previously generated token if the current character terminates a token or ``None``
        if no token has been generated plus the :py:type:`Tokenizer` representing the next state.
    :rtype: TokenizerResult
    :raise TokenizerError: if an unexpected character is encountered
    """
    if classes.is_eol(char):
        return context.terminate_and_forward(TokenKind.WHITE_SPACE, char, tok_eol)
    if char.isspace():
        context.add_more(char)
        return ([], tok_whitespace)
    if char == '#':
        return tok_comment(char, context)
    return context.terminate_and_forward(TokenKind.WHITE_SPACE, char, tok_start)

def tok_comment(char: str, context: TokenizerContext) -> TokenizerResult:
    """
    Scan a comment.

    :param char: the next character to be read
    :type char: str
    :param context: the current tokenizer context
    :type context: TokenizerContext
    :return: the previously generated token if the current character terminates a token or ``None``
        if no token has been generated plus the :py:type:`Tokenizer` representing the next state.
    :rtype: TokenizerResult
    :raise TokenizerError: if an unexpected character is encountered
    """
    if classes.is_eol(char):
        return context.terminate_and_forward(TokenKind.WHITE_SPACE, char, tok_start)
    context.add_more(char)
    return ([], tok_comment)

def tok_eol(char: str, context: TokenizerContext) -> TokenizerResult:
    """
    Scan a comment.

    :param char: the next character to be read
    :type char: str
    :param context: the current tokenizer context
    :type context: TokenizerContext
    :return: the previously generated token if the current character terminates a token or ``None``
        if no token has been generated plus the :py:type:`Tokenizer` representing the next state.
    :rtype: TokenizerResult
    :raise TokenizerError: if an unexpected character is encountered
    """
    if char == '\n':
        context.add_more(char)
        return ([], tok_eol)
    if char == '\r':
        context.add_more(char)
        context.next_line()
        return ([context.terminate_more(TokenKind.END_OF_LINE)], tok_start)
    context.next_line()
    return context.terminate_and_forward(TokenKind.END_OF_LINE, char, tok_start)

def tok_identifier(char: str, context: TokenizerContext) -> TokenizerResult:
    """
    Scan an identifer.

    :param char: the next character to be read
    :type char: str
    :param context: the current tokenizer context
    :type context: TokenizerContext
    :return: the previously generated token if the current character terminates a token or ``None``
        if no token has been generated plus the :py:type:`Tokenizer` representing the next state.
    :rtype: TokenizerResult
    :raise TokenizerError: if an unexpected character is encountered
    """
    if classes.is_identifier_continue(char):
        context.add_more(char)
        return ([], tok_identifier)
    if classes.is_identifier_connector(char):
        context.add_more(char)
        return ([], tok_identifier_connector)
    return context.terminate_and_forward(check_keywords(context.more), char, tok_start)

def tok_identifier_connector(char: str, context: TokenizerContext) -> TokenizerResult:
    """
    Scan an identifer -- the part which is allowed after an identifier connector.

    :param char: the next character to be read
    :type char: str
    :param context: the current tokenizer context
    :type context: TokenizerContext
    :return: the previously generated token if the current character terminates a token or ``None``
        if no token has been generated plus the :py:type:`Tokenizer` representing the next state.
    :rtype: TokenizerResult
    :raise TokenizerError: if an unexpected character is encountered
    """
    if classes.is_identifier_continue(char):
        context.add_more(char)
        return ([], tok_identifier)
    if classes.is_identifier_connector(char):
        context.add_more(char)
        return ([], err_identifier)
    return context.terminate_and_forward(check_keywords(context.more), char, tok_start)

def err_identifier(char: str, context: TokenizerContext) -> TokenizerResult:
    """
    Scan an errorneous identifier.

    :param char: the next character to be read
    :type char: str
    :param context: the current tokenizer context
    :type context: TokenizerContext
    :return: the previously generated token if the current character terminates a token or ``None``
        if no token has been generated plus the :py:type:`Tokenizer` representing the next state.
    :rtype: TokenizerResult
    :raise TokenizerError: if an unexpected character is encountered
    """
    if classes.is_identifier_continue(char) or classes.is_identifier_connector(char):
        context.add_more(char)
        return ([], err_identifier)
    return context.terminate_and_forward(TokenKind.ERR_IDENTIFIER, char, tok_start)

