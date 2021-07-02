import Qual2018
import Scorer
import sys
from skopt import gp_minimize
from skopt.space import Real

try:
    inpt = sys.argv[1]
except IndexError:
    print("Please pass in a dataset")
    exit()

# rides, bonus, out = Qual2018.run([1,1,1,1,.0982])
# print(Scorer.run(rides, bonus, out))
# exit()

def wrapper(coefficients):
    rides, bonus, out = Qual2018.run([1,1,1,1]+ coefficients + [0])
    ret = 100000000 - Scorer.run(rides, bonus, out)
    print(ret)
    return ret

dimspace = [
#             Real(0, 1, name="Start location similarity bias"),
#             Real(0, 1, name="End location similarity bias"),
#             Real(0, 1, name="Start time similarity bias"),
#             Real(0, 1, name="End time similarity bias"),
            Real(0, 1, name="Batch tail maximum size"),
            Real(0, 1, name="Batch tail filtering threshold"),
            Real(0, 1, name="Percentage of cars to max DOF"),
            Real(0, 1, name="Distance score weight"),
            Real(0, 1, name="Bonus score weight"),
            Real(0, 1, name="Wasted distance score weight"),
#             Real(0, 1, name="Wasted time score weight")
           ]
result = gp_minimize(wrapper, dimspace, n_calls=100, n_random_starts=10, acq_func='gp_hedge', acq_optimizer='sampling', random_state=1, n_points=10000, kappa=1, xi=.05, noise=1e-10, verbose=True)
print(result.fun)
print(result.x)



