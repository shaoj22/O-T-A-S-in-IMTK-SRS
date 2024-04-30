'''
File: adaptive_large_scale_neighborhood_search.py
Project: Joint_Optimization_of_Orders_and_Totes_for_WayZim.
Description:
-----------
ALNS framework.
-----------
Author: 626
Created Date: 2023-1109
'''


import sys
sys.path.append('../')
import numpy as np
import math
import copy
import tqdm
from src.greedy_algorithm.order_sequence_random import OrderSequenceRandom
from src.greedy_algorithm.order_sequence_greedy import OrderSequenceGreedy
from src.greedy_algorithm.tote_sequence_greedy import ToteSequenceGreedy
from src.mate_heuristic_algorithm.operators import RandomDestroy, RandomRepair, GreedyDestroy, GreedyRepair


class ALNS():
    def __init__(self, instance, iter_num=None, heuristic=None, order_assignment_solution=None):
        """ init the ALNS algorithm
        
        Args:
            instance (obj): instance class.
            iter_num (int): number of the iter.
            heuristic (obj): init solution of heuristic.

        Return:
            best_solution (list[list[list]]): solution of the orders and totes.
        """
        self.name = "ALNS"
        self.instance = instance # instance
        if iter_num is not None: # iter num
            self.iter_num = iter_num
        else:
            self.iter_num = self.instance
        self.heuristic = heuristic # init solution
        self.order_assignment_solution = order_assignment_solution
        # ALNS's operators.
        self.destroy_operators_list = [
                RandomDestroy(min_k=2, max_k=5),
                GreedyDestroy(min_k=2, max_k=5, order_list=self.instance.order_list)
            ]
        self.repair_operators_list = [
                RandomRepair(), 
                GreedyRepair(order_list=self.instance.order_list)
            ]
        # ALNS's parameters
        self.sigma1 = 2
        self.sigma2 = 1
        self.sigma3 = 0.1
        self.rho = 0.1
        self.destroy_operators_weights = np.ones(len(self.destroy_operators_list))
        self.destroy_operators_scores = np.ones(len(self.destroy_operators_list))
        self.destroy_operators_steps = np.ones(len(self.destroy_operators_list))
        self.repair_operators_weights = np.ones(len(self.repair_operators_list))
        self.repair_operators_scores = np.ones(len(self.repair_operators_list))
        self.repair_operators_steps = np.ones(len(self.repair_operators_list))
        # SA's parameters
        self.max_temp = 0.01
        self.min_temp = 1e-10
        self.a = 0.97
        self.a_steps = 50
        # display parameters
        self.process = []

    def solution_init(self):
        """ generate initial solution randomly """
        if self.heuristic is not None: # order sequence greedy algorithm
            order_sequence_greedy_alg = OrderSequenceGreedy(instance=self.instance, order_assignment_solution=self.order_assignment_solution)
            order_sequence_greedy_solution = order_sequence_greedy_alg.order_sequence_solution
            solution = order_sequence_greedy_solution
        else: # order sequence randomly algorithm
            solution = self.order_assignment_solution
        self.best_solution = self.transfer(solution)
        self.best_obj = self.cal_objective(self.best_solution)
        return self.best_solution
    
    def transfer(self, lst_2d):
        flattened_list = [-1]
        for sublist in lst_2d:
            flattened_list.extend(sublist)
            flattened_list.append(-1)
        return flattened_list
    
    def transfer_back(self, list_1d):
        unflattened_list = []
        sublist = []
        for item in list_1d:
            if item == -1:
                # 遇到-1时，表示一个子列表的结束，将当前子列表添加到结果中，并重置子列表
                if sublist:  # 避免在首位和末尾都有-1时出现空的子列表
                    unflattened_list.append(sublist)
                    sublist = []
            else:
                # 将元素添加到当前子列表
                sublist.append(item)
        return unflattened_list    
    
    def cal_objective(self, solution):
        """ calculate fitness(-obj) """
        new_solution = self.transfer_back(solution)
        tote_sequence_greedy_alg = ToteSequenceGreedy(instance=self.instance, order_sequence_solution=new_solution)
        obj = sum(len(row) for row in tote_sequence_greedy_alg.tote_sequence_solution)
        return obj

    def SA_accept(self, detaC, temperature):
        """ accept the new solution """
        return math.exp(-detaC / temperature)

    def temperature_update(self, temperature):
        """ temperature of the SA """
        temperature *= self.a
        temperature = max(self.min_temp, temperature)
        return temperature

    def update_weights(self):
        """ update the weights of the ALNS's operators """
        # update weights
        destroy_deta_weights = self.destroy_operators_scores / self.destroy_operators_steps
        self.destroy_operators_weights = self.rho * self.destroy_operators_weights + (1 - self.rho) * destroy_deta_weights
        repair_deta_weights = self.repair_operators_scores / self.repair_operators_steps
        self.repair_operators_weights = self.rho * self.repair_operators_weights + (1 - self.rho) * repair_deta_weights
        # refresh scores / steps
        self.destroy_operators_scores = np.ones(len(self.destroy_operators_list))
        self.destroy_operators_steps = np.ones(len(self.destroy_operators_list))
        self.repair_operators_scores = np.ones(len(self.repair_operators_list))
        self.repair_operators_steps = np.ones(len(self.repair_operators_list))

    def choose_operator(self):
        """ choose the ALNS's operators """
        # choose destroy operator
        prob1 = self.destroy_operators_weights / sum(self.destroy_operators_weights)
        opt_i1 = np.random.choice(range(len(self.destroy_operators_list)), p=prob1)
        # choose repair operator
        prob2 = self.repair_operators_weights / sum(self.repair_operators_weights)
        opt_i2 = np.random.choice(range(len(self.repair_operators_list)), p=prob2)
        return opt_i1, opt_i2

    def get_neighborhood(self, solution, destroy_operator, repair_operator):
        """ get the operator's neighborhood """
        solution = self.transfer_back(solution)
        new_solution, destroy_list = destroy_operator.get(solution)
        new_solution = repair_operator.get(new_solution, destroy_list)
        new_solution = self.transfer(new_solution)
        return new_solution

    def run(self):
        """ run the ALNS to get the solution """
        cur_solution = self.solution_init() # solution in form of routes
        cur_obj = self.cal_objective(cur_solution)
        self.best_solution = cur_solution
        self.best_obj = cur_obj
        temperature = self.max_temp
        pbar = tqdm.tqdm(range(self.iter_num), desc="ALNS Iteration")
        for step in pbar:
            opt_i1, opt_i2 = self.choose_operator()
            new_solution = self.get_neighborhood(cur_solution, self.destroy_operators_list[opt_i1], self.repair_operators_list[opt_i2])
            new_obj = self.cal_objective(new_solution)
            # obj: minimize the total distance 
            if new_obj < self.best_obj:
                self.best_solution = new_solution
                self.best_obj = new_obj
                cur_solution = new_solution
                cur_obj = new_obj
                self.destroy_operators_scores[opt_i1] += self.sigma1
                self.repair_operators_scores[opt_i2] += self.sigma1
            elif new_obj < cur_obj: 
                cur_solution = new_solution
                cur_obj = new_obj
                self.destroy_operators_scores[opt_i1] += self.sigma2
                self.repair_operators_scores[opt_i2] += self.sigma2
            elif np.random.random() < self.SA_accept(new_obj-cur_obj, temperature):
                cur_solution = new_solution
                cur_obj = new_obj
                self.destroy_operators_scores[opt_i1] += self.sigma3
                self.repair_operators_scores[opt_i2] += self.sigma3
            self.destroy_operators_steps[opt_i1] += 1
            self.repair_operators_steps[opt_i2] += 1
            # reset operators weights and update SA temperature
            if step % self.a_steps == 0: 
                self.update_weights()
                temperature = self.temperature_update(temperature)
            # record process obj
            self.process.append(cur_obj)
            # if step % 100 == 0:
            #     print("iter {}, obj={}".format(step, self.best_obj))
            # print("cur_solution:", cur_solution)
            # print("self.best_solution:", self.best_solution)
            pbar.set_postfix({
                "best_obj" : self.best_obj, 
                "cur_obj" : cur_obj, 
                "temperature" : temperature
            })
        self.best_solution = self.transfer_back(self.best_solution)
        return self.best_solution
