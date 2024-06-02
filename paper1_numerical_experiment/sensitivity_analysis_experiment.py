'''
Author: shaoj22 935619774@qq.com
Date: 2024-03-19 19:59:06
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-03-25 10:06:54
FilePath: \Integrated_Picking_and_Sorting_Model\paper1_numerical_experiment\\sensitivity_analysis_experiment.py
Description: sensitivity analysis experiment.
'''


import sys
sys.path.append('..')
import xlwt
import time
from Integrated_Picking_and_Sorting_Model.metaheuristic_algorithm.Integrated_ALNS import ALNS
from Integrated_Picking_and_Sorting_Model.generate_instances.Integrated_Instance import Instance


def generate_instances(instances_matrix):
    """ input instances matrix, output instances """

    instances = []
    for instance_matrix in instances_matrix:
        instance = Instance(instance_matrix[0], instance_matrix[1], instance_matrix[2], instance_matrix[3], instance_matrix[4], instance_matrix[5])
        instances.append(instance)
    
    return instances

def alns_experiment_runner(instances_matrix, instances, name='test'):
    """" input: instances, output: alns solution  """
    
    alns_results = []
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("alns")
    save_path = "../Integrated_Picking_and_Sorting_Model/paper1_numerical_experiment/result/sensitivity_analysis_for_" + name + ".xls"
    row_idx = 0
    for instance in instances:
        alns_solver = ALNS(instance, iter_num=100000)
        start_time = time.time()
        solution, obj, obj_of_500 = alns_solver.run()
        end_time = time.time()
        alns_results.append(obj)
        cpu_times = end_time - start_time
        # save the alns's result into a excel file
        sheet.write(row_idx, 0, row_idx+1)
        sheet.write(row_idx, 1, instances_matrix[row_idx][0])
        sheet.write(row_idx, 2, instances_matrix[row_idx][1])
        sheet.write(row_idx, 3, instances_matrix[row_idx][2])
        sheet.write(row_idx, 4, instances_matrix[row_idx][3])
        sheet.write(row_idx, 5, instances_matrix[row_idx][4])
        sheet.write(row_idx, 6, instances_matrix[row_idx][5])
        sheet.write(row_idx, 7, obj)
        sheet.write(row_idx, 8, cpu_times)
        row_idx += 1
        book.save(save_path)

    return alns_results


if __name__ == "__main__":
    # # block's width
    # instances_matrix_1 = [
    #     [2, 4, 60, 50, 20, 10],
    #     [3, 4, 60, 50, 20, 10],
    #     [4, 4, 60, 50, 20, 10],
    #     [5, 4, 60, 50, 20, 10],
    #     [6, 4, 60, 50, 20, 10],
    #     [7, 4, 60, 50, 20, 10],
    #     [8, 4, 60, 50, 20, 10],
    #     [9, 4, 60, 50, 20, 10],
    #     [10, 4, 60, 50, 20, 10],
    # ]
    # instances_1 = generate_instances(instances_matrix_1)
    # alns_results_1 = alns_experiment_runner(instances_matrix_1, instances_1, name='block_width')
    
    # # block's length
    # instances_matrix_2 = [
    #     [4, 2, 60, 50, 20, 10],
    #     [4, 3, 60, 50, 20, 10],
    #     [4, 4, 60, 50, 20, 10],
    #     [4, 5, 60, 50, 20, 10],
    #     [4, 6, 60, 50, 20, 10],
    #     [4, 7, 60, 50, 20, 10],
    #     [4, 8, 60, 50, 20, 10],
    #     [4, 9, 60, 50, 20, 10],
    #     [4, 10, 60, 50, 20, 10],
    # ]
    # instances_2 = generate_instances(instances_matrix_2)
    # alns_results_2 = alns_experiment_runner(instances_matrix_2, instances_2, name='block_length')

    # # tote's num
    # instances_matrix_3 = [
    #     [4, 4, 20, 50, 20, 10],
    #     [4, 4, 30, 50, 20, 10],
    #     [4, 4, 40, 50, 20, 10],
    #     [4, 4, 50, 50, 20, 10],
    #     [4, 4, 60, 50, 20, 10],
    #     [4, 4, 70, 50, 20, 10],
    #     [4, 4, 80, 50, 20, 10],
    #     [4, 4, 90, 50, 20, 10],
    #     [4, 4, 100, 50, 20, 10],
    # ]
    # instances_3 = generate_instances(instances_matrix_3)
    # alns_results_3 = alns_experiment_runner(instances_matrix_3, instances_3, name='tote_num')

    # # order's num
    # instances_matrix_4 = [
    #     [4, 4, 60, 20, 20, 10],
    #     [4, 4, 60, 30, 20, 10],
    #     [4, 4, 60, 40, 20, 10],
    #     [4, 4, 60, 50, 20, 10],
    #     [4, 4, 60, 60, 20, 10],
    #     [4, 4, 60, 70, 20, 10],
    #     [4, 4, 60, 80, 20, 10],
    #     [4, 4, 60, 90, 20, 10],
    #     [4, 4, 60, 100, 20, 10],
    # ]
    # instances_4 = generate_instances(instances_matrix_4)
    # alns_results_4 = alns_experiment_runner(instances_matrix_4, instances_4, name='order_num')

    # robot's num
    instances_matrix_5 = [
        [4, 4, 60, 50, 10, 10],
        [4, 4, 60, 50, 15, 10],
        [4, 4, 60, 50, 20, 10],
        [4, 4, 60, 50, 25, 10],
        [4, 4, 60, 50, 30, 10],
        [4, 4, 60, 50, 35, 10],
        [4, 4, 60, 50, 40, 10],
        [4, 4, 60, 50, 45, 10],
        [4, 4, 60, 50, 50, 10],
    ]
    instances_5 = generate_instances(instances_matrix_5)
    alns_results_5 = alns_experiment_runner(instances_matrix_5, instances_5, name='robot_num')

    # # station's num
    # instances_matrix_6 = [
    #     [4, 4, 60, 50, 20, 2],
    #     [4, 4, 60, 50, 20, 3],
    #     [4, 4, 60, 50, 20, 4],
    #     [4, 4, 60, 50, 20, 5],
    #     [4, 4, 60, 50, 20, 6],
    #     [4, 4, 60, 50, 20, 7],
    #     [4, 4, 60, 50, 20, 8],
    #     [4, 4, 60, 50, 20, 9],
    #     [4, 4, 60, 50, 20, 10],
    # ]
    # instances_6 = generate_instances(instances_matrix_6)
    # alns_results_6 = alns_experiment_runner(instances_matrix_6, instances_6, name='station_num')
    
    
    