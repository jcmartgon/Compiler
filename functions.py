import variables
from semantics import types as st


##################################################
# Function-related classes
##################################################


# Functions class
class Func:

    # Constructor method
    def __init__(self, ret_type = None):
        self.signature = []  # The parameters' types in order
        self.ret_type = 0  # The function's return type
        self.var_tab = variables.VarTab()  # The function's variable table
        self.first_quad = -1  # The first quadruple, initialized as -1, later to me modified during compilation
        self.ints_used = 0  # Amount of ints required for it, defined during compilation
        self.floats_used = 0  # Amount of floats required for it, defined during compilation
        self.chars_used = 0  # Amount of chars required for it, defined during compilation
        self.bools_used = 0  # Amount of bools required for it, defined during compilation

    # To be used during compilation, adds the type of the parameter being defined to the signature of the function
    def add_param(self, param_type):
        self.signature.append(param_type)

    # Returns the function's signature
    def get_signature(self):
        return self.signature

    # Sets the function's signature to the received element
    def set_signature(self, signature):
        self.signature = signature

    # Returns the function's return type
    def get_ret_type(self):
        return self.ret_type

    # Sets the function's return type
    def set_ret_type(self, ret_type):
        self.ret_type = ret_type

    # Returns the function's variables table
    def get_var_tab(self):
        return self.var_tab

    # Checks if the given var is already in the function's variables table
    def has_var(self, key):
        return self.var_tab.has(key)

    # Returns the given variable from the functions variables table
    def get_var(self, var_id):
        return self.var_tab.get_var(var_id)

    # Adds the given variable into the function's variables table and modifies the type-specific counter
    def add_var(self, var_id, var_type, var_ref):
        self.var_tab.add_var(var_id, var_type, var_ref)
        if var_type == st['int']:
            self.ints_used += 1
        elif var_type == st['float']:
            self.floats_used += 1
        elif var_type == st['char']:
            self.chars_used += 1
        else:
            self.bools_used += 1

    # Returns the first quadruple
    def get_first_quad(self):
        return self.first_quad

    # Sets the first quadruple to the given one
    def set_first_quad(self, quad):
        self.first_quad = quad

    # Returns the amount of ints required by the function
    def get_ints_used(self):
        return self.ints_used

    # Sets the amount of ints used by the function
    def set_ints_used(self, ints_used):
        self.ints_used = ints_used

    # Returns the amount of floats required by the function
    def get_floats_used(self):
        return self.floats_used

    # Sets the amount of floats required by the function
    def set_floats_used(self, floats_used):
        self.floats_used = floats_used

    # Returns the amount of chars required by the function
    def get_chars_used(self):
        return self.chars_used

    # Sets the amount of chars required by the function
    def set_chars_used(self, chars_used):
        self.chars_used = chars_used

    # Returns the amount of booleans required by the function
    def get_bools_used(self):
        return self.bools_used

    # Sets the amount of booleans required by the function
    def set_bools_used(self, bools_used):
        self.bools_used = bools_used


# Functions directory class
class FuncDir:

    # Constructor method
    def __init__(self):
        self.dir = {}  # Initialized as an empty directory

    # Returns the functions' directory
    def get_func_dir(self):
        return self.dir

    # Checks to see if the given function is already in the functions' directory
    def has(self, key):
        return key in self.dir

    # Returns the function based on its id
    def get_func(self, func_id):
        return self.dir[func_id]

    # Adds a function to the functions' directory
    def add_func(self, func_id):
        self.dir[func_id] = Func()

    # For testing purposes, prints the function directory and all its elements, including its variable table
    def print_dir(self):
        for func in self.dir:
            print("Function ", func, " has the following signature: ", self.dir[func].get_signature(),
                  ", return type: ", self.dir[func].get_ret_type(), " requires ", self.dir[func].get_ints_used(),
                  "ints, ", self.dir[func].get_floats_used(), " floats, ", self.dir[func].get_chars_used(), " chars, ",
                  self.dir[func].get_bools_used(), " booleans, and the following variables:")
            self.dir[func].get_var_tab().print_tab()
