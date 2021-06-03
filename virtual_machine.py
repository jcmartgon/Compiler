import functions
import constants
import memory
from semantics import sem_cube as sc, types as st, operators as so
import turtle


# Receives a string representing a list and turns it into an actual list
def fix_list(str: str):
    to_remove = ['[', ']']
    for char in to_remove:
        str = str.replace(char, '')  # Removes the squared brackets from the string
    li = list(str.split(","))  # Creates a list from the string
    if li[0] == '':
        li.remove('')  # If the list has an empty space it gets removed
    li = list(map(int, li))  # Turns the list of chars into a list of ints
    return li


# Checks whether the given value can be cast to an int or not
def can_cast(to_check):
    try:
        int(to_check)
        return True
    except ValueError:
        return False


# Receives a string and turns it into a list representing an instruction
def fix_quad(str: str):
    li = list(str.split(";"))  # Splits the string by the element delimiter
    li[0] = int(li[0])  # Every quadruple starts with a semantic code, hence the first element can always be casted
    if not li[1] == ' ':  # If the second element is not a blank space, casts it to int
        li[1] = int(li[1])
    if not li[2] == ' ':  # If the third element is not a blank space, casts it to int
        li[2] = int(li[2])
    if can_cast(li[3]):  # If the third element can be casted to an int, casts it to int
        li[3] = int(li[3])
    return li


# Virtual machine class, will read the object code produced by the commpiler and perform every instruction in the
# proper order.
class VirtualMachine:

    def __init__(self):
        self.quad_dir = {}  # Directory with the instructions to perform, in order of appearance
        self.instruction_pointer = 0  # The current instruction being performed
        self.func_dir = functions.FuncDir()  # Functions directory created from the object code
        self.const_tab = constants.ConstTab()  # Constants table created from the object code
        self.memory = memory.MainMemory()  # Initializes the machine's memory
        self.param_dir = {}  # Directory to place the arguments of a function been called
        self.scope_int = [0]  # Stack to keep track of how many ints are currently in local memory
        self.scope_float = [0]  # Stack to keep track of how many floats are currently in local memory
        self.scope_char = [0]  # Stack to keep track of how many chars are currently in local memory
        self.scope_bool = [0]  # Stack to keep track of how many bools are currently in local memory
        self.back_pointer = []  # Stack to keep track of where the instruction_pointer was before a gosub
        self.ret_func = {}  # Directory to keep track of functions with a return type which have already showed up
        self.wn = turtle.Screen()
        self.wn.colormode(255)
        self.turtle = turtle.Turtle()
        screen_x, screen_y = self.wn.screensize()

    # Receives a line representing a function and adds the corresponding information to the directory
    def add_func(self, line):
        func = line.split(';')
        self.func_dir.add_func(func[0])
        self.func_dir.get_func(func[0]).set_ret_type(func[1])
        self.func_dir.get_func(func[0]).set_signature(fix_list(func[2]))
        self.func_dir.get_func(func[0]).set_first_quad(int(func[3]))
        self.func_dir.get_func(func[0]).set_ints_used(int(func[4]))
        self.func_dir.get_func(func[0]).set_floats_used(int(func[5]))
        self.func_dir.get_func(func[0]).set_chars_used(int(func[6]))
        self.func_dir.get_func(func[0]).set_bools_used(int(func[7]))

    # Receives a line representing a constant and adds it to memoryy
    def add_const(self, line):
        const = line.split(';')
        self.const_tab.add_const(const[0], const[1])  # TODO: NECESARIO?
        self.memory.const_mem.add_element(int(const[1]), const[0], self.scope_int[-1], self.scope_float[-1], self.scope_char[-1], self.scope_bool[-1])

    # Receives a line representing a quadruple and adds it to the directory
    def add_quad(self, line):
        quad = fix_quad(line)
        self.quad_dir[self.instruction_pointer] = quad

    # Reads the object file and restores the data on memory
    # Throughout this process, the instruction_pointer will be used temporarily, at the end it gets reset
    def restore_data(self):
        obj = open("obj.txt", "r")  # Object code file
        line = ''
        while line != '$':  # Reads the functions block
            line = next(obj).rstrip('\n')
            if line != '$':
                self.add_func(line)
        line = ''
        while line != '$':  # Reads the constants block
            line = next(obj).rstrip('\n')
            if line != '$':
                self.add_const(line)
        line = ''
        while line != '#':  # Reads the quadruples block
            line = next(obj).rstrip('\n')
            if line != '$' and line != '#':
                self.add_quad(line)
                self.instruction_pointer += 1
        self.instruction_pointer = 0  # End of File

    # Checks if there's enough room in memory for the function being called
    def request_memory(self, func):
        func = self.func_dir.get_func(func)
        if func == 'main':  # Only happens at the start of the program
            return self.memory.global_mem.check_space(func.ints_used, func.floats_used, func.chars_used, func.bools_used)
        else:  # Happens every call
            return self.memory.local_mem.check_space(func.ints_used, func.floats_used, func.chars_used, func.bools_used)

    # Returns the value of the address being requested
    def fetch_value(self, address):
        scope = self.memory.check_seg(address)
        if scope == 'int':  # The address is from a local int and the local-int offset is added
            return self.memory.fetch_value(address + self.scope_int[-1])
        elif scope == 'float':  # The address is from a local float and the offset is added
            return self.memory.fetch_value(address + self.scope_float[-1])
        elif scope == 'char':  # The address is from a local char and the offset is added
            return self.memory.fetch_value(address + self.scope_char[-1])
        elif scope == 'bool':  # The address is from a local bool and the offset is added
            return self.memory.fetch_value(address + self.scope_bool[-1])
        else:  # The address is either in the global or constant memory and no scope-specific offset is required
            return self.memory.fetch_value(address)

    # Adds the value to the address provided
    def add_value(self, address, value):
        self.memory.add_value(address, value, self.scope_int[-1], self.scope_float[-1], self.scope_char[-1], self.scope_bool[-1])

    # The instruction pointer starts at 0, from there, every instruction is performed accordingly
    def run_instructions(self):
        while self.quad_dir[self.instruction_pointer][0] != so['endprog']:  # While there are quadruples to read
            # print(self.quad_dir[self.instruction_pointer])  # Testing
            if not self.quad_dir[self.instruction_pointer][1] == ' ' \
                    and self.quad_dir[self.instruction_pointer][0] != so['era'] \
                    and self.quad_dir[self.instruction_pointer][0] != so['return']:
                first_operand = self.fetch_value(self.quad_dir[self.instruction_pointer][1])
            if not self.quad_dir[self.instruction_pointer][2] == ' ':
                second_operand = self.fetch_value(self.quad_dir[self.instruction_pointer][2])
            if self.quad_dir[self.instruction_pointer][0] == so['+']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand + second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['-']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand - second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['*']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand * second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['/']:
                if second_operand == 0:
                    print('ERROR: Cannot divide by 0')
                    raise ZeroDivisionError
                res = first_operand / second_operand
                if isinstance(first_operand, int) and isinstance(second_operand, int):
                    res = int(res)
                self.add_value(self.quad_dir[self.instruction_pointer][3], res)
            elif self.quad_dir[self.instruction_pointer][0] == so['==']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand == second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['!=']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand != second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['<']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand < second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['<=']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand <= second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['>']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand > second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['>=']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand >= second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['&']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand and second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['|']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand or second_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['=']:
                self.add_value(self.quad_dir[self.instruction_pointer][3], first_operand)
            elif self.quad_dir[self.instruction_pointer][0] == so['print']:
                to_print = self.quad_dir[self.instruction_pointer][3]
                if isinstance(to_print, int):  # An expression is being printed
                    print(self.fetch_value(to_print))
                else:  # A string is being printed
                    print(to_print.replace('"', ''))
            elif self.quad_dir[self.instruction_pointer][0] == so['goto']:
                self.instruction_pointer = self.quad_dir[self.instruction_pointer][3] - 1
            elif self.quad_dir[self.instruction_pointer][0] == so['gotof']:
                if not self.fetch_value(self.quad_dir[self.instruction_pointer][1]):  # If the condition is not met
                    self.instruction_pointer = self.quad_dir[self.instruction_pointer][3] - 1
            elif self.quad_dir[self.instruction_pointer][0] == so['era']:
                if not self.request_memory(self.quad_dir[self.instruction_pointer][3]):  # If there's not enough space
                    print('Stack Overflow')
                    raise MemoryError
                elif self.quad_dir[self.instruction_pointer][1] != 'void':  # If the function will return something
                    if not self.quad_dir[self.instruction_pointer][3] in self.ret_func:  # And it's its first call
                        self.memory.new_func(self.quad_dir[self.instruction_pointer][1])
                        self.ret_func[self.quad_dir[self.instruction_pointer][3]] = 1
            elif self.quad_dir[self.instruction_pointer][0] == so['param']:
                self.param_dir[self.quad_dir[self.instruction_pointer][3]] = \
                    self.fetch_value(self.quad_dir[self.instruction_pointer][1])  # Adds the parameter to the dictionary
            elif self.quad_dir[self.instruction_pointer][0] == so['gosub']:
                self.back_pointer.append(self.instruction_pointer)  # Stores the current quadruple, to continue later
                self.scope_int.append(self.memory.local_mem.int_size())  # Adds the current local ints
                self.scope_float.append(self.memory.local_mem.float_size())  # Adds the current local floats
                self.scope_char.append(self.memory.local_mem.char_size())  # Adds the current local chars
                self.scope_bool.append(self.memory.local_mem.bool_size()) # Adds the current local booleans
                for param in self.param_dir:  # Adds the parameters as variables to the new scope
                    if isinstance(self.param_dir[param], int):
                        self.memory.add_param(self.param_dir[param], st['int'], self.scope_int[-1], self.scope_float[-1], self.scope_char[-1], self.scope_bool[-1])
                    elif isinstance(self.param_dir[param], float):
                        self.memory.add_param(self.param_dir[param], st['float'], self.scope_int[-1], self.scope_float[-1], self.scope_char[-1], self.scope_bool[-1])
                    elif isinstance(self.param_dir[param], chr):
                        self.memory.add_param(self.param_dir[param], st['char'], self.scope_int[-1], self.scope_float[-1], self.scope_char[-1], self.scope_bool[-1])
                    else:
                        self.memory.add_param(self.param_dir[param], st['bool'], self.scope_int[-1], self.scope_float[-1], self.scope_char[-1], self.scope_bool[-1])
                self.instruction_pointer = self.func_dir.get_func(self.quad_dir[self.instruction_pointer][3]).get_first_quad() - 1
            elif self.quad_dir[self.instruction_pointer][0] == so['endfunc']:
                self.memory.release_memory(self.scope_int.pop(), self.scope_float.pop(), self.scope_char.pop(), self.scope_bool.pop())
                self.instruction_pointer = self.back_pointer.pop()  # Gets the pointer out of the scope
            elif self.quad_dir[self.instruction_pointer][0] == so['return']:
                glob = self.quad_dir[self.instruction_pointer][1]  # Global address to save the value returned
                self.add_value(glob, self.fetch_value(self.quad_dir[self.instruction_pointer][3]))
            elif self.quad_dir[self.instruction_pointer][0] == so['line']:
                self.turtle.forward(self.fetch_value(self.quad_dir[self.instruction_pointer][3]))
            elif self.quad_dir[self.instruction_pointer][0] == so['dot']:
                self.turtle.dot(self.fetch_value(self.quad_dir[self.instruction_pointer][3]))
            elif self.quad_dir[self.instruction_pointer][0] == so['circle']:
                self.turtle.circle(self.fetch_value(self.quad_dir[self.instruction_pointer][3]))
            elif self.quad_dir[self.instruction_pointer][0] == so['arc']:
                self.turtle.circle(self.fetch_value(self.quad_dir[self.instruction_pointer][3]), 180)
            elif self.quad_dir[self.instruction_pointer][0] == so['penup']:
                self.turtle.penup()
            elif self.quad_dir[self.instruction_pointer][0] == so['pendown']:
                self.turtle.pendown()
            elif self.quad_dir[self.instruction_pointer][0] == so['color']:
                color = self.quad_dir[self.instruction_pointer][3]
                if color in ['"blue"', '"red"', '"green"']:
                    if color == "blue":
                        self.turtle.color("blue")
                    elif color == "red":
                        self.turtle.color("red")
                    else:
                        self.turtle.color("green")
                else:
                    print('ERROR: Color must be either, reed, green, or blue')
                    raise RuntimeError
            elif self.quad_dir[self.instruction_pointer][0] == so['size']:
                self.turtle.pensize(self.fetch_value(self.quad_dir[self.instruction_pointer][3]))
            elif self.quad_dir[self.instruction_pointer][0] == so['reset']:
                self.turtle.reset()
            elif self.quad_dir[self.instruction_pointer][0] == so['left']:
                self.turtle.left(self.fetch_value(self.quad_dir[self.instruction_pointer][3]))
            elif self.quad_dir[self.instruction_pointer][0] == so['right']:
                self.turtle.right(self.fetch_value(self.quad_dir[self.instruction_pointer][3]))
            self.instruction_pointer += 1  # Moves the pointer to the next instruction
        self.scope_int.pop()  # Pops the scopes
        self.scope_float.pop()
        self.scope_char.pop()
        self.scope_bool.pop()
        self.wn.exitonclick()  # Waits for click to close graphical environment

    # First restores data, then runs the instructions
    def run(self):
        self.restore_data()
        if self.request_memory('main'):
            self.run_instructions()
        else:
            print('Stack Overflow')
            raise MemoryError
        #  self.func_dir.print_dir()  # TESTING
        #  self.const_tab.print_tab()  # TESTING
        #  print(self.quad_dir)  # TESTING
        #  print(obj.read())  # TESTING
