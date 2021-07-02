import random
import copy

class biased_selector():
    def __init__(self, iterable, distribution):
        self.iterable = copy.deepcopy(iterable)
        for i in range(len(self.iterable)):
            try:
                self.iterable[i].append(i)
            except AttributeError:
                print(self.iterable)
                print("Iterable elements must be list encapsulated")
                exit()
        self.distribution = distribution

    def draw(self, replace=False):
        if len(self.iterable) == 0:
            raise IndexError
        weights = []
        total = 0
        for i in range(len(self.iterable)):
            tmp = self.distribution(i+1) #Avoid 0-based evaluations
            total += tmp
            weights.append(tmp)
        weights = [e/total for e in weights]
        ret = random.choices(population=self.iterable, weights=weights, k=1)[0]
        if replace:
            return ret[:-1]
        else:
            del(self.iterable[ret[-1]])
            return ret[:-1]