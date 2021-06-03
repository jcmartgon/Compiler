import ply.lex as lex


##################################################
# Token specification
##################################################


# Dictionary for reserved words, with the key being the term itself and the value it's token
res_words = {
    'Program': 'PROGRAM',
    'main': 'MAIN',
    'vars': 'VARS',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'void': 'VOID',
    'func': 'FUNC',
    'return': 'RETURN',
    'print': 'PRINT',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'do': 'DO',
    'while': 'WHILE',
    'from': 'FROM',
    'to': 'TO',
    'line': 'LINE',
    'dot': 'DOT',
    'circle': 'CIRCLE',
    'arc': 'ARC',
    'penup': 'PENUP',
    'pendown': 'PENDOWN',
    'color': 'COLOR',
    'size': 'SIZE',
    'reset': 'RESET',
    'left': 'LEFT',
    'right': 'RIGHT',
}


# The full list of tokens, specified below
tokens = ['ID', 'SEMICOLON', 'COLON', 'COMMA', 'L_PAREN', 'R_PAREN', 'L_BRACKET', 'R_BRACKET',
          'L_SBRACKET', 'R_SBRACKET', 'ASSIGN', 'AND', 'OR', 'EQ', 'NE', 'LTE', 'GTE', 'LT', 'GT', 'ADD',
          'SUB', 'TIMES', 'DIVIDE', 'CT_INT', 'CT_FLOAT', 'CT_CHAR', 'CT_STRING'] + list(res_words.values())


##################################################
# Token specification with regex
##################################################


# Possibility of negative sign, followed by any amount of digits, followed by a dot, followed by any amount of digits
def t_CT_FLOAT(t):
    r'\-?[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t


# Possibility of negative sign, followed by any amount of digits
def t_CT_INT(t):
    r'\-?[0-9]+'
    t.value = int(t.value)
    return t


# At least one character between single quotes
def t_CT_CHAR(t):
    r'\'.\''
    return t


# Any amount of characters between double quotes
def t_CT_STRING(t):
    r'\".*\"'
    return t


# At lest a letter, followed by any amount of letters and numbers
def t_ID(t):
    r'[A-Za-z][A-Za-z_0-9]*'
    t.type = res_words.get(t.value, 'ID')
    return t


# Self-defining rules
t_SEMICOLON = r'\;'
t_COLON = r'\:'
t_COMMA = r'\,'
t_L_PAREN = r'\('
t_R_PAREN = r'\)'
t_L_BRACKET = r'\{'
t_R_BRACKET = r'\}'
t_L_SBRACKET = r'\['
t_R_SBRACKET = r'\]'
t_ASSIGN = r'\='
t_AND = r'\&'
t_OR = r'\|'
t_EQ = r'\=\='
t_NE = r'\!\='
t_LTE = r'\<='
t_GTE = r'\>='
t_LT = r'\<'
t_GT = r'\>'
t_ADD = r'\+'
t_SUB = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'

t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Initialize the lexer
lexer = lex.lex()


##################################################
# TESTING - uncomment the lines below, up to the references section
##################################################


# testFile = open("testProvided.txt", "r")

# lexer.input(testFile.read())

# while True:
#     tok = lexer.token()
#     if not tok:
#         break;
#     print(tok)


##################################################
# References
##################################################

# PLY documentation: https://www.dabeaz.com/ply/ply.html#ply_nn3

