import ply.yacc as yacc
from lexer import tokens
import functions
import quadruples
from semantics import sem_cube as sc, types as st, operators as so
import memory
import constants
from virtual_machine import VirtualMachine


##################################################
# Variable declaration
##################################################


avail = memory.MainMemory()  # Memory counters to be used during compilation


quad_manager = quadruples.QuadMan()  # Quadruple manager class


func_dir = functions.FuncDir()  # Functions directory


const_tab = constants.ConstTab()  # Constants table


operators_stack = []  # Stack to keep track of the operators present during compilation


operands_stack = []  # Stack to keep track of the operands present during compilation


types_stack = []  # Stack to keep track of the types present during compilation


funcs_stack = []  # Stack to simulate the concept of scopes


vars_stack = []  # Stack to keep track of variables during multiple variables declarations


jumps_stack = []  # Stack to keep track of pending jump spaces in non-linear quadruples


aux_stack = []  # Stack to keep track of parameters during function calls


counter_stack = []  # Stack to keep track of how many parameters have been passed on a function call


##################################################
# Auxiliary functions
##################################################


# Adds a function to the stack, and the directory
def add_func(id):
    funcs_stack.append(id)
    func_dir.add_func(id)
    func_dir.get_func(id).set_ret_type(types_stack[-1])


# Checks if a given function has already been declared, to prevent redundancy
def check_func(func):
    if func_dir.has(func):
        print("ERROR: function: '", func, "' had already been declared")
        raise RuntimeError


# Checks if a given variable has already been declared on the current scope, to prevent redundancy
def check_var(id):
    if func_dir.get_func(funcs_stack[-1]).has_var(id):
        print("ERROR: variable identifier: '", id, "' was already in use")
        raise RuntimeError


# If a given constant hasn't been added to the table, it adds it, regardless, it returns it's address on memory
def check_const(val, type):
    if not const_tab.has(val):
        ref = avail.const_mem.assign_ref(type)
        const_tab.add_const(val, ref)
    return const_tab.get_const(val).get_ref()


# Returns the deepest scope in which a variable exist, if it doesn't exist, returns false
def var_context(id):
    if func_dir.get_func(funcs_stack[-1]).has_var(id):
        return funcs_stack[-1]
    elif func_dir.get_func('main').has_var(id):
        return 'main'
    else:
        return False


# Removes a function and its type from the corresponding stacks
def pop_func():
    funcs_stack.pop()
    types_stack.pop()


# Returns the next available address on memory for the given type on the current scope
def request_var_ref(type):
    if funcs_stack[-1] != 'main':
        return avail.local_mem.assign_ref(type)
    return avail.global_mem.assign_ref(type)


# Returns the next available address on memory for the given type on the previous scope, used during function calls
def request_var_ref_call(type):
    if funcs_stack[-2] != 'main':
        return avail.local_mem.assign_ref(type)
    return avail.global_mem.assign_ref(type)


# Returns the next available address on memory for a constant of the given type
def request_const_ref(type):
    return avail.const_mem.assign_ref(type)


# Generates the object code to be run by the virtual machine
def compile():
    obj = open("./obj.txt", "w")  # Opens/creates the file
    for func in func_dir.get_func_dir():  # Adds the relevant information from the functions directory
        obj.write("%s;%s;%s;%s;%s;%s;%s;%s\n" % (func, func_dir.get_func(func).get_ret_type(),
                                                 func_dir.get_func(func).get_signature(),
                                                 func_dir.get_func(func).get_first_quad(),
                                                 func_dir.get_func(func).get_ints_used(),
                                                 func_dir.get_func(func).get_floats_used(),
                                                 func_dir.get_func(func).get_chars_used(),
                                                 func_dir.get_func(func).get_bools_used())
                  )
    obj.write('$\n')  # Section delimiter
    for const in const_tab.get_const_tab():  # Adds the addresses and values of constants from the table
        obj.write("%s;%s\n" % (const, const_tab.get_const(const).get_ref()))
    obj.write('$\n')  # Section delimiter
    for quad in quad_manager.get_quads():  # Adds all the quadruples in order
        obj.write("%s;%s;%s;%s\n" % (quad.get_operator(), quad.get_first_operand(), quad.get_second_operand(), quad.get_res()))
    obj.write('#')  # File delimiter


# Checks if the given function has already had a quadruple assigned as their first
def check_func_quad():
    if funcs_stack and func_dir.get_func(funcs_stack[-1]).get_first_quad() == -1 and funcs_stack[-1] != 'main':
        func_dir.get_func(funcs_stack[-1]).set_first_quad(quad_manager.size() - 1)


# Adds the quadruple for binary arithmetic operations in the format: operator; 1st operator; 2nd operator; result
def binary_ari_quad():
    operator = operators_stack.pop()
    sec_operand = operands_stack.pop()
    first_operand = operands_stack.pop()
    sec_type = types_stack.pop()
    first_type = types_stack.pop()
    ret_type = sc[first_type][operator][sec_type]
    if ret_type != -1:
        types_stack.append(ret_type)
        ref = request_var_ref(ret_type)
        quad_manager.add_quad(operator, first_operand, sec_operand, ref)
        check_func_quad()
        operands_stack.append(ref)
    else:
        print("ERROR: Type mismatch!")
        raise TypeError


# Adds the quadruple for the assign operations in the format: assign operator; to assign; ; assign to
def assign_quad():
    operator = operators_stack.pop()
    to_assign = operands_stack.pop()
    target = operands_stack.pop()
    to_assign_type = types_stack.pop()
    target_type = types_stack.pop()
    ret_type = sc[target_type][operator][to_assign_type]
    if ret_type != -1:
        quad_manager.add_quad(operator, to_assign, ' ', target)
        check_func_quad()
    else:
        print("ERROR: Type mismatch!")
        raise TypeError


# Same as the previous one but re-adds the operand to be used as iterator for the loop as well as its type
def assign_from_to_quad():
    operator = operators_stack.pop()
    to_assign = operands_stack.pop()
    target = operands_stack.pop()
    to_assign_type = types_stack.pop()
    target_type = types_stack.pop()
    ret_type = sc[target_type][operator][to_assign_type]
    if ret_type != -1:
        quad_manager.add_quad(operator, to_assign, ' ', target)
        check_func_quad()
        operands_stack.append(target)
        types_stack.append(target_type)
    else:
        print("ERROR: Type mismatch!")
        raise TypeError


# Adds the quadruple for the print operation in the format: print; ; ; element to print
def print_quad(to_print):
    quad_manager.add_quad(so['print'], ' ', ' ', to_print)
    check_func_quad()


# Adds the quadruple for the goto operation (without destination9 in the format: goto; ; ;
def goto_quad():
    quad_manager.add_quad(so['goto'], ' ', ' ', ' ')
    check_func_quad()
    jumps_stack.append(quad_manager.size() - 1)


# Same as the previous one but with a destination address in the format: goto; ; ; destionation address
def goto_target_quad(target):
    quad_manager.add_quad(so['goto'], ' ', ' ', target)
    check_func_quad()


# Adds the quadruple for the gotof operation (without destination) in the format: gotof; ; ;
def gotof_quad():
    quad_manager.add_quad(so['gotof'], operands_stack.pop(), ' ', ' ')
    check_func_quad()
    jumps_stack.append(quad_manager.size() - 1)


# Adds the quadruple for the endfunc operation in the format: endfunc; ; ;
def end_func_quad():
    quad_manager.add_quad(so['endfunc'], ' ', ' ', ' ')
    check_func_quad()


# Adds the quadruple for the era operation in the format: era; return type ; ; name of the function
def era_quad(func):
    quad_manager.add_quad(so['era'], func_dir.get_func(func).get_ret_type(), ' ', func)
    check_func_quad()


# Adds the quadruple for the param operation in the format: param; argument's address; ; number of the argument
def param_quad(arg, num):
    quad_manager.add_quad(so['param'], arg, ' ', num)
    check_func_quad()


# Adds the quadruple for the gosub operation in the format: gosub; ; ; name of the fucntion
def gosub_quad(func):
    quad_manager.add_quad(so['gosub'], ' ', ' ', func)
    check_func_quad()


# Adds the quadruple for the return operation in the format: return; global address; ; local address
def return_quad(glob, loc):
    quad_manager.add_quad(so['return'], glob, ' ', loc)
    check_func_quad()


# Adds the quadruple for the endprog operation in the format: endprog; ; ;
def end_prog_quad():
    quad_manager.add_quad(so['endprog'], ' ', ' ', ' ')


def line_quad(length):
    if not types_stack.pop() == st['int']:
        print("ERROR: Type mismatch! A line can only be of an integer length")
        raise TypeError
    quad_manager.add_quad(so['line'], ' ', ' ', length)


def dot_quad(diameter):
    if not types_stack.pop() == st['int']:
        print("ERROR: Type mismatch! A dot can only have an integer as a diameter")
        raise TypeError
    quad_manager.add_quad(so['dot'], ' ', ' ', diameter)


def circle_quad(radius):
    if not types_stack.pop() == st['int']:
        print("ERROR: Type mismatch! A circle can only have an integer as a radius")
        raise TypeError
    quad_manager.add_quad(so['circle'], ' ', ' ', radius)


def arc_quad(radius):
    if not types_stack.pop() == st['int']:
        print("ERROR: Type mismatch! An arc can only have an integer as a radius")
        raise TypeError
    quad_manager.add_quad(so['arc'], ' ', ' ', radius)


def penup_quad():
    quad_manager.add_quad(so['penup'], ' ', ' ', ' ')


def pendown_quad():
    quad_manager.add_quad(so['pendown'], ' ', ' ', ' ')


def color_quad(color):
    quad_manager.add_quad(so['color'], ' ', ' ', color)


def size_quad(size):
    if not types_stack.pop() == st['int']:
        print("ERROR: Type mismatch! Pen size can only be of type integer")
        raise TypeError
    quad_manager.add_quad(so['size'], ' ', ' ', size)


def reset_quad():
    quad_manager.add_quad(so['reset'], ' ', ' ', ' ')


def left_quad(length):
    if not types_stack.pop() == st['int']:
        print("ERROR: Type mismatch! The length to move can only be of type integer")
        raise TypeError
    quad_manager.add_quad(so['left'], ' ', ' ', length)


def right_quad(length):
    if not types_stack.pop() == st['int']:
        print("ERROR: Type mismatch! The length to move can only be of type integer")
        raise TypeError
    quad_manager.add_quad(so['right'], ' ', ' ', length)


##################################################
# Grammar definition
##################################################


# General structure of a program
def p_program(p):
    'program : program_decl vars_decl_space funcs_decl_space main'
    end_prog_quad()
    # func_dir.print_dir()  # TESTING
    # const_tab.print_tab()  # TESTING
    # quad_manager.print_quads()  # TESTING


# Adds the goto main quadruple and adds the main function to the stack and the directory
def p_program_decl(p):
    'program_decl : PROGRAM ID SEMICOLON'
    types_stack.append("PN")
    add_func("main")
    goto_quad()


# Layout for the variables declaration space
def p_vars_decl_space(p):
    '''
    vars_decl_space : VARS vars_decl vars_decl_list
           | empty
    '''
    pass


# After the declaration for the given type is over, the temporal data related to it is removed
def p_vars_decl(p):
    'vars_decl : var_decl vars_list COLON type SEMICOLON'
    var_type = types_stack.pop()
    for var in vars_stack:
        ref = request_var_ref(var_type)
        func_dir.get_func(funcs_stack[-1]).add_var(var, var_type, ref)
    vars_stack.clear()


# If the var doesn't exist in the current scope or the previous one, adds the variable to the stack, otherwise error
def p_var_decl(p):
    'var_decl : ID var_dim'
    check_var(p[1])
    vars_stack.append(p[1])


# TODO: Arrays and standalone variables allowed
def p_var_dim(p):
    '''
    var_dim : L_SBRACKET CT_INT R_SBRACKET
           | empty
    '''
    pass


# Multiple variables of the same type
def p_vars_list(p):
    '''
    vars_list : COMMA var_decl vars_list
           | empty
    '''
    pass


# dds the type to the stack, to keep track of it
def p_type(p):
    '''
    type : INT
         | FLOAT
         | CHAR
    '''
    types_stack.append(st[p[1]])


# Multiple declarations of different types allowed
def p_vars_decl_list(p):
    '''
    vars_decl_list : vars_decl vars_decl_list
           | empty
    '''
    pass


# Layout for the functions declaration space
def p_funcs_decl_space(p):
    '''
    funcs_decl_space : func_decl funcs_decl_space
           | empty
    '''
    pass


# After the declaration for the function is over, the temporal data related to it is removed
def p_func_decl(p):
    'func_decl : func_header vars_decl_space func_body'
    funcs_stack.pop()
    end_func_quad()
    avail.reset_local_memory()


# Layour of the header of a function declaration
def p_func_header(p):
    'func_header : func_init L_PAREN params_decl R_PAREN SEMICOLON'
    pass


# If the fucntion hasn't been declared it adds it, otherwise throws an error
def p_func_init(p):
    'func_init : ret_type FUNC ID'
    check_func(p[3])
    add_func(p[3])


# INT | FLOAT | CHAR
def p_ret_type(p):
    'ret_type : type'
    pass


# VOID | Adds the type to the stack, to keep track of it
def p_ret_void(p):
    'ret_type : VOID'
    types_stack.append(p[1])


# Layour for the parameters of a function to be declared
def p_params_decl(p):
    '''
    params_decl : param_decl
           | empty
    '''
    pass


# At least a parameter is being declared
def p_param_decl(p):
    'param_decl : param params_list'
    pass


# If the variable doesnt exist in the scope, it adds it, otherwise throws an error
def p_param(p):
    'param : ID COLON type'
    check_var(p[1])
    ref = request_var_ref(types_stack[-1])
    func_dir.get_func(funcs_stack[-1]).add_var(p[1], types_stack[-1], ref)
    func_dir.get_func(funcs_stack[-1]).add_param(types_stack[-1])
    types_stack.pop()


# Multiple parameters or none
def p_params_list(p):
    '''
    params_list : COMMA param_decl
            | empty
    '''
    pass


# Layour for the body of a function
def p_func_body(p):
    'func_body : L_BRACKET stmnt R_BRACKET'
    pass


# The statements allowed
def p_stmnt(p):
    '''
    stmnt : return SEMICOLON
        | assignment SEMICOLON stmnt
        | print SEMICOLON stmnt
        | decision SEMICOLON stmnt
        | loop SEMICOLON stmnt
        | call SEMICOLON stmnt
        | graphics SEMICOLON stmnt
        | empty
    '''
    pass


# An assignment
def p_assignment(p):
    'assignment : assignee ASSIGN hyper_exp'
    operators_stack.append(so['='])
    assign_quad()


# Layout of the assignee
def p_assignee(p):
    'assignee : ID atom_id var_dim'
    pass


# Logical expression
def p_hyper_exp(p):
    'hyper_exp : super_exp logic exp_over'
    pass


# Relational expression
def p_super_exp(p):
    'super_exp : exp relation'
    pass


# Arithmetic expression
def p_exp(p):
    'exp : term add_sub'
    pass


# Multiplication or division
def p_term(p):
    'term : factor times_divide'
    pass


# L_PAREN hyper_exp R_PAREN | atom
def p_factor(p):
    '''
    factor : false_buttom hyper_exp pop_false_buttom
        | atom
    '''
    pass


# Adds the left parenthesis to the operator's stack as a priority delimiter
def p_false_buttom(p):
    'false_buttom : L_PAREN'
    operators_stack.append('(')


# Removes the left parenthesis from the operator's stack
def p_pop_false_buttom(p):
    'pop_false_buttom : R_PAREN'
    operators_stack.pop()


# The end of the expression has been reached, if there's still operations to be resolved, it resolves them
def p_exp_over(p):
    'exp_over : '
    while len(operators_stack) > 0 and operators_stack[-1] != '(':
        binary_ari_quad()


# The atomic elements in the expressions
def p_atom(p):
    '''
    atom : ID atom_id
        | CT_INT atom_ct_int
        | CT_FLOAT atom_ct_float
        | CT_CHAR atom_ct_char
        | call
    '''
    pass


# If an ID is read and has been declared, it gets added to the stacks
def p_atom_id(p):
    'atom_id : '
    context = var_context(p[-1])
    if context:
        operands_stack.append(func_dir.get_func(context).get_var_tab().get_var(p[-1]).get_ref())
        types_stack.append(func_dir.get_func(context).get_var_tab().get_var(p[-1]).get_type())
    else:
        print("ERROR: variable identifier: '", p[-1], "' hasn't been declared within this scope")
        raise NameError


# The int constant gets added to the stacks
def p_atom_ct_int(p):
    'atom_ct_int : '
    types_stack.append(st['int'])
    ref = check_const(p[-1], types_stack[-1])
    operands_stack.append(ref)


# The float constant gets added to the stacks
def p_atom_ct_float(p):
    'atom_ct_float : '
    types_stack.append(st['float'])
    ref = check_const(p[-1], types_stack[-1])
    operands_stack.append(ref)


# The char constat gets added to the stacks
def p_atom_ct_char(p):
    'atom_ct_char : '
    types_stack.append(st['char'])
    ref = check_const(p[-1], types_stack[-1])
    operands_stack.append(ref)


# Either a multiplacation, a division or nothing
def p_times_divide(p):
    '''
    times_divide : times_divide_op term
        | empty
    '''
    pass


# If the current opreator at the top of the stack is a multiplication or a division, it solves it and adds the new one
def p_times_divide_op(p):
    '''
    times_divide_op : TIMES
        | DIVIDE
    '''
    if len(operators_stack) > 0 and (operators_stack[-1] == 2 or operators_stack[-1] == 3):
        binary_ari_quad()
    operators_stack.append(so[p[1]])


# An addition, a substracion or nothing
def p_add_sub(p):
    '''
    add_sub : add_sub_op exp
        | empty
    '''
    pass


# Solves any pending operation of higher precedence and adds the new one
def p_add_sub_op(p):
    '''
    add_sub_op : ADD
        | SUB
    '''
    while len(operators_stack) > 0 and (operators_stack[-1] == 2 or operators_stack[-1] == 3
                                        or operators_stack[-1] == 0 or operators_stack[-1] == 1):
        binary_ari_quad()
    operators_stack.append(so[p[1]])


# A relation or nothing
def p_relation(p):
    '''
    relation : rel_op exp
        | empty
    '''
    pass


# Solves any pending operation of higher precedence and adds the new one
def p_rel_op(p):
    '''
    rel_op : GTE
        | LTE
        | GT
        | LT
        | NE
        | EQ
    '''
    while len(operators_stack) > 0 and (operators_stack[-1] == 2 or operators_stack[-1] == 3
                                        or operators_stack[-1] == 0 or operators_stack[-1] == 1
                                        or operators_stack[-1] == 4 or operators_stack[-1] == 5
                                        or operators_stack[-1] == 6 or operators_stack[-1] == 7):
        binary_ari_quad()
    operators_stack.append(so[p[1]])


# A logical expresion
def p_logic(p):
    '''
    logic : log_op super_exp
        | empty
    '''
    pass


# Solves any pending operation of higher precedence and adds the new one
def p_log_op(p):
    '''
    log_op : AND
        | OR
    '''
    while len(operators_stack) > 0 and (operators_stack[-1] == 2 or operators_stack[-1] == 3
                                        or operators_stack[-1] == 0 or operators_stack[-1] == 1
                                        or operators_stack[-1] == 4 or operators_stack[-1] == 5
                                        or operators_stack[-1] == 6 or operators_stack[-1] == 7
                                        or operators_stack[-1] == 8 or operators_stack[-1] == 9):
        binary_ari_quad()
    operators_stack.append(so[p[1]])


# After the call has been made, adds the gosub quadruple and the corresponding variable on the previous scope
def p_call(p):
    'call : call_starts L_PAREN args R_PAREN'
    if len(aux_stack) > 0:
        print("ERROR: Arguments missing on the declaration for function: ", funcs_stack[-1])
        raise RuntimeError
    funcs_stack.pop()
    counter_stack.clear()
    gosub_quad(funcs_stack[-1])
    if func_dir.get_func(funcs_stack[-1]).get_ret_type() != 'void':
        ref = request_var_ref_call(func_dir.get_func(funcs_stack[-1]).get_ret_type())
        operators_stack.append(so['='])
        operands_stack.append(ref)
        operands_stack.append(func_dir.get_func('main').get_var(funcs_stack[-1]).get_ref())
        types_stack.append(func_dir.get_func(funcs_stack[-1]).get_ret_type())
        types_stack.append(func_dir.get_func(funcs_stack[-1]).get_ret_type())
        assign_quad()
        operands_stack.append(ref)
        types_stack.append(func_dir.get_func(funcs_stack[-1]).get_ret_type())
        funcs_stack.pop()


# Adds the era quadruple, simulates loading the new scope and prepares to add parameters
def p_call_starts(p):
    'call_starts : ID'
    if not func_dir.has(p[1]):
        print("ERROR: function '", p[1], "' has not been declared")
        raise NameError
    era_quad(p[1])
    funcs_stack.append(p[1])
    aux_stack.extend(func_dir.get_func(funcs_stack[-1]).get_signature())
    funcs_stack.append(funcs_stack[-2])


# Several arguments or none
def p_args(p):
    '''
    args : arg
        | empty
    '''
    pass


# At least one argument
def p_arg(p):
    'arg : hyper_exp param_quad arg_list'
    pass


# After an argument has been passed, checks if it's valid, if so, adds the parameter quadruple
def p_param_quad(p):
    'param_quad : '
    if not aux_stack:
        print("ERROR: Too many arguments on function: ", funcs_stack[-1])
        raise RuntimeError
    if types_stack.pop() != aux_stack[0]:
        print("ERROR: Type mismatch on argument: ", operands_stack[-1])
        raise TypeError
    param_quad(operands_stack.pop(), len(counter_stack))
    counter_stack.append(0)
    del aux_stack[0]


# Either more arguments or none
def p_arg_list(p):
    '''
    arg_list : COMMA arg
        | empty
    '''
    pass


# If the return statement is a valid one, if so, adds the return quadruple and the global variable for the function
def p_return(p):
    'return : RETURN L_PAREN hyper_exp R_PAREN'
    if func_dir.get_func(funcs_stack[-1]).get_ret_type() != types_stack[-1]:
        print("ERROR: return type of function ", funcs_stack[-1], ' doesnt match the type of the return statement')
        raise TypeError
    if not func_dir.get_func('main').has_var(funcs_stack[-1]):
        ref = avail.global_mem.assign_ref(types_stack[-1])
        func_dir.get_func('main').add_var(funcs_stack[-1], types_stack.pop(), ref)
    return_quad(func_dir.get_func('main').get_var_tab().get_var(funcs_stack[-1]).get_ref(), operands_stack.pop())


# Layout for the print statement
def p_print(p):
    'print : PRINT L_PAREN to_print R_PAREN'
    pass


# Either an expression or a string
def p_to_print(p):
    '''
    to_print : hyper_exp print_exp printing_list
              | CT_STRING print_str printing_list
    '''
    pass


# Adds the print quadruple for the expression
def p_print_exp(p):
    'print_exp : '
    print_quad(operands_stack.pop())
    types_stack.pop()


# Adds the print quadruple for the string
def p_print_str(p):
    'print_str : '
    print_quad(p[-1])


# More or none elements to print
def p_printing_list(p):
    '''
    printing_list : COMMA to_print
              | empty
    '''
    pass


# Layout for the if statement
def p_decision(p):
    'decision : IF L_PAREN hyper_exp cond R_PAREN THEN L_BRACKET stmnt R_BRACKET else_block if_over'
    pass


# If the condition presented is of type bool, adds the gotof quadruple, otherwise throws an error
def p_cond(p):
    'cond : '
    if types_stack.pop() != st['bool']:
        print("ERROR: Type mismatch!")
        raise TypeError
    gotof_quad()


# Layout for the else block for the if statement
def p_else_block(p):
    '''
    else_block : ELSE else_starts L_BRACKET stmnt R_BRACKET
            | empty
    '''
    pass


# Adds the goto quadruple and fills the previously presented gotof quadruple
def p_else_starts(p):
    'else_starts : '
    false = jumps_stack.pop()
    goto_quad()
    quad_manager.fill(false, quad_manager.size())


# Fills the previously presented goto quadruple
def p_if_over(p):
    'if_over : '
    quad_manager.fill(jumps_stack.pop(), quad_manager.size())


# Either a conditional loop or a non-conditional
def p_loop(p):
    '''
    loop : conditional
       | non_conditional
    '''
    pass


# Layout for the while-do statement
def p_conditional(p):
    'conditional : WHILE L_PAREN while_starts hyper_exp cond R_PAREN DO L_BRACKET stmnt R_BRACKET while_do_over'
    pass


# Adds the quadruple to return to, to check the condition
def p_while_starts(p):
    'while_starts : '
    jumps_stack.append(quad_manager.size())


# Adds the goto quadruple to go back to the beginning of the statement and fills the pending gotof quadruple
def p_while_do_over(p):
    'while_do_over : '
    false = jumps_stack.pop()
    ret = jumps_stack.pop()
    goto_target_quad(ret)
    quad_manager.fill(false, quad_manager.size())


# Layout for the from-to statement
def p_non_conditional(p):
    'non_conditional : FROM from_to_assignment TO from_to_limit from_to_cond DO L_BRACKET stmnt R_BRACKET from_to_over'
    pass


# Adds the assign_from_to quadruple
def p_from_to_assignment(p):
    'from_to_assignment : assignee ASSIGN hyper_exp'
    if types_stack[-1] != st['int']:
        print("ERROR: Type mismatch!")
        raise TypeError
    operators_stack.append(so['='])
    assign_from_to_quad()


# Adds the less than or equeal operator and re-adds the iterator to be operated on later on the statement
def p_from_to_limit(p):
    'from_to_limit : hyper_exp'
    if types_stack[-1] != st['int']:
        print("ERROR: Type mismatch!")
        raise TypeError
    to_increment = operands_stack[-2]
    type_to_increment = types_stack[-2]
    operators_stack.append(so['<='])
    binary_ari_quad()
    operands_stack.append(to_increment)
    types_stack.append(type_to_increment)
    jumps_stack.append(quad_manager.size() - 1)


# If the condition is valid, adds the gotof quadruple and re-adds the iterator twice, to be operated later
def p_from_to_cond(p):
    'from_to_cond : '
    to_increment = operands_stack.pop()
    type_to_increment = types_stack.pop()
    if types_stack.pop() != st['bool']:
        print("ERROR: Type mismatch!")
        raise TypeError
    gotof_quad()
    operands_stack.append(to_increment)
    types_stack.append(type_to_increment)
    operands_stack.append(to_increment)
    types_stack.append(type_to_increment)

# Adds the quadruples to add 1 to the iterator, the goto quadruple to the start of the statement and fills the gotof
def p_from_to_over(p):
    'from_to_over : '
    operators_stack.append(so['+'])
    types_stack.append(st['int'])
    ref = check_const(1, types_stack[-1])
    operands_stack.append(ref)
    binary_ari_quad()
    operators_stack.append(so['='])
    assign_quad()
    false = jumps_stack.pop()
    ret = jumps_stack.pop()
    goto_target_quad(ret)
    quad_manager.fill(false, quad_manager.size())


# Graphical statements
def p_graphics(p):
    '''
    graphics : line
        | dot
        | circle
        | arc
        | penup
        | pendown
        | color
        | size
        | reset
        | left
        | right
    '''
    pass


def p_line(p):
    'line : LINE L_PAREN exp R_PAREN'
    line_quad(operands_stack.pop())


def p_dot(p):
    'dot : DOT L_PAREN exp R_PAREN'
    dot_quad(operands_stack.pop())


def p_circle(p):
    'circle : CIRCLE L_PAREN exp R_PAREN'
    circle_quad(operands_stack.pop())


def p_arc(p):
    'arc : ARC L_PAREN exp R_PAREN'
    arc_quad(operands_stack.pop())


def p_penup(p):
    'penup : PENUP L_PAREN R_PAREN'
    penup_quad()


def p_pendown(p):
    'pendown : PENDOWN L_PAREN R_PAREN'
    pendown_quad()


def p_color(p):
    'color : COLOR L_PAREN CT_STRING R_PAREN'
    color_quad(p[3])


def p_size(p):
    'size : SIZE L_PAREN exp R_PAREN'
    size_quad(operands_stack.pop())


def p_reset(p):
    'reset : RESET L_PAREN R_PAREN'
    reset_quad()


def p_left(p):
    'left : LEFT L_PAREN exp R_PAREN'
    left_quad(operands_stack.pop())


def p_right(p):
    'right : RIGHT L_PAREN exp R_PAREN'
    right_quad(operands_stack.pop())


# Layout for the main program
def p_main(p):
    'main : main_init func_body'
    pop_func()


# Adds the main function and fills the pending goto quadrple
def p_main_init(p):
    'main_init : MAIN L_PAREN R_PAREN'
    types_stack.append('void')
    main = jumps_stack.pop()
    quad_manager.fill(main, quad_manager.size())
    func_dir.get_func('main').set_first_quad(quad_manager.size())


def p_empty(p):
    'empty :'
    pass


# # Error rule for syntax errors
def p_error(p):
    if p != None:
        print(f"Syntax error on line:  {p.lexer.lineno}")
    else:
        print(p)
        print("Syntax error")
        return
    parser.restart()


# Initialize parser
parser = yacc.yacc()
parser.defaulted_states = {}


##################################################
# TESTING
##################################################


# source_code = open("testGraphics.txt")
# source_code = open("testFactorialIterative.txt")
# source_code = open("testFactorialRecursive.txt")
# source_code = open("testFibonacciIterative.txt")
# source_code = open("testFibonacciRecursive.txt")



##################################################
# COMPILE AND EXECUTE
##################################################


print('Type the name of the source code file (including file extension): ')


file = input()


source_code = open(file)


parser.parse(source_code.read())


compile()


virtual_machine = VirtualMachine()


virtual_machine.run()



##################################################
# References
##################################################


# PLY documentation: https://www.dabeaz.com/ply/ply.html#ply_nn3
