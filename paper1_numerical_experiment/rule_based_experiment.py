'''
Author: shaoj22 935619774@qq.com
Date: 2024-03-19 19:59:06
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-03-20 14:41:20
FilePath: \Integrated_Picking_and_Sorting_Model\paper1_numerical_experiment\\rule_based_experiment.py
Description: rule based experiment.
'''


import sys
sys.path.append('..')
import xlwt
import time
from Integrated_Picking_and_Sorting_Model.heuristic_algorithm.rule_based_algorithm import ruleBasedAlgorithm
from Integrated_Picking_and_Sorting_Model.paper1_numerical_experiment.experiment_instances import *
from Integrated_Picking_and_Sorting_Model.utils_new import efficient_integrated_evaluate


def rule_based_experiment_runner(instances):
    """" input: instances, output: rule based solution  """
    rule_based_results = []
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("rule_based")
    save_path = "../Integrated_Picking_and_Sorting_Model/paper1_numerical_experiment/result/rule_based_results_of_large_scale_instances.xls"
    rule_based_idx = 0
    row_idx = 0
    for instance in instances:
        each_rule_based_idx = 0
        each_rule_based_results = []
        each_rule_based_time = []
        for i in range(10):
            rule_based_solver = ruleBasedAlgorithm(instance[i])
            start_time = time.time()
            solution = rule_based_solver.runner()
            obj, info = efficient_integrated_evaluate(instance[i], solution['picking_solution'], solution['sorting_solution'])
            end_time = time.time()
            each_rule_based_results.append(obj)
            # output the model's result into a file
            cpu_times = end_time - start_time
            each_rule_based_time.append(cpu_times)
        avg_obj = sum(each_rule_based_results) / len(each_rule_based_results)
        avg_cpu_times = sum(each_rule_based_time) / len(each_rule_based_time)
        # save the rule_based's result into a excel file
        sheet.write(row_idx, 0, rule_based_idx)
        sheet.write(row_idx, 1, avg_obj)
        sheet.write(row_idx, 2, avg_cpu_times)
        each_rule_based_idx += 1
        row_idx += 1
        rule_based_idx += 1
        book.save(save_path)

    return rule_based_results


if __name__ == "__main__":
    # generate instances
    small_scale_instances_matrix = generate_small_scale_instances_matrix()
    medium_scale_instances_matrix = generate_medium_scale_instances_matrix()
    large_scale_instance_matrix = generate_large_scale_instances_matrix()
    # small_scale_instances = generate_instances(small_scale_instances_matrix)
    medium_scale_instances = generate_instances(medium_scale_instances_matrix)
    large_scale_instances = generate_instances(large_scale_instance_matrix)
    # run instances
    # rule_based_results_1 = rule_based_experiment_runner(small_scale_instances)
    # rule_based_results_2 = rule_based_experiment_runner(medium_scale_instances)
    rule_based_results_3 = rule_based_experiment_runner(large_scale_instances)