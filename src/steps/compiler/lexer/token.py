"""Definition of :py:class:`Token`, :py:class:`TokenKind` and :py:class:`TokenizerContext`. """
import dataclasses
import enum
import typing


class TokenKind(enum.Enum):
    """Enumerates the allowed :py:class:`token <Token>` types."""
    WHITE_SPACE = '<WS>'
    END_OF_LINE = '<EOL>'
    IDENTIFIER = '<IDENTIFIER>'
    DUMMY_IDENTIFIER = '<DUMMY IDENTIFIER>'
    KW_AND = 'and'
    KW_AS = 'as'
    KW_ASSERT = 'assert'
    KW_AXIOM = 'axiom'
    KW_CASE = 'case'
    KW_DIV = 'div'
    KW_ELSE = 'else'
    KW_EMIT = 'emit'
    KW_ENUM = 'enum'
    KW_EXTENDS = 'extends'
    KW_FINALLY = 'finally'
    KW_FN = 'fn'
    KW_FORWARD = 'forward'
    KW_FORWARDER = 'forwarder'
    KW_FROM = 'from'
    KW_GIVEN = 'given'
    KW_IF = 'if'
    KW_IMPORT = 'import'
    KW_IN = 'in'
    KW_INV = 'inv'
    KW_INITIALLY = 'initially'
    KW_LEMMA = 'lemma'
    KW_LET = 'let'
    KW_MOD = 'mod'
    KW_NEW = 'new'
    KW_NOT = 'not'
    KW_OF = 'of'
    KW_OP = 'op'
    KW_OR = 'or'
    KW_PROC = 'proc'
    KW_PURE = 'pure'
    KW_RETURN = 'return'
    KW_SPAWN = 'spawn'
    KW_SWITCH = 'switch'
    KW_THEOREM = 'theorem'
    KW_THEN = 'then'
    KW_TYPE = 'type'
    KW_VAR = 'var'
    KW_VARIANT = 'variant'
    KW_WHERE = 'where'
    KW_WHILE = 'while'
    KW_XOR = 'xor'
    EOF = '<EOF>'
    ERR_IDENTIFIER = 'ERROR <IDENTIFIER>'
    LEFT_PARENTHESIS = '('
    RIGHT_PARENTHESIS = ')'
    LEFT_BRACKET = '['
    RIGHT_BRACKET = ']'
    LEFT_BRACE = '{'
    RIGHT_BRACE = '}'
    COMMA = ','
    COLON = ':'
    DOT = '.'
    DOTDOT = '..'
    ELLIPSIS = '...'
    RIGHT_ARROW = '->'
    RESERVED_SEMICOLON = ';'
    RESERVED_COMMERCIAL_AT = '@'
    RESERVED_EXCLAMATION_MARK = '!'
    RESERVED_AMPERSAND = '&'
    RESERVED_PERCENT = '%'
    RESERVED_DOLLAR = '$'

    OP_EQ = '='
    OP_LT = '<'
    OP_GT = '>'
    OP_LEQ = '<='
    OP_GEQ = '>='
    OP_NEQ = '<>'
    OP_ASSIGN = ':='
    OP_CROSS = '><'
    OP_PLUS = '+'
    OP_MINUS = '-'
    OP_MULTIPLY = '*'
    OP_DIVIDE = '/'
    OP_PLUS_ASSIGN = '+='
    OP_MINUS_ASSIGN = '-='
    OP_MULTIPLY_ASSIGN = '*='
    OP_DIVIDE_ASSIGN = '/='
    OP_EXPONENT = '^'

    OP_CIRCLED_EQ = '(=)'
    OP_CIRCLED_LT = '(<)'
    OP_CIRCLED_GT = '(>)'
    OP_CIRCLED_LEQ = '(<=)'
    OP_CIRCLED_GEQ = '(>=)'
    OP_CIRCLED_NEQ = '(<>)'
    OP_CIRCLED_CROSS = '(><)'
    OP_CIRCLED_PLUS = '(+)'
    OP_CIRCLED_MINUS = '(-)'
    OP_CIRCLED_MULTIPLY = '(*)'
    OP_CIRCLED_DIVIDE = '(/)'
    OP_CIRCLED_DOT = '(.)'

    OP_BOXED_EQ = '[=]'
    OP_BOXED_LT = '[<]'
    OP_BOXED_GT = '[>]'
    OP_BOXED_LEQ = '[<=]'
    OP_BOXED_GEQ = '[>=]'
    OP_BOXED_NEQ = '[<>]'
    OP_BOXED_CROSS = '[><]'
    OP_BOXED_PLUS = '[+]'
    OP_BOXED_MINUS = '[-]'
    OP_BOXED_MULTIPLY = '[*]'
    OP_BOXED_DIVIDE = '[/]'
    OP_BOXED_DOT = '[.]'

    OP_PARENTHESES = '()'
    OP_BRACKETS = '[]'
    OP_BRACES = '{}'

EXTRA_TOKENS: typing.Set[TokenKind] = {
        TokenKind.WHITE_SPACE
}

@dataclasses.dataclass(frozen=True)
class Token:
    """
    Describes a token.

    """
    kind: TokenKind
    img: str
    line: int
    column: int
    extra: typing.Sequence['Token'] = dataclasses.field(default_factory=list)


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

