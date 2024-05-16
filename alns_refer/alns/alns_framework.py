'''
Author: shaoj22 935619774@qq.com
Date: 2024-05-10 10:41:17
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-05-16 09:54:01
FilePath: \Meituan-INFORMS-TSL-Research-Challenge\pdp_module\test.py
Description: alns's generic framework.
'''


import math
import tqdm
import copy
import numpy as np
import matplotlib.pyplot as plt


class ALNSFramework:
    def __init__(self, alns_args):
        """ ALNS's generic framework. """
        self.iter_num = alns_args.iter_num
        self.adaptive_period = alns_args.adaptive_period
        self.sigma1 = alns_args.sigma1
        self.sigma2 = alns_args.sigma2
        self.sigma3 = alns_args.sigma3
        self.max_temp = alns_args.max_temp
        self.min_temp = alns_args.min_temp
        self.cooling_rate = alns_args.cooling_rate
        self.cooling_period = alns_args.cooling_period
        self.break_operators_list = alns_args.break_operators_list
        self.repair_operators_list = alns_args.repair_operators_list
    
    def set_operators_list(self):
        """ set operators' list. """
        self.break_operators_list = []
        self.repair_operators_list = []
        raise NotImplementedError

    def init_solution(self):
        """ initialize the solution. """
        raise NotImplementedError
    
    def cal_objective(self):
        """ calculate the objective value. """
        raise NotImplementedError 

    def reset(self):
        """ reset the alns framework. """
        self.reset_operators_scores()
        self.obj_iter_process = []
    
    def reset_operators_scores(self):
        """ reset operators' scores. """
        self.break_operators_scores = np.ones(len(self.break_operators_list))
        self.repair_operators_scores = np.ones(len(self.repair_operators_list))
        self.break_operators_steps = np.ones(len(self.break_operators_list))
        self.repair_operators_steps = np.ones(len(self.repair_operators_list))
    
    def SA_accept(self, delta_c, temperature):
        """ accept the neighborhood solution by SA. """
        return math.exp(-delta_c / temperature)

    def temperature_update(self, temperature, step):
        """ update temperature by dynamic steps. """
        if step % self.cooling_period == 0:
            temperature *= self.cooling_rate
        temperature = max(self.min_temp, temperature)
        return temperature

    def choose_operator(self):
        """ choose operators by their scores. """
        break_weights = self.break_operators_scores / self.break_operators_steps
        repair_weights = self.repair_operators_scores / self.repair_operators_steps
        break_prob = break_weights / sum(break_weights)
        repair_prob = repair_weights / sum(repair_weights)
        break_opt_i = np.random.choice(range(len(self.break_operators_list)), p=break_prob)
        repair_opt_i = np.random.choice(range(len(self.repair_operators_list)), p=repair_prob)
        return break_opt_i, repair_opt_i
    
    def get_neighborhood(self, solution, break_opt_i, repair_opt_i):
        """ get the neighborhood solution by operators. """
        solution = copy.deepcopy(solution)
        break_info = self.break_operators_list[break_opt_i].set(solution)
        self.repair_operators_list[repair_opt_i].set(solution, break_info)
        return solution

    def show_process(self):
        """ show the iteration process of ALNS. """
        y = self.obj_iter_process
        x = np.arange(len(y))
        plt.plot(x, y)
        plt.title("Iteration Process of ALNS")
        plt.xlabel("Iteration")
        plt.ylabel("Objective")
        plt.show()

    def run(self):
        """ run ALNS. """
        self.reset()
        cur_solution = self.init_solution() 
        cur_obj = self.cal_objective(cur_solution)
        self.best_solution = cur_solution
        self.best_obj = cur_obj
        temperature = self.max_temp
        pbar = tqdm.tqdm(range(self.iter_num), desc="ALNS Iteration")
        for step in pbar:
            break_opt_i, repair_opt_i = self.choose_operator()
            new_solution = self.get_neighborhood(cur_solution, break_opt_i, repair_opt_i)
            new_obj = self.cal_objective(new_solution)
            if new_obj < self.best_obj:
                self.best_solution = new_solution
                self.best_obj = new_obj
                cur_solution = new_solution
                cur_obj = new_obj
                self.break_operators_scores[break_opt_i] += self.sigma1
                self.break_operators_steps[break_opt_i] += 1
                self.repair_operators_scores[repair_opt_i] += self.sigma1
                self.repair_operators_steps[repair_opt_i] += 1
            elif new_obj < cur_obj: 
                cur_solution = new_solution
                cur_obj = new_obj
                self.break_operators_scores[break_opt_i] += self.sigma2
                self.break_operators_steps[break_opt_i] += 1
                self.repair_operators_scores[repair_opt_i] += self.sigma2
                self.repair_operators_steps[repair_opt_i] += 1
            elif np.random.random() < self.SA_accept((new_obj-cur_obj)/(cur_obj+1e-10), temperature):
                cur_solution = new_solution
                cur_obj = new_obj
                self.break_operators_scores[break_opt_i] += self.sigma3
                self.break_operators_steps[break_opt_i] += 1
                self.repair_operators_scores[repair_opt_i] += self.sigma3
                self.repair_operators_steps[repair_opt_i] += 1
            if step % self.adaptive_period == 0: 
                self.reset_operators_scores()
            temperature = self.temperature_update(temperature, step)
            pbar.set_postfix({
                "best_obj" : self.best_obj, 
                "cur_obj" : cur_obj, 
                "temperature" : temperature,
            })
        
        return self.best_solution, self.best_obj
