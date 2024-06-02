'''
Author: shaoj22 935619774@qq.com
Date: 2024-03-19 19:59:06
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-04-15 16:54:04
FilePath: \Integrated_Picking_and_Sorting_Model\paper1_numerical_experiment\RL_experiment.py
Description: RL experiment.
'''


import sys
sys.path.append('..')
import xlwt
import os
import matplotlib.pyplot as plt
import json
import xlwt
from Integrated_Picking_and_Sorting_Model.RL_choose_operator import Test
from Integrated_Picking_and_Sorting_Model.paper1_numerical_experiment.experiment_instances import *


def RL_experiment_runner(instances):
    """" input: instances, output: models """
    cur_dir = os.path.dirname(__file__)
    instance_list = [instance[0] for instance in instances]
    model_dir = "d:\\Desktop\\python_code\\Integrated_Picking_and_Sorting_Model\\RL_choose_operator\\log\\sb3\\ppo-20240414-203214\\model.zip"
    tester = Test.Tester(instance_list, 10000, model_dir, cur_dir + '/result')
    results = tester.test()
    # export to excel
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("RL")
    save_path = cur_dir + "/result/RL_results.xls"
    RL_iter_obj_list = results['ChooseOperatorWithModel']['iter_obj_list']
    ALNS_iter_obj_list = results['ChooseOperatorWithALNS']['iter_obj_list']
    for row in range(len(RL_iter_obj_list[0])):
        for ins in range(len(instances)):
            sheet.write(row, ins, RL_iter_obj_list[ins][row])
            sheet.write(row, ins+10, ALNS_iter_obj_list[ins][row])
    book.save(save_path)

    return results

def plot_comparison(data1, data2):
    """
    Plot comparison of data from two methods in a line graph.

    Args:
    data1 (list): Data from the first method. A two-dimensional list where each one-dimensional list represents a line, and each element is the y-axis value of that line at different x-axis positions.
    data2 (list): Data from the second method. A two-dimensional list where each one-dimensional list represents a line, and each element is the y-axis value of that line at different x-axis positions.
    """
    # Set the figure size
    plt.figure(figsize=(8, 6))

    # Plot the curves for the first method
    for line_data in data1:
        x_values = list(range(len(line_data)))  # x-axis values are indices
        plt.plot(x_values, line_data, linestyle='-', marker='', linewidth=2)  # Plot curves

    # Plot the curves for the second method
    for line_data in data2:
        x_values = list(range(len(line_data)))  # x-axis values are indices
        plt.plot(x_values, line_data, linestyle='--', marker='', linewidth=2)  # Plot curves

    # Add legend and labels
    plt.legend(['Method 1 - Line {}'.format(i+1) for i in range(len(data1))] + \
               ['Method 2 - Line {}'.format(i+1) for i in range(len(data2))], loc='upper left')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Comparison of Two Methods')

    # Show the plot
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # generate instances
    RL_instances_matrix = generate_RL_instances_matrix()
    medium_scale_instances = generate_instances(RL_instances_matrix)
    # run instances
    # results = RL_experiment_runner(medium_scale_instances)
    # plot
    cur_dir = os.path.dirname(__file__)
    json_file_dir = cur_dir + '/result/test_result.json'
    with open(json_file_dir, 'r') as f:
        results = json.load(f)
    # 提取每个method的obj
    RL_obj_list = results['ChooseOperatorWithModel']['obj']
    ALNS_obj_list = results['ChooseOperatorWithALNS']['obj']
    # 提取每个method的iter_obj_list
    RL_iter_obj_list = results['ChooseOperatorWithModel']['iter_obj_list']
    ALNS_iter_obj_list = results['ChooseOperatorWithALNS']['iter_obj_list']
    # plot
    plot_comparison(RL_iter_obj_list, ALNS_iter_obj_list)

