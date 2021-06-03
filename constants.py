##################################################
# Constant-related classes
##################################################


# Constant class
class Const:

    # Initializes an instance of the constant
    def __init__(self, ref):
        self.ref = ref

    # Returns the constant's address in memory
    def get_ref(self):
        return self.ref

    # Sets the constant's address in memory
    def set_ref(self, var_ref):
        self.ref = var_ref


# Constant table class
class ConstTab:

    # Constructor method
    def __init__(self):
        self.table = {}

    # Returns the constants table
    def get_const_tab(self):
        return self.table

    # Returns the requested constant from the table
    def get_const(self, value):
        return self.table[value]

    # Adds the given constant to the table
    def add_const(self, val, ref):
        self.table[val] = Const(ref)

    # Checks if the given constant is already in the table
    def has(self, val):
        return val in self.table

    # Prints the table's values
    def print_tab(self):
        for const in self.table:
            print("Constant ", const, " is on address: ", self.table[const].get_ref(), "\n")
