"""
Character classes for the STEPS lexer.

This module contains the necessary classifications of characters
for the STEPS lexer.
"""
import unicodedata

def is_eof(char: str) -> bool:
    """
    Return whether a character is considered to be an end-of-file marker.

    An end-of-file marker is either ASCII ``0x00`` or ``0x1A``.
    The physical end of file is converted to ``0x00`` by the tokenizer
    beforehand.

    :param char: the character to be tested
    :type char: str
    :return: true if the character is an end-of-file marker.
    """
    return char in ('\x00', '\x1A')

def is_eol(char: str) -> bool:
    """
    Return whether a character is considered to be an end-of-line marker.

    :param char: the character to be tested
    :type char: str
    :return: true if the character is an end-of-line marker.
    """
    return char in ('\r', '\n')

def is_identifier_start(char: str) -> bool:
    """
    Return whether a character is considered to be the start of an identifier.

    :param char: the character to be tested
    :type char: str
    :return: true if the character is the start of an identifier
    """
    return unicodedata.category(char) in ('Ll', 'Lm', 'Lo', 'Lt', 'Lu', 'Nl')
    
def is_identifier_continue(char: str) -> bool:
    """
    Return whether a character is considered to be the continue part of an identifier.

    :param char: the character to be tested
    :type char: str
    :return: true if the character is the continue part of an identifier
    """
    return unicodedata.category(char) in ('Ll', 'Lm', 'Lo', 'Lt', 'Lu', 'Nd', 'Nl', 'Mn', 'Mc')
    
def is_identifier_connector(char: str) -> bool:
    """
    Return whether a character is considered to be the connector part of an identifier.

    :param char: the character to be tested
    :type char: str
    :return: true if the character is the connector part of an identifier
    """
    return unicodedata.category(char) == 'Pc'

def is_symbolic(char: str) -> bool:
    """
    Return whether a character is considered to be symbolic

    :param char: the character to be tested
    :type char: str
    :return: true if the character is the continue part of an identifier
    """
    return char in '!$%&()*+,-./:;<=>?@[\\]^{|}~'

