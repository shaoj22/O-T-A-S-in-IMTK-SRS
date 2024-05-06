'''
File: order_assignment_greedy.py
Project: Joint_Optimization_of_Order_and_Totes_for_WayZim.
Description:
-----------
generate the greedy init solution of the order assignment.
-----------
Author: 626
Created Date: 2023-1117
'''

import random

class OrderAssignmentGreedy:
    def __init__(self, instance):
        """ init the OrderAssignmentGreedy """
        self.instance = instance
        self.order_num = self.instance.order_num
        self.order_assignment_solution = self.assign()
    
    def assign(self):
        """ assign the orders into the station greedy """
        order_assignment_solution = [[] for station in range(self.instance.station_num)]
        order_assignment_solution_dict = []
        # init the order assignment solution dict
        for station in range(self.instance.station_num):
            order_assignment_solution_dict.append({})
        order_idx_list = [i for i in range(self.order_num)]
        # init the each station's order
        for station in range(self.instance.station_num):
            order_assignment_solution[station].append(random.choice(order_idx_list))
            order_assignment_solution_dict[station] = \
                self.add_sku_into_dict(order_assignment_solution[station][0], \
                                       order_assignment_solution_dict[station])
            order_idx_list.remove(order_assignment_solution[station][0])
        # continue to add the orders into the order assignment solution
        while order_idx_list:
            for station in range(self.instance.station_num):
                # cal the most similarity order's idx of this station and add it into
                order_idx = self.get_most_similar_order_idx(order_idx_list, order_assignment_solution[station])
                order_assignment_solution[station].append(order_idx)
                order_assignment_solution_dict[station] = \
                self.add_sku_into_dict(order_idx, order_assignment_solution_dict[station])
                order_idx_list.remove(order_idx)
                # if empty
                if not order_idx_list:
                    break
        print(sum(len(dic) for dic in order_assignment_solution_dict))
        return order_assignment_solution

    def get_most_similar_order_idx(self, order_list, order_assignment_solution_of_station):
        """ get one station's most similar order """
        max_similarity = 0
        most_similar_order_idx = order_list[0]
        for order in order_list:
            order_similarity = self.get_order_similarity(order, order_assignment_solution_of_station)
            if order_similarity > max_similarity:
                max_similarity = order_similarity
                most_similar_order_idx = order
        return most_similar_order_idx
    
    def get_order_similarity(self, order_idx, order_assignment_solution_of_station):
        """ get one order's similar if it in the station """
        similarity = 0
        for sku in self.instance.order_list[order_idx]['sku']:
            if sku in order_assignment_solution_of_station:
                similarity += 1
        return similarity

    def add_sku_into_dict(self, order_idx, order_assignment_solution_of_station_dict):
        """ add sku into dict """
        for sku in self.instance.order_list[order_idx]['sku']:
            if sku in order_assignment_solution_of_station_dict:
                order_assignment_solution_of_station_dict[sku] += 1
            else:
                order_assignment_solution_of_station_dict[sku] = 1
        return order_assignment_solution_of_station_dict
    
