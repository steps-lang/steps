
Feature: Running the lexer

	I can run the lexer stand-alone, independently from all
	other compiler components. It returns the correct list of
	tokens for all given inputs.

	Scenario Outline: Scan valid input and return a list of tokens
		Given the following input: <source_str>
		When the `tokenize` function is run
		Then the token kinds returned by `tokenize` are <token_kinds>
		
		Examples:
		| source_str           | token_kinds                                            |
        	| if x                 | KW_IF IDENTIFIER                                       |
                | *		       | OP_MULTIPLY                                            |
		| (*)                  | OP_CIRCLED_MULTIPLY                                    |
            	| (x)                  | LEFT_PARENTHESIS IDENTIFIER RIGHT_PARENTHESIS          |
            	| (-x)                 | LEFT_PARENTHESIS OP_MINUS IDENTIFIER RIGHT_PARENTHESIS |
                | _dummy               | DUMMY_IDENTIFIER                                       |
                | _                    | DUMMY_IDENTIFIER                                       |
                | _1                   | DUMMY_IDENTIFIER                                       |
                | x_1                  | IDENTIFIER                                             |
                | x__1                 | ERR_IDENTIFIER                                         |
                | __1                  | ERR_IDENTIFIER                                         |
                | x_                   | ERR_IDENTIFIER                                         |

		

	Scenario: Scan a byte order mark (BOM)
		Given the input consisting only of a BOM character
		When the `tokenize` function is run
		Then the token kinds returned by `tokenize` are

	Scenario: Scan an empty file
		Given the empty input
		When the `tokenize` function is run
		Then the token kinds returned by `tokenize` are

