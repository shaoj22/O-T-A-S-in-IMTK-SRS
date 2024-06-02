'''
Author: shaoj22 935619774@qq.com
Date: 2024-03-19 19:59:06
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-03-21 14:21:31
FilePath: \Integrated_Picking_and_Sorting_Model\paper1_numerical_experiment\gurobi_experiment.py
Description: gurobi experiment.
'''


import sys
sys.path.append('..')
import xlwt
import time
from two_layer_revolving_algorithm.integrated_gurobi_model_update import IntegratedGurobiModel
from paper1_numerical_experiment.experiment_instances import *


def gurobi_experiment_runner(instances):
    """" input: instances, output: models """
    models = []
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("gurobi")
    save_path = "../paper1_numerical_experiment/result/gurobi_medium_scale_instance_results.xls"
    model_idx = 0
    row_idx = 0
    for instance in instances:
        if model_idx < 8:
            model_idx += 1
            continue
        each_model_idx = 0
        each_model_upper_result = []
        each_model_lower_result = []
        each_model_time = []
        for i in range(len(instance)):
            gurobi_solver = IntegratedGurobiModel(instance[i], time_limit=1000)
            start_time = time.time()
            model = gurobi_solver.run_gurobi_model()
            end_time = time.time()
            # output the model's result into a file
            models.append(model)
            cpu_times = end_time - start_time
            upper_bound = model.objBound
            lower_bound = model.objVal
            each_model_upper_result.append(upper_bound)
            each_model_lower_result.append(lower_bound)
            each_model_time.append(cpu_times)
        # save the model's result into a excel file
        avg_upper_bound = sum(each_model_upper_result) / len(each_model_upper_result)
        avg_lower_bound = sum(each_model_lower_result) / len(each_model_lower_result)
        avg_time = sum(each_model_time) / len(each_model_time)
        sheet.write(row_idx, 0, model_idx)
        sheet.write(row_idx, 1, avg_upper_bound)
        sheet.write(row_idx, 2, avg_lower_bound)
        sheet.write(row_idx, 3, avg_time)
        each_model_idx += 1
        row_idx += 1
        book.save(save_path)
        model_idx += 1

    return models


if __name__ == "__main__":
    # generate instances
    small_scale_instances_matrix = generate_small_scale_instances_matrix()
    medium_scale_instances_matrix = generate_medium_scale_instances_matrix()
    # small_scale_instances = generate_instances(small_scale_instances_matrix)
    medium_scale_instances = generate_instances(medium_scale_instances_matrix)
    # run instances
    # models1 = gurobi_experiment_runner(small_scale_instances)
    models2 = gurobi_experiment_runner(medium_scale_instances)

