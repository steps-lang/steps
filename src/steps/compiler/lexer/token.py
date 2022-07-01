"""Definition of :py:class:`Token`, :py:class:`TokenKind` and :py:class:`TokenizerContext`. """
import dataclasses
import enum
import typing


class TokenKind(enum.Enum):
    """Enumerates the allowed :py:class:`token <Token>` types."""
    WHITE_SPACE = enum.auto()
    END_OF_LINE = enum.auto()
    IDENTIFIER = enum.auto()
    DUMMY_IDENTIFIER = enum.auto()
    KW_IF = enum.auto()
    KW_AND = ENUM.AUTO()
    KW_AS = ENUM.AUTO()
    KW_ASSERT = ENUM.AUTO()
    KW_AXIOM = ENUM.AUTO()
    KW_CASE = ENUM.AUTO()
    KW_DIV = ENUM.AUTO()
    KW_ELSE = ENUM.AUTO()
    KW_EMIT = ENUM.AUTO()
    KW_ENUM = ENUM.AUTO()
    KW_EXTENDS = ENUM.AUTO()
    KW_FINALLY = ENUM.AUTO()
    KW_FN = ENUM.AUTO()
    KW_FORWARD = ENUM.AUTO()
    KW_FORWARDER = ENUM.AUTO()
    KW_FROM = ENUM.AUTO()
    KW_GIVEN = ENUM.AUTO()
    KW_IF = ENUM.AUTO()
    KW_IMPORT = ENUM.AUTO()
    KW_IN = ENUM.AUTO()
    KW_INV = ENUM.AUTO()
    KW_INITIALLY = ENUM.AUTO()
    KW_LEMMA = ENUM.AUTO()
    KW_LET = ENUM.AUTO()
    KW_MOD = ENUM.AUTO()
    KW_NEW = ENUM.AUTO()
    KW_NOT = ENUM.AUTO()
    KW_OF = ENUM.AUTO()
    KW_OP = ENUM.AUTO()
    KW_OR = ENUM.AUTO()
    KW_PROC = ENUM.AUTO()
    KW_PURE = ENUM.AUTO()
    KW_RETURN = ENUM.AUTO()
    KW_SPAWN = ENUM.AUTO()
    KW_SWITCH = ENUM.AUTO()
    KW_THEOREM = ENUM.AUTO()
    KW_THEN = ENUM.AUTO()
    KW_TYPE = ENUM.AUTO()
    KW_VAR = ENUM.AUTO()
    KW_VARIANT = ENUM.AUTO()
    KW_WHERE = ENUM.AUTO()
    KW_WHILE = ENUM.AUTO()
    KW_XOR = ENUM.AUTO()
    EOF = enum.auto()
    ERR_IDENTIFIER = enum.auto()

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

