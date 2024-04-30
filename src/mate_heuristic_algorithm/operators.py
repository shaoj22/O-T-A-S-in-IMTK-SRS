'''
File: operators.py
Project: Joint_Optimization_of_Orders_and_Totes_for_WayZim.
Description:
-----------
some operators for the ALNS.
-----------
Author: 626
Created Date: 2023-1109
'''


import sys
sys.path.append("..")
import numpy as np
import random
import copy

class ReverseDestroy():
    def get(self, solution):
        new_solution = solution.copy()
        pi = np.random.randint(1, len(solution)-2)
        pj = np.random.randint(pi+1, len(solution)-1)
        new_solution[pi:pj+1] = new_solution[pj:pi-1:-1]
        destroy_list = []
        return new_solution, destroy_list

class RelocateDestroy():
    def __init__(self, k=1):
        self.k = k
    
    def get(self, solution):
        new_solution = solution.copy()
        pi = np.random.randint(1, len(solution)-self.k) 
        li = np.random.randint(1, len(solution)-self.k) 
        points = []
        for _ in range(self.k):
            points.append(new_solution.pop(pi))
        for p in points[::-1]:
            new_solution.insert(li, p)
        destroy_list = []
        return new_solution, destroy_list

class RandomDestroy(): 
    def __init__(self, min_k = 2, max_k = 5):
        """ random destroy k orders """
        self.min_k = min_k # minimum destroy number
        self.max_k = max_k # maximum destroy number

    def get(self, solution):
        new_solution = solution.copy()
        # random destroy number
        order_num = sum(len(station) for station in solution)
        destroy_num = min(np.random.randint(self.min_k, self.max_k), order_num-2)
        # randomly choose destroy place (can't destroy first/last 0)
        new_solution, destroy_list = self.random_destroy(new_solution, destroy_num)
        return new_solution, destroy_list
    
    def random_destroy(self, solution, destroy_num):
        rows = len(solution)
        cols = len(solution[0])   
        new_solution = copy.deepcopy(solution)
        destroy_list = [[] for _ in range(rows)]
        # new_solution = copy.deepcopy(solution)
        for _ in range(destroy_num):
            # 随机选择要破坏的元素的位置
            i = random.randint(0, rows - 1)
            j = random.randint(0, cols - 1)
            # 保存被破坏的元素到destroy中，并在solution中删除它
            if i >= len(solution) or j >= len(solution[i]):
                continue
            destroyed_element = solution[i][j]
            if destroyed_element not in destroy_list[i]:
                destroy_list[i].append(destroyed_element)
        # take destroy element out
        for i in range(len(solution)):
            for element in destroy_list[i]:
                if element in solution[i]:
                    new_solution[i].remove(element)
        return new_solution, destroy_list

class GreedyDestroy():
    def __init__(self, min_k=2, max_k=5, order_list=None):
        self.min_k = min_k # minimul destroy number
        self.max_k = max_k # maximum destroy number
        self.order_list = order_list # use to calculate obj

    def get(self, solution):
        rows = len(solution)
        cols = len(solution[0])   
        destroy_list = [[] for _ in range(rows)]
        new_solution = solution.copy()
        # random destroy number
        destroy_num = min(np.random.randint(self.min_k, self.max_k), len(solution)-2)
        # greedy choose destroy place
        for i in range(destroy_num):
            random_station = np.random.randint(0, rows - 1)
            random_station_similarity = []
            for j in range(len(new_solution[random_station])):
                random_station_similarity.append(self.cal_order_similarity(j, new_solution[random_station]))
            max_order_index = random_station_similarity.index(max(random_station_similarity))
            if new_solution[random_station][max_order_index] not in destroy_list[random_station]:
                destroy_list[random_station].append(new_solution[random_station][max_order_index])
        # take destroy element out
        for i in range(len(solution)):
            for element in destroy_list[i]:
                if element in solution[i]:
                    new_solution[i].remove(element)
        return new_solution, destroy_list       
    
    def cal_order_similarity(self, index, solution_of_station):
        """ cal one order's similarity in its solution of station """
        # get the start index and end index
        if index - 4 <= 0:
            start_index = 0
        else:
            start_index = index - 4
        if index + 4 >= len(solution_of_station):
            end_index = len(solution_of_station)
        else:
            end_index = index + 4
        # cal the similarity
        similarity_dict = {}
        for i in range(len(self.order_list[solution_of_station[index]]['sku'])):
            if self.order_list[solution_of_station[index]]['sku'][i] not in similarity_dict:
                similarity_dict[self.order_list[solution_of_station[index]]['sku'][i]] = 1
        for i in range(start_index, end_index):
            if i == index:
                continue
            else:
                for j in range(len(self.order_list[solution_of_station[i]]['sku'])):
                    if self.order_list[solution_of_station[i]]['sku'][j] not in similarity_dict:
                        similarity_dict[self.order_list[solution_of_station[i]]['sku'][j]] = 1
                    else:
                        similarity_dict[self.order_list[solution_of_station[i]]['sku'][j]] += 1
        return len(similarity_dict)
  
class ShawDestroy():
    def __init__(self, min_k = 2, max_k = 5, disMatrix = None):
        self.min_k = min_k # minimul destroy number
        self.max_k = max_k # maximum destroy number
        self.disMatrix = disMatrix

    def get(self, solution):
        new_solution = solution.copy()
        # random destroy number
        destroy_num = min(np.random.randint(self.min_k, self.max_k), len(solution)-2)
        # randomly choose one destroy place (can't destroy first/last 0)
        first_destroy_idx = np.random.choice(range(1, len(new_solution)-1))
        dist_idx_list = []
        for idx in range(1, len(new_solution)-1):
            dist = self.disMatrix[new_solution[first_destroy_idx], new_solution[idx]]
            dist_idx_list.append([dist, idx])
        dist_idx_list.sort(key=lambda x:x[0])
        destroy_idx_list = [dist_idx_list[i][1] for i in range(len(dist_idx_list)) if i < destroy_num]
        destroy_list = [new_solution[i] for i in destroy_idx_list]
        # take destroy element out
        delete_count = 0
        idx = 0
        while idx < len(new_solution):
            check_idx = idx + delete_count
            if check_idx in destroy_idx_list:
                new_solution.pop(idx)
                delete_count += 1
            else:
                idx += 1
        return new_solution, destroy_list

class RandomRepair():
    def get(self, new_solution, destroy_list):
        for i in range(len(new_solution)):
            # 获取当前行的元素
            current_solution_row = new_solution[i]
            # 获取当前行要插入的元素
            destroy_elements = destroy_list[i]
            # 在当前行的随机位置插入元素
            for element in destroy_elements:
                random_index = random.randint(0, len(current_solution_row))
                current_solution_row.insert(random_index, element)
        return new_solution
        
class GreedyRepair():
    def __init__(self, order_list=None):
        self.order_list = order_list
    def get(self, new_solution, destroy_list):
        for i in range(len(destroy_list)):
            for j in range(len(destroy_list[i])):
                # get the new solution of station
                insert_order = destroy_list[i][j]
                max_dis = 1000
                max_index = 0
                for k in range(len(new_solution[i])):
                    new_solution_of_station = new_solution[i].copy()
                    new_solution_of_station.insert(k, insert_order)
                    cur_dis = self.cal_order_similarity(k, new_solution_of_station)
                    if cur_dis < max_dis:
                        max_index = k
                new_solution[i].insert(max_index, insert_order)
        return new_solution

    def cal_order_similarity(self, index, solution_of_station):
        """ cal one order's similarity in its solution of station """
        # get the start index and end index
        if index - 4 <= 0:
            start_index = 0
        else:
            start_index = index - 4
        if index + 4 >= len(solution_of_station):
            end_index = len(solution_of_station)
        else:
            end_index = index + 4
        # cal the similarity
        similarity_dict = {}
        for i in range(len(self.order_list[solution_of_station[index]]['sku'])):
            if self.order_list[solution_of_station[index]]['sku'][i] not in similarity_dict:
                similarity_dict[self.order_list[solution_of_station[index]]['sku'][i]] = 1
        for i in range(start_index, end_index):
            if i == index:
                continue
            else:
                for j in range(len(self.order_list[solution_of_station[i]]['sku'])):
                    if self.order_list[solution_of_station[i]]['sku'][j] not in similarity_dict:
                        similarity_dict[self.order_list[solution_of_station[i]]['sku'][j]] = 1
                    else:
                        similarity_dict[self.order_list[solution_of_station[i]]['sku'][j]] += 1
        return len(similarity_dict)

class RegretRepair():
    def __init__(self, regret_n=8, disMatrix=None, alg=None):
        self.regret_n = regret_n
        self.disMatrix = disMatrix
        self.alg = alg
    
    def get(self, new_solution, destroy_list):
        unassigned_list = destroy_list.copy()
        routes = self.alg.transfer(new_solution)
        while unassigned_list:
            best_insert_list = []
            regret_list = []
            for pi in unassigned_list:
                extra_dist_list = []
                min_extra_dist = np.inf
                for j in range(1, len(new_solution)):
                    p1 = new_solution[j-1]
                    p2 = pi
                    p3 = new_solution[j]
                    extra_dist = self.disMatrix[p1, p2] + self.disMatrix[p2, p3] - self.disMatrix[p1, p3]
                    extra_dist_list.append(extra_dist)
                    if extra_dist < min_extra_dist:
                        min_extra_dist = extra_dist
                        best_insert_j = j
                extra_dist_list.sort() # increase order
                regret_list.append(sum(extra_dist_list[:self.regret_n]) - extra_dist_list[0]*self.regret_n)
                best_insert_list.append(best_insert_j)
            chosen_i = regret_list.index(max(regret_list))
            pi = unassigned_list.pop(chosen_i)
            best_insert = best_insert_list[chosen_i]
            new_solution.insert(best_insert, pi)
        return new_solution