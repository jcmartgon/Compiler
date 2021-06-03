##################################################
# Quadruple-related classes
##################################################


# Quadruple class following the format: operator first operand second operand result
class Quad:

    # Constructor method
    def __init__(self, operator, first_operand, second_operand, res):
        self.operator = operator
        self.first_operand = first_operand
        self.second_operand = second_operand
        self.res = res

    # Returns the quadruple's operator
    def get_operator(self):
        return self.operator

    # Returns the quadruple's first operator
    def get_first_operand(self):
        return self.first_operand

    # Returns the quadruple's first operator
    def get_second_operand(self):
        return self.second_operand

    # Returns the quadruple's result
    def get_res(self):
        return self.res

    # Sets the quadruple's res value to result
    def set_res(self, result):
        self.res = result


# Quadruple manager class
class QuadMan:

    # Constructor method
    def __init__(self):
        self.quads = []

    def get_quads(self):
        return self.quads

    # Adds a quadruple to the quadruples' stack
    def add_quad(self, operator, first_operand, second_operand, res):
        self.quads.append(Quad(operator, first_operand, second_operand, res))

    # Returns the length of the quadruples' stack
    def size(self):
        return len(self.quads)

    # Sets a jump on the quadruples' stack's given index to the given jump_to address
    def fill(self, ind, jump_to):
        self.quads[ind].set_res(jump_to)

    # For testing purposes, prints each quadruple one by one
    def print_quads(self):
        print('Quadruples:')
        for quad in self.quads:
            print(quad.get_operator(), " ", quad.get_first_operand(), " ", quad.get_second_operand(), " ",
                  quad.get_res())
