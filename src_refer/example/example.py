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
sys.path.append('../')
from src.instance.input_data import read_input_data
from src.clustering_algorithm.order_assignment_random import OrderAssignmentRandom
from src.clustering_algorithm.order_assignment_greedy import OrderAssignmentGreedy
from src.greedy_algorithm.order_sequence_random import OrderSequenceRandom
from src.greedy_algorithm.order_sequence_greedy import OrderSequenceGreedy
from src.greedy_algorithm.tote_sequence_greedy import ToteSequenceGreedy
from src.mate_heuristic_algorithm.adaptive_large_scale_neighborhood_search import ALNS
# read data and print
input_path = "D:\\Desktop\\python_code\\Joint_Optimization_of_Orders_and_Totes_for_WayZim\\src\\instance\\myRandomInstanceGurobi2.json"
instance_obj = read_input_data(input_path)
# print('order_list:', instance_obj.order_list)
# print('tote_list:', instance_obj.tote_list)
# print('station_list:', instance_obj.station_list)
# print('station_buffer_num:', instance_obj.station_buffer_num)
# get order assignment solution
# order_assignment_random_alg = OrderAssignmentRandom(instance=instance_obj)
# order_assignment_random_solution = order_assignment_random_alg.order_assignment_solution
order_assignment_greedy_alg = OrderAssignmentGreedy(instance=instance_obj)
order_assignment_greedy_solution = order_assignment_greedy_alg.order_assignment_solution
# print("order assignment solution:", order_assignment_random_solution)
# get order sequence solution
# order_sequence_random_alg = OrderSequenceRandom(instance=instance_obj, order_assignment_solution=order_assignment_random_solution)
order_sequence_greedy_alg = OrderSequenceGreedy(instance=instance_obj, order_assignment_solution=order_assignment_random_solution)
order_sequence_greedy_solution = order_sequence_greedy_alg.order_sequence_solution
# print("order sequence solution:", order_sequence_greedy_solution)
order_sequence_ALNS_alg = ALNS(instance=instance_obj, iter_num=20000, heuristic=order_sequence_greedy_solution, order_assignment_solution=order_assignment_random_solution)
order_sequence_ALNS_alg.run()
order_sequence_ALNS_solution = order_sequence_ALNS_alg.best_solution
# print("order sequence solution:", order_sequence_random_solution)
# get tote sequence solution
# tote_sequence_greedy_alg = ToteSequenceGreedy(instance=instance_obj, order_sequence_solution=order_sequence_greedy_solution)
# print("tote sequence solution:", tote_sequence_greedy_alg.tote_sequence_solution)
# print('greedy solution:', sum(len(solution) for solution in tote_sequence_greedy_alg.tote_sequence_solution))









# cal the max and min sku num of this instance
sum_sku_max = 0
for i in range(len(instance_obj.order_list)):
    sum_sku_max += len(instance_obj.order_list[i]['sku'])
print("sum_sku_max:", sum_sku_max)
sum_sku_min = []
for station in order_assignment_greedy_solution:
    sum_sku_min_dict = {}
    for i in range(len(station)):
        for j in range(len(instance_obj.order_list[station[i]]['sku'])): 
            if instance_obj.order_list[station[i]]['sku'][j] not in sum_sku_min_dict:
                sum_sku_min_dict[instance_obj.order_list[station[i]]['sku'][j]] = 1
            else:
                sum_sku_min_dict[instance_obj.order_list[station[i]]['sku'][j]] += 1
    sum_sku_min_of_station = len(sum_sku_min_dict)
    sum_sku_min.append(sum_sku_min_of_station)
print("sum_sku_min:", sum(sum_sku_min))






