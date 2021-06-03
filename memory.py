from semantics import types as st


# A memory class to be used both during compilation and execution
class Memory:

    def __init__(self, base_address):
        self.base_address = base_address  # The base memory address
        self.int_off_set = 0  # Offset for integer values
        self.float_off_set = 1000  # Offset for floating point values
        self.char_off_set = 2000  # Offset for characters values
        self.bool_off_set = 3000  # Offset for boolean values
        self.int_counter = 0  # Simulates integer memory during compilation, simply a counter
        self.float_counter = 0  # Simulates floating point memory during compilation, simply a counter
        self.char_counter = 0  # Simulates character memory during compilation, simply a counter
        self.bool_counter = 0  # Simulates boolean memory during compilation, simply a counter
        self.int_segment = {}  # Actual integer memory to be used during execution
        self.float_segment = {}  # Actual floating point memory to be used during execution
        self.char_segment = {}  # Actual character memory to be used during execution
        self.bool_segment = {}  # Actual boolean memory to be used during execution

    # Returns the base address
    def get_base_address(self):
        return self.base_address

    # Returns the int offset
    def get_int_off_set(self):
        return self.int_off_set

    # Returns the floating point offset
    def get_float_off_set(self):
        return self.float_off_set

    # Returns the character offset
    def get_char_off_set(self):
        return self.char_off_set

    # Returns the boolean offset
    def get_bool_off_Set(self):
        return self.bool_off_set

    # Returns the amount of elements in the integer segment
    def int_size(self):
        return len(self.int_segment)

    # Returns the amount of elements in the floating point segment
    def float_size(self):
        return len(self.float_segment)

    # Returns the amount of elements in the character segment
    def char_size(self):
        return len(self.char_segment)

    # Returns the amount of elements in the boolean segment
    def bool_size(self):
        return len(self.bool_segment)

    # To be used in compilation, receives a type and returns the next usable slot in memory for it (counter)
    def assign_ref(self, var_type):
        if var_type == st['int']:
            ref = self.base_address + self.int_off_set + self.int_counter
            self.int_counter += 1
            return ref
        elif var_type == st['float']:
            ref = self.base_address + self.float_off_set + self.float_counter
            self.float_counter += 1
            return ref
        elif var_type == st['char']:
            ref = self.base_address + self.char_off_set + self.char_counter
            self.char_counter += 1
            return ref
        elif var_type == st['bool']:
            ref = self.base_address + self.bool_off_set + self.bool_counter
            self.bool_counter += 1
            return ref

    # To be used in execution, receives an address and returns the corresponding value
    def get_value(self, address):
        type_address = address - self.base_address  # The received address minus the memory's base address
        if type_address < self.float_off_set:  # It's an int address
            real_address = type_address
            return self.int_segment[real_address]
        elif type_address < self.char_off_set:  # It's a float address
            real_address = type_address - self.float_off_set
            return self.float_segment[real_address]
        elif type_address < self.bool_off_set:  # It's a char address
            real_address = type_address - self.char_off_set
            return self.char_segment[real_address]
        else:  # It's a boolean address
            real_address = type_address - self.bool_off_set
            return self.bool_segment[real_address]

    # To be used in execution, adds the given value to the given address
    # "ints", "floats", "chars", "bools" are typed offsets
    def add_element(self, address, value, ints, floats, chars, bools):
        type_address = address - self.base_address  # Received address minus the memory's base address
        if type_address < self.float_off_set:  # It's an int
            real_address = type_address + ints
            self.int_segment[real_address] = int(value)
        elif type_address < self.char_off_set:  # It's a float
            real_address = type_address - self.float_off_set + floats
            self.float_segment[real_address] = float(value)
        elif type_address < self.bool_off_set:  # It's a char
            real_address = type_address - self.char_off_set + chars
            self.char_segment[real_address] = value
        else:  # It's a boolean
            real_address = type_address - self.bool_off_set + bools
            self.bool_segment[real_address] = bool(value)

    # To be used during execution, checks if there's enough room for all of the given arguments
    def check_space(self, ints_used, floats_used, chars_used, bools_used):
        if not self.int_counter + ints_used < 1000 and self.float_counter + floats_used < 1000 and \
                self.char_counter + chars_used < 1000 and self.bool_counter + bools_used < 1000:
            return False
        return True

    # Returns the type corresponding to the address received
    def check_type(self, address):
        type_address = address - self.base_address
        if type_address < self.float_off_set:
            return 'int'
        elif type_address < self.char_off_set:
            return 'float'
        elif type_address < self.bool_off_set:
            return 'char'
        else:
            return 'bool'

    # To be used in execution, pops all the type segments up to the limits provided
    def release_memory(self, int_limit, float_limit, char_limit, bool_limit):
        while self.int_size() != int_limit:
            self.int_segment.pop(self.int_size() - 1)
        while self.float_size() != float_limit:
            self.float_segment.pop(self.float_size() - 1)
        while self.char_size() != char_limit:
            self.char_segment.pop(self.char_size() - 1)
        while self.bool_size() != bool_limit:
            self.bool_segment.pop(self.bool_size() - 1)


# Manages the various memory segments
class MainMemory:

    def __init__(self):
        self.base_global = 5000  # Base address for the global memory segments
        self.base_local = 9000  # Base address for the local memory segments
        self.base_constant = 13000  # Base address for the constant memory segments
        self.global_mem = Memory(self.base_global)  # Initializes the global memory with its base address
        self.local_mem = Memory(self.base_local)  # Initializes the local memory with its base address
        self.const_mem = Memory(self.base_constant)  # Initializes the constant memory with its base address

    # To be used during compilation after a function has been declared, initializes the local memory
    def reset_local_memory(self):
        self.local_mem = Memory(self.base_local)

    # Receives an address and returns the value in it
    def fetch_value(self, address):
        if address < self.base_local:  # It's in the global memory
            return self.global_mem.get_value(address)
        elif address < self.base_constant:  # It's in the local memory
            return self.local_mem.get_value(address)
        else:  # It's in the constant memory
            return self.const_mem.get_value(address)

    # Adds the given value on the given address
    # "ints", "floats", "chars", "bools" are typed offsets
    def add_value(self, address, value, ints, floats, chars, bools):
        if address < self.base_local:  # It's in the global memory
            self.global_mem.add_element(address, value, 0, 0, 0, 0)
        elif address < self.base_constant:  # It's in the local memory
            self.local_mem.add_element(address, value, ints, floats, chars, bools)
        else:  # It's in the constant memory
            self.const_mem.add_element(address, value, 0, 0, 0, 0)

    # To be used during execution, checks whether or not the given address corresponds to the local memory or not
    # In case that the given address is indeed a local one, it returns its type
    # This is used to determine which in-scope-typed offset to use, if any at all
    def check_seg(self, address):
        if self.base_local <= address < self.base_constant:
            return self.local_mem.check_type(address)
        else:
            return 'glob_const'

    # To be used during execution, generates the address for the given value and adds it to local memory
    def add_param(self, value, type, ints, floats, chars, bools):
        base_address = self.base_local
        if type == st['int']:
            address = base_address + self.local_mem.get_int_off_set() + self.local_mem.int_size()
        elif type == st['float']:
            address = base_address + self.local_mem.get_float_off_set() + self.local_mem.float_size()
        else:
            address = base_address + self.local_mem.get_char_off_set() + self.local_mem.char_size()
        self.add_value(address, value, 0, 0, 0, 0)

    # To be used in execution, removes the elements from memory corresponding to the latest scope
    # the limits received indicate up to which cell in memory to release
    def release_memory(self, int_limit, float_limit, char_limit, bool_limit):
        self.local_mem.release_memory(int_limit, float_limit, char_limit, bool_limit)

    # To be used in execution, adds a global variable corresponding to the function been called during the era quad
    def new_func(self, type):
        base_address = self.global_mem.get_base_address()
        if type == st['int']:
            address = base_address + self.global_mem.get_int_off_set() + self.global_mem.int_size()
        elif type == st['float']:
            address = base_address + self.global_mem.get_float_off_set() + self.global_mem.float_size()
        else:
            address = base_address + self.global_mem.get_char_off_set() + self.global_mem.char_size()
        self.global_mem.add_element(address, 0, 0, 0, 0, 0)  # -999 is a temporary value, the 0s are offsets
