/// This module declares the regular expressions for each token type.
///

import "dart:math" as math;
import "token.dart" as token;

const String _magnitude = r"[kMGTP]";
const String _fractionalMagnitude = r"[munpfa]";
const List<String> _singleEscapeCharacter = [
  "b",
  "t",
  "n",
  "f",
  "r",
  "e",
  "\\",
  '"',
  "'",
  "`",
  "0",
];

String _singleCharacterEscape() =>
    ("(?:" + _singleEscapeCharacter.map(RegExp.escape).join("|") + ")");

List<String> _characterCodeVariants = [
  "#[0-9A-Fa-f]{2}",
  "#[0-9A-Fa-f]{4}",
  "#[0-9A-Fa-f]{6}",
  // see 'The Unicode(R) Standard Version 14.0 - Core Specification'
  //     section '4.8 Name'
  "[A-Za-z]((-| -|_)?[A-Za-z0-9]|( |- )[A-Za-z])*",
];

String _characterCode() => "(?:" + _characterCodeVariants.join("|") + ")";

List<String> _escapeSequenceVariants() => [
      _singleCharacterEscape(),
      RegExp.escape("{") + _characterCode() + RegExp.escape("}"),
    ];

// Escape sequence according to Ceylon 1.3 language specification.
String _escapeSequence() =>
    r"\\(?:" + _escapeSequenceVariants().join("|") + ")";

String _regularCharacter() =>
    "[^" + ["\\", "'"].map(RegExp.escape).join("") + "]";

String _stringCharacter() => "(?:[^\\\"\r\n]|" + _escapeSequence() + ")";

const String _digit = r"[0-9]";

const String _digits = "$_digit+(?:_$_digit)*";

/// Return a regular expression literal for a [base] n integer literal.
String _baseIntegerRegEx(int base) {
  int cpLowerA = 'a'.codeUnits[0];
  int cpLowerZ = 'z'.codeUnits[0];
  int cpUpperA = 'A'.codeUnits[0];

  assert(base > 0);
  assert(base < (cpLowerZ - cpLowerA) + 11);

  String numDigits =
      (base == 1) ? "0" : "0-" + math.min(base - 1, 9).toString();
  String lcDigits = (base <= 10)
      ? ""
      : (base == 11)
          ? "a"
          : "a-" + String.fromCharCode(cpLowerA + base - 11);
  String ucDigits = (base <= 10)
      ? ""
      : (base == 11)
          ? "A"
          : "A-" + String.fromCharCode(cpUpperA + base - 11);
  String bDigits = "[$numDigits$lcDigits$ucDigits]";

  return (base == 10)
      ? "(?:10r)?$bDigits+(?:_$bDigits)*$_magnitude?"
      : "${base}r$bDigits+(?:_$bDigits)*";
}

String? getRegexString(token.TokenKind kind) {
  switch (kind) {
    case token.TokenKind.characterLiteral:
      return "'(?:" + _regularCharacter() + "|" + _escapeSequence() + ")'";
    case token.TokenKind.stringLiteral:
      return "\"" + _stringCharacter() + "*\"";
    case token.TokenKind.verbatimStringLiteral:
      return "\"\"\"(?:[^\"]|\"[^\"]|\"\"[^\"])*\"\"\"";
    case token.TokenKind.integerLiteral:
      return [for (var base = 1; base < 33; ++base) _baseIntegerRegEx(base)]
          .join("|");
    case token.TokenKind.floatLiteral:
      const String _exponent = "[Ee][-+]?$_digit+";
      const String _normalFloatLiteral = "$_digits[.]$_digits"
          "(?:$_exponent|$_magnitude|$_fractionalMagnitude)?";
      const String _shortcutFloatLiteral = "$_digits$_fractionalMagnitude";
      return '$_normalFloatLiteral|$_shortcutFloatLiteral';
    case token.TokenKind.lowerIdentifier:
      return r'[a-z][A-Za-z0-9]*(_[A-Za-z0-9]+)*';
    case token.TokenKind.upperIdentifier:
      return r'[A-Z][A-Za-z0-9]*(_[A-Za-z0-9]+)*';
    case token.TokenKind.dummyIdentifier:
      return r'(_[A-Za-z0-9]+)+|_';
    case token.TokenKind.whiteSpace:
      return r"[ \t]+";
    case token.TokenKind.lineFeed:
      return r'\r|\n|\r\n';
    case token.TokenKind.comment:
      return r"#[^\r\n]*";
    case token.TokenKind.kwFn:
      return RegExp.escape("fn");
    case token.TokenKind.indent:
      return null;
    case token.TokenKind.dedent:
      return null;
    case token.TokenKind.endOfFile:
      return null;
  }
}
