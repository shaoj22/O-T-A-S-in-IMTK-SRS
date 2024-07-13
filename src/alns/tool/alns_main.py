import time
from src.alns.tool.alns_framework import ALNSFramework
from src.alns.tool.adaptive_greedy_initial import AdaptiveGreedyInitial
from src.alns.tool.evaluator import EVALUATOR
from src.alns.alns_args import *
import cProfile
import pstats

class ALNS(ALNSFramework):
    def __init__(self, alns_args, input_path, T):
        """ alns algorithm for the pdptw. """
        super().__init__(alns_args, input_path, T)

    def init_solution(self):
        """ initialize the solution. """
        greedyinitial = AdaptiveGreedyInitial(self.input_path,self.T)
        return greedyinitial.run()

    def cal_objective(self, solution_op, flag):
        """ calculate the objective value. """
        # start = time.time()
        eva = EVALUATOR(self.input_path, solution_op, self.T, flag)
        # end = time.time()
        # print("时长；", end - start)
        return eva.evaluate_solution()

if __name__ == '__main__':
    start = time.time()
    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/Instance-medium-1.json"
    T = 45
    instance_obj = read_input_data(input_path=input_path)
    alns_args = get_common_alns_args(instance_obj=instance_obj)
    alns_algorithm = ALNS(alns_args=alns_args, input_path=input_path, T=T)
    best_solution, best_obj = alns_algorithm.run()
    end = time.time()
    print("时长；", end - start)

