import time
from src.alns.tool.alns_framework import ALNSFramework
from src.alns.tool.adaptive_greedy_initial import AdaptiveGreedyInitial
from src.alns.tool.evaluator import EVALUATOR
from src.alns.alns_args import *
import cProfile
import pstats

class ALNS(ALNSFramework):
    def __init__(self, alns_args, input_path):
        """ alns algorithm for the pdptw. """
        super().__init__(alns_args, input_path)

    def init_solution(self):
        """ initialize the solution. """
        greedyinitial = AdaptiveGreedyInitial(self.input_path)
        return greedyinitial.run()

    def cal_objective(self, solution_op, flag):
        """ calculate the objective value. """
        # start = time.time()
        eva = EVALUATOR(self.input_path, solution_op, flag)
        # end = time.time()
        # print("时长；", end - start)
        return eva.evaluate_solution()


if __name__ == '__main__':
    # for i in range(20):
    #     print("myRandomInstanceGurobi"+str(i))
    #     start = time.time()
    #     input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/experiment/small_scale_experiment/"+"myRandomInstanceGurobi"+str(i)+".json"
    #     # T = 55
    #     instance_obj = read_input_data(input_path=input_path)
    #     alns_args = get_common_alns_args(instance_obj=instance_obj)
    #     alns_algorithm = ALNS(alns_args=alns_args, input_path=input_path)
    #     best_solution, best_obj = alns_algorithm.run()
    #     end = time.time()
    #     print("时长；", end - start)
    start = time.time()
    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/experiment/small_scale_experiment/"+"myRandomInstanceGurobi"+str(0)+".json"
    # T = 55
    instance_obj = read_input_data(input_path=input_path)
    alns_args = get_common_alns_args(instance_obj=instance_obj)

    alns_algorithm = ALNS(alns_args=alns_args, input_path=input_path)
    best_solution, best_obj = alns_algorithm.run()
    end = time.time()
    print("时长；", end - start)
