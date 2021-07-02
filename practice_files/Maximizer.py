import random

class Maximizer():
    def __init__(self, dof, direction, linearity):
        random.seed()
        self.dof = dof
        self.direction = direction
        self.vector = [random.random() for i in range(self.dof)]
        self.linearity = linearity #True if assuming local linearity in the state space among all DOF
    def Run(self, self.vector):
        raise NotImplementedError
    def Score(self, variadic):
        raise NotImplementedError

    def deltaStep(self, value): #Delta step the given value based on the current value's precision


    def singleDOF(self): #Perform local exploration on a single degree of freedom


    def execute(self):
        



