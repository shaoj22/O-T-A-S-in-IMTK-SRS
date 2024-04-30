'''
File: input_data.py
Project: Joint_Optimization_of_Order_and_Totes_for_WayZim.
Description:
-----------
read the input data (json file) and create the Instance class.
-----------
Author: 626
Created Date: 2023-1109
'''


import sys
sys.path.append('..')
import random
from collections import Counter
import copy


class OrderSequenceGreedy:
    def __init__(self, instance, order_assignment_solution=None):
        """ init the order sequence random """
        self.instance = instance
        self.order_num = self.instance.order_num
        self.tote_num = self.instance.tote_num
        self.station_num = self.instance.station_num
        self.order_assignment_solution = copy.deepcopy(order_assignment_solution)
        self.order_sequence_solution = [] # order sequence
        self.similarity_matrix = self.get_similarity_matrix()
        self.order_sequence_greedy()
    
    def order_sequence_greedy(self):
        """ sequence the orders greedy can be used as init solution of ALNS """
        for i in range(len(self.order_assignment_solution)):
            self.order_sequence_solution.append(self.order_sequence_greedy_of_station(self.order_assignment_solution[i]))
    
    def order_sequence_greedy_of_station(self, order_assignment_of_station):
        """" sequence the order of one station """
        order_sequence_of_station = []
        # choose the first order: use the max num of sku
        choose_order = 0
        max_sku_num = 0
        for i in range(len(order_assignment_of_station)):
            if len(self.instance.order_list[order_assignment_of_station[i]]['sku']) > max_sku_num:
                max_sku_num = len(self.instance.order_list[order_assignment_of_station[i]]['sku'])
                choose_order = order_assignment_of_station[i]
        order_sequence_of_station.append(choose_order)
        order_assignment_of_station.remove(choose_order)
        # choose the remain orders
        while len(order_assignment_of_station) > 0:
            similarity_num = 0
            choose_order = order_assignment_of_station[0]
            for i in range(len(order_assignment_of_station)):
                # compare with the order_sequence_of_station[-1] to choose the best order and add it into
                if self.similarity_matrix[order_sequence_of_station[-1]][order_assignment_of_station[i]] > similarity_num:
                    similarity_num = self.similarity_matrix[order_sequence_of_station[-1]][order_assignment_of_station[i]]
                    choose_order = order_assignment_of_station[i]
            order_sequence_of_station.append(choose_order)
            order_assignment_of_station.remove(choose_order)
        return order_sequence_of_station

    def get_similarity_matrix(self):
        """ get the similarity matrix of the orders """
        similarity_matrix = [[0 for i in range(len(self.instance.order_list))] for j in range(len(self.instance.order_list))]
        for i in range(len(self.instance.order_list)):
            for j in range(i+1, len(self.instance.order_list)):
                # cal the order i and order j similarity
                counter_order_i = Counter(self.instance.order_list[i]['sku'])
                counter_order_j = Counter(self.instance.order_list[j]['sku'])
                # cal the common num of order i and order j
                common_count_num = sum((counter_order_i & counter_order_j).values())
                similarity_matrix[i][j] = common_count_num
                similarity_matrix[j][i] = common_count_num            
        return similarity_matrix

