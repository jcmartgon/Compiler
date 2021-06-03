##################################################
# Variable-related classes
##################################################


# Variable class
class Var:

    # Initializes an instance of the variable with var_type as its type
    def __init__(self, var_type, var_ref):
        self.type = var_type
        self.ref = var_ref  # Address in memory

    # Returns the variable's type
    def get_type(self):
        return self.type

    # Sets the variable's type to the given value
    def set_type(self, var_type):
        self.type = var_type

    # Returns the memory address of the variable
    def get_ref(self):
        return self.ref

    # Sets the memory address to the given value
    def set_ref(self, var_ref):
        self.ref = var_ref


# Variables table class
class VarTab:

    # Constructor method
    def __init__(self):
        self.table = {}

    # Returns the requested variable from the table
    def get_var(self, var_id):
        return self.table[var_id]

    # Adds the given variable to the table
    def add_var(self, var_id, var_type, var_ref):
        self.table[var_id] = Var(var_type, var_ref)

    # Sets the given variable's type to the given value
    def set_var_type(self, var_id, var_type):
        self.table[var_id].set_type(var_type)

    # Checks if the given variable is already in the table
    def has(self, key):
        return key in self.table

    # For testing purposes, prints the variable table
    def print_tab(self):
        for var in self.table:
            print("Variable ", var, " is of type: ", self.table[var].get_type(), ", and has reference: ",
                  self.table[var].get_ref(), "\n")
