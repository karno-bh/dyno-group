from enum import Enum


class TokenType(Enum):
    # Single char tokens
    LEFT_PAREN = 0
    RIGHT_PAREN = 10
    LEFT_BRACE = 20
    RIGHT_BRACE = 30
    COMMA = 40
    DOT = 50
    MINUS = 60
    PLUS = 70
    SEMICOLON = 80
    SLASH = 90
    STAR = 100
    PERCENT = 110
    GREATER = 120
    LESS = 130

    # Two char tokens
    EXCLAMATION_EQ = 140
    LESS_MORE = 150
    LESS_EQ = 160
    MORE_EQ = 170

    # Keywords
    AND = 180
    OR = 190
    NOT = 200
    LIKE = 210

    # Identifiers
    IDENTIFIER = 220
    STRING = 230
    NUMBER = 240


class Scanner:

    def __init__(self) -> None:
        super().__init__()


