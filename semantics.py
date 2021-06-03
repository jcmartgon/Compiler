##################################################
# Operators dictionary
##################################################


# A dictionary with the keys being the operators themselves and their values the semantic codes
operators = {
    '+': 0,
    '-': 1,
    '*': 2,
    '/': 3,
    '==': 4,
    '!=': 5,
    '<': 6,
    '<=': 7,
    '>': 8,
    '>=': 9,
    '&': 10,
    '|': 11,
    '=': 12,
    'print': 13,
    'goto': 14,
    'gotof': 15,
    'endfunc': 16,
    'era': 17,
    'param': 18,
    'gosub': 19,
    'return': 20,
    'read': 21,
    'endprog': 22,
    'line': 23,
    'dot': 24,
    'circle': 25,
    'arc': 26,
    'penup': 27,
    'pendown': 28,
    'color': 29,
    'size': 30,
    'reset': 31,
    'left': 32,
    'right': 33,
}


##################################################
# Supported types
##################################################


# A dictionary with the keys being the supported types and their values the semantic codes
types = {
    'int': 0,
    'float': 1,
    'char': 2,
    'bool': 3
}


##################################################
# Semantic cube initialization
##################################################


# Semantic cube, a 3-dimensional list, it's structure will be [firstOperandType][operator][secondOperandType]
sem_cube = []


# Creates the semantic cube, filling all fields with a -1 value, later to be modified
for type_0 in types:
    types_x = []
    for op in operators:
        ops_y = []
        for types_1 in types:
            ops_y.append(-1)
        types_x.append(ops_y)
    sem_cube.append(types_x)


##################################################
# Return type specification
##################################################


# The return types for some combinations will be defined below, but not all,the -1 value will only be modified if needed


# Setting the return types for [int][int] combinations
sem_cube[types['int']][operators['+']][types['int']] = types['int']
sem_cube[types['int']][operators['-']][types['int']] = types['int']
sem_cube[types['int']][operators['*']][types['int']] = types['int']
sem_cube[types['int']][operators['/']][types['int']] = types['int']
sem_cube[types['int']][operators['==']][types['int']] = types['bool']
sem_cube[types['int']][operators['!=']][types['int']] = types['bool']
sem_cube[types['int']][operators['<']][types['int']] = types['bool']
sem_cube[types['int']][operators['<=']][types['int']] = types['bool']
sem_cube[types['int']][operators['>']][types['int']] = types['bool']
sem_cube[types['int']][operators['>=']][types['int']] = types['bool']
sem_cube[types['int']][operators['&']][types['int']] = types['bool']
sem_cube[types['int']][operators['|']][types['int']] = types['bool']
sem_cube[types['int']][operators['=']][types['int']] = types['int']


# Setting the return types for [int][float] combinations
sem_cube[types['int']][operators['==']][types['float']] = types['bool']
sem_cube[types['int']][operators['!=']][types['float']] = types['bool']
sem_cube[types['int']][operators['<']][types['float']] = types['bool']
sem_cube[types['int']][operators['<=']][types['float']] = types['bool']
sem_cube[types['int']][operators['>']][types['float']] = types['bool']
sem_cube[types['int']][operators['>=']][types['float']] = types['bool']
sem_cube[types['int']][operators['&']][types['float']] = types['bool']
sem_cube[types['int']][operators['|']][types['float']] = types['bool']


# Setting the return types for [float][int] combinations
sem_cube[types['float']][operators['==']][types['int']] = types['bool']
sem_cube[types['float']][operators['!=']][types['int']] = types['bool']
sem_cube[types['float']][operators['<']][types['int']] = types['bool']
sem_cube[types['float']][operators['<=']][types['int']] = types['bool']
sem_cube[types['float']][operators['>']][types['int']] = types['bool']
sem_cube[types['float']][operators['>=']][types['int']] = types['bool']
sem_cube[types['float']][operators['&']][types['int']] = types['bool']
sem_cube[types['float']][operators['|']][types['int']] = types['bool']


# Setting the return types for [float][float] combinations
sem_cube[types['float']][operators['+']][types['float']] = types['float']
sem_cube[types['float']][operators['-']][types['float']] = types['float']
sem_cube[types['float']][operators['*']][types['float']] = types['float']
sem_cube[types['float']][operators['/']][types['float']] = types['float']
sem_cube[types['float']][operators['==']][types['float']] = types['bool']
sem_cube[types['float']][operators['!=']][types['float']] = types['bool']
sem_cube[types['float']][operators['<']][types['float']] = types['bool']
sem_cube[types['float']][operators['<=']][types['float']] = types['bool']
sem_cube[types['float']][operators['>']][types['float']] = types['bool']
sem_cube[types['float']][operators['>=']][types['float']] = types['bool']
sem_cube[types['float']][operators['&']][types['float']] = types['bool']
sem_cube[types['float']][operators['|']][types['float']] = types['bool']
sem_cube[types['float']][operators['=']][types['float']] = types['float']


# Setting the return types for [char][char] combinations
sem_cube[types['char']][operators['==']][types['char']] = types['bool']
sem_cube[types['char']][operators['!=']][types['char']] = types['bool']
sem_cube[types['char']][operators['<']][types['char']] = types['bool']
sem_cube[types['char']][operators['<=']][types['char']] = types['bool']
sem_cube[types['char']][operators['>']][types['char']] = types['bool']
sem_cube[types['char']][operators['>=']][types['char']] = types['bool']
sem_cube[types['char']][operators['=']][types['char']] = types['char']
