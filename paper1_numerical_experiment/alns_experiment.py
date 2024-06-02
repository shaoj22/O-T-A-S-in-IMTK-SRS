'''
Author: shaoj22 935619774@qq.com
Date: 2024-03-19 19:59:06
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-04-25 09:31:48
FilePath: \Integrated_Picking_and_Sorting_Model\paper1_numerical_experiment\\alns_experiment.py
Description: alns experiment.
'''


import sys
sys.path.append('..')
import xlwt
import time
from Integrated_Picking_and_Sorting_Model.metaheuristic_algorithm.Integrated_ALNS import ALNS
from Integrated_Picking_and_Sorting_Model.paper1_numerical_experiment.experiment_instances import *


def alns_experiment_runner(instances):
    """" input: instances, output: alns solution  """
    alns_results = []
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("alns")
    save_path = "../Integrated_Picking_and_Sorting_Model/paper1_numerical_experiment/result/alns_results_of_medium_scale_instances.xls"
    alns_idx = 0
    row_idx = 0
    for instance in instances:
        each_alns_idx = 0
        each_alns_results = []
        each_alns_time = []
        for i in range(1):
            alns_solver = ALNS(instance[i], iter_num=10000)
            start_time = time.time()
            solution, obj, obj_of_500 = alns_solver.run()
            end_time = time.time()
            alns_results.append(obj)
            # output the model's result into a file
            cpu_times = end_time - start_time
            each_alns_results.append(obj)
            each_alns_time.append(cpu_times)
        # save the alns's result into a excel file
        avg_obj = sum(each_alns_results) / len(each_alns_results)
        avg_cpu_times = sum(each_alns_time) / len(each_alns_time)
        sheet.write(row_idx, 0, alns_idx)
        sheet.write(row_idx, 1, avg_obj)
        sheet.write(row_idx, 2, avg_cpu_times)
        each_alns_idx += 1
        row_idx += 1
        book.save(save_path)
        alns_idx += 1

    return alns_results


if __name__ == "__main__":
    # generate instances
    small_scale_instances_matrix = generate_small_scale_instances_matrix()
    medium_scale_instances_matrix = generate_medium_scale_instances_matrix()
    large_scale_instance_matrix = generate_large_scale_instances_matrix()
    # small_scale_instances = generate_instances(small_scale_instances_matrix)
    medium_scale_instances = generate_instances(medium_scale_instances_matrix)
    # large_scale_instances = generate_instances(large_scale_instance_matrix)
    # run instances
    # alns_results_1 = alns_experiment_runner(small_scale_instances)
    alns_results_2 = alns_experiment_runner(medium_scale_instances)
    # alns_results_3 = alns_experiment_runner(large_scale_instances)