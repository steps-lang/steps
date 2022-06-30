"""
Lexical analysis for STEPS.

This module contains the lexical analysis for the STEPS language.
It scans a stream of characters into a sequence of :py:class:`tokens <Token>`.
"""
import dataclasses
import enum
import typing
import unicodedata


class TokenKind(enum.Enum):
    """Enumerates the allowed :py:class:`token <Token>` types."""
    WHITE_SPACE = enum.auto()
    END_OF_LINE = enum.auto()
    IDENTIFIER = enum.auto()
    KW_IF = enum.auto()
    EOF = enum.auto()

    @classmethod
    def check_keywords(cls, term: str) -> 'TokenKind':
        """
        Determine whether the given term is an identifier or a keyword.

        :param term: the term to be checked
        :type term: str
        :return: the corresponding token kind
        :rtype: TokenKind
        """
        if term == 'if':
            return TokenKind.KW_IF
        return TokenKind.IDENTIFIER

@dataclasses.dataclass(frozen=True)
class Token:
    """
    Describes a token.

    """
    kind: TokenKind
    img: str
    line: int
    column: int


@dataclasses.dataclass
class TokenizerContext:
    """Global context for the tokenization process for a single file or stream."""
    is_at_bof: bool = True
    current_line: int = 1
    current_column: int = 0
    more: str = ''
    more_line: int = -1
    more_column: int = -1

    def add_more(self, char: str) -> None:
        """
        Add a character to the ``more`` field.

        :param char: the character to be added
        :type char: str
        """
        if not self.more:
            self.more_line = self.current_line
            self.more_column = self.current_column
        self.more += char

    def terminate_more(self, kind: TokenKind) -> Token:
        """
        Reset the ``more`` field.

        :param kind: token kind for constructing a token
        :type kind: TokenKind
        :return: token constructed from the ``more`` field before resetting.
        :rtype: Token
        """
        result: Token = Token(kind, self.more, self.more_line, self.more_column)
        self.more = ''
        self.more_line = -1
        self.more_column = -1
        return result

    def terminate_and_forward(self,
            kind: TokenKind,
            char: str,
            forward_state: 'Tokenizer'
    ) -> 'TokenizerResult':
        """
        Create a token from terminating the ``more`` field and forward to the given state.

        :param kind: token kind for constructing a token
        :type kind: TokenKind
        :param char: the character, which is forwarded
        :type char: str
        :param forward_state: the state handling the forwarded character
        :type forward_state: Tokenizer
        :return: the generated token plus the result from the forwarded state
        :rtype: TokenizerResult
        """
        term_token = self.terminate_more(kind)
        next_tokens, next_state = forward_state(char, self)
        return ([term_token] + next_tokens, next_state)

    def next_line(self) -> None:
        """Adjust the line and column counter to account for a new line."""
        self.current_line += 1
        self.current_column = 0


TokenizerResult = typing.Tuple[typing.Sequence[Token], 'Tokenizer']
Tokenizer = typing.Callable[[str, TokenizerContext], TokenizerResult]


def state_summary(state: Tokenizer) -> str:
    """
    Extract some summary from a given lexer state.

    :param state: the state which needs to be summarized.
    :type state: Tokenizer
    :return: the summary of the given state
    :rtype: str
    """
    doc_lines: typing.List[str] = list(filter(bool, map(str.strip, state.__doc__.splitlines())))
    if doc_lines:
        return doc_lines[0]
    return state.__name__


class TokenizerError(Exception):
    """
    Error which is raised by the tokenizer.

    :param message: the error message
    :type message: str
    """
    def __init__(self, message: str, context: TokenizerContext) -> None:
        """Initialize a new instance."""
        super().__init__(message)
        self._message: str = message
        self._line: int = context.current_line
        self._column: int = context.current_column
        self._state: typing.Optional[Tokenizer] = None

    def __str__(self) -> str:
        """
        Generate an error message with context information.

        :return: the error message
        :rtype: str
        """
        result: str = f'At [{self.line}:{self.column}]: {self.message}'
        if self.state:
            result += ' (' + state_summary(self.state) + ')'
        return result
    
    @property
    def line(self) -> int:
        """
        Return the line number in the tokenized source where this error was raised.

        :return: the line number
        :rtype: int
        """
        return self._line
    
    @property
    def column(self) -> int:
        """
        Return the column in the tokenized source where this error was raised.

        :return: the column number
        :rtype: int
        """
        return self._column
    
    @property
    def message(self) -> str:
        """
        Return the undecorated message for this error.

        :return: the error message
        :rtype: str
        """
        return self._message

    @property
    def state(self) -> typing.Optional[Tokenizer]:
        """
        Return the state of the tokenizer at which this error occurred.

        :return: the tokenizer state
        :rtype: typing.Optional[Tokenizer]
        """
        return self._state

    @state.setter
    def state(self, new_state: Tokenizer) -> None:
        """
        Set the state of the tokenizer at which this error occurred.

        :param new_state: the tokenizer state
        :type new_state: Tokenizer
        """
        self._state = new_state

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
    if is_identifier_start(char):
        return tok_identifier(char, context)
    if is_eol(char):
        return tok_eol(char, context)
    if char.isspace():
        return tok_whitespace(char, context)
    if char == '\uFEFF' and context.is_at_bof:
        return ([], tok_start)
    if is_eof(char):
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
    if is_eol(char):
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
    if is_eol(char):
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
    if is_identifier_continue(char):
        context.add_more(char)
        return ([], tok_identifier)
    if is_identifier_connector(char):
        context.add_more(char)
        return ([], tok_identifier_connector)
    return context.terminate_and_forward(TokenKind.check_keyword(context.more), char, tok_start)

def tokenize(source: typing.TextIO, start_state: Tokenizer = tok_start) -> typing.Iterator[Token]:
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

