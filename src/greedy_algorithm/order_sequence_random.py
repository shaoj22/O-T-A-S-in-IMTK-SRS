'''
File: order_sequence_random.py
Project: Joint_Optimization_of_Order_and_Totes_for_WayZim.
Description:
-----------
generate the random init solution of the order sequence.
-----------
Author: 626
Created Date: 2023-1110
'''

import sys
sys.path.append('..')
import random

class OrderSequenceRandom:
    def __init__(self, instance, order_assignment_solution=None):
        """ init the order sequence random """
        self.instance = instance
        self.order_num = self.instance.order_num
        self.tote_num = self.instance.tote_num
        self.station_num = self.instance.station_num
        self.order_assignment_solution = order_assignment_solution
        self.order_sequence_solution = [] # order sequence
        self.order_sequence_random()
    
    def order_sequence_random(self):
        """ generate the random init solution of the order sequence """
        order_sequence_of_station = [] # one station's order sequence list
        for station in range(self.station_num):
            order_sequence_of_station = self.order_assignment_solution[station]
            random.shuffle(order_sequence_of_station) # random generate the sequence
            self.order_sequence_solution.append(order_sequence_of_station)







