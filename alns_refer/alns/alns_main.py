'''
Author: shaoj22 935619774@qq.com
Date: 2024-05-10 10:36:36
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-05-15 17:02:32
FilePath: \Meituan-INFORMS-TSL-Research-Challenge\pdp_module\alns\alns_main.py
Description: main function of alns.
'''


import sys
sys.path.append("..")
import numpy as np
from pdp_module.alns.alns_framework import ALNSFramework
from pdp_module.alns.evaluator import evaluate_solution
from pdp_module.alns.adaptive_nearest_neighbor import AdaptiveNearestNeighbor
from pdp_module.data.input_alns_data import input_alns_data


class ALNS(ALNSFramework):
    def __init__(self, instance, alns_args):
        """ alns algorithm for the pdptw. """
        super().__init__(alns_args)
        self.instance = instance

    def init_solution(self):
        """ get the initial solution. """
        init_algorithm_tool = AdaptiveNearestNeighbor(self.instance)
        init_solution = init_algorithm_tool.run()
        return init_solution
    
    def cal_objective(self, solution):
        """ calculate the objective value of the solution. """
        obj = evaluate_solution(instance=self.instance, solution=solution)
        return obj

    def choose_operator(self):
        """ choose the operator. """
        # choose break operator
        break_weights = self.break_operators_scores / self.break_operators_steps
        break_prob = break_weights / sum(break_weights)
        break_opt_i = np.random.choice(range(len(self.break_operators_list)), p=break_prob)
        # choose repair operator
        repair_weights = self.repair_operators_scores / self.repair_operators_steps
        repair_prob = repair_weights / sum(repair_weights)
        repair_opt_i = np.random.choice(range(len(self.repair_operators_list)), p=repair_prob)
        return break_opt_i, repair_opt_i
  

if __name__ == '__main__':
    instance = input_alns_data('../data/input.json')