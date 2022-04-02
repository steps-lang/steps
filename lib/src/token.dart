/// This module declare the [TokenKind] enumeration and the [Token] type.
///

enum TokenKind {
  characterLiteral,
  stringLiteral,
  verbatimStringLiteral,
  integerLiteral,
  floatLiteral,
  lowerIdentifier,
  upperIdentifier,
  dummyIdentifier,
  whiteSpace,
  lineFeed,
  comment,
  kwFn,
  indent,
  dedent,
  endOfFile,
}

class Token {}
