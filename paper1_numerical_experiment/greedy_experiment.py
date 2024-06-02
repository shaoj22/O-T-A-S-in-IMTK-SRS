'''
Author: shaoj22 935619774@qq.com
Date: 2024-03-19 19:59:06
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-03-20 16:15:48
FilePath: \Integrated_Picking_and_Sorting_Model\paper1_numerical_experiment\\greedy_experiment.py
Description: greedy experiment.
'''


import sys
sys.path.append('..')
import xlwt
import time
from Integrated_Picking_and_Sorting_Model.heuristic_algorithm.greedy_algorithm import greedyAlgorithm
from Integrated_Picking_and_Sorting_Model.paper1_numerical_experiment.experiment_instances import *
from Integrated_Picking_and_Sorting_Model.utils_new import efficient_integrated_evaluate


def greedy_experiment_runner(instances):
    """" input: instances, output: rule based solution  """
    greedy_results = []
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("greedy")
    save_path = "../Integrated_Picking_and_Sorting_Model/paper1_numerical_experiment/result/greedy_results_of_large_scale_instances.xls"
    greedy_idx = 0
    row_idx = 0
    for instance in instances:
        each_greedy_idx = 0
        each_greedy_results = []
        each_greedy_time = []
        for i in range(10):
            greedy_solver = greedyAlgorithm(instance[i])
            start_time = time.time()
            solution = greedy_solver.runner()
            obj, info = efficient_integrated_evaluate(instance[i], solution['picking_solution'], solution['sorting_solution'])
            end_time = time.time()
            each_greedy_results.append(obj)
            # output the model's result into a file
            cpu_times = end_time - start_time
            each_greedy_time.append(cpu_times)
        avg_obj = sum(each_greedy_results) / len(each_greedy_results)
        avg_cpu_times = sum(each_greedy_time) / len(each_greedy_time)
        # save the greedy's result into a excel file
        sheet.write(row_idx, 0, greedy_idx)
        sheet.write(row_idx, 1, avg_obj)
        sheet.write(row_idx, 2, avg_cpu_times)
        each_greedy_idx += 1
        row_idx += 1
        greedy_idx += 1
        book.save(save_path)

    return greedy_results


if __name__ == "__main__":
    # generate instances
    small_scale_instances_matrix = generate_small_scale_instances_matrix()
    medium_scale_instances_matrix = generate_medium_scale_instances_matrix()
    large_scale_instance_matrix = generate_large_scale_instances_matrix()
    # small_scale_instances = generate_instances(small_scale_instances_matrix)
    # medium_scale_instances = generate_instances(medium_scale_instances_matrix)
    large_scale_instances = generate_instances(large_scale_instance_matrix)
    # run instances
    # greedy_results_1 = greedy_experiment_runner(small_scale_instances)
    # greedy_results_2 = greedy_experiment_runner(medium_scale_instances)
    greedy_results_3 = greedy_experiment_runner(large_scale_instances)