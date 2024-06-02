'''
Author: shaoj22 935619774@qq.com
Date: 2024-03-19 20:01:38
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-03-20 09:25:42
FilePath: \Integrated_Picking_and_Sorting_Model\paper1_numerical_experiment\experiment_instances.py
Description: generate instances for numerical experiment.
'''


import sys
sys.path.append('..')
from Integrated_Picking_and_Sorting_Model.generate_instances.Integrated_Instance import Instance


def generate_small_scale_instances_matrix():
    """ generate small scale instances matrix """

    small_scale_instances_matrix = [
        [2, 4, 2, 3, 3, 2],
        [2, 4, 4, 3, 3, 2],
        [2, 4, 6, 3, 3, 2],
        [4, 4, 8, 6, 6, 4],
        [4, 4, 10, 6, 6, 4],
        [4, 4, 12, 6, 6, 4],
        [6, 4, 14, 9, 9, 6],
        [6, 4, 16, 9, 9, 6],
        [6, 4, 18, 9, 9, 6],
    ]
    
    return small_scale_instances_matrix

def generate_medium_scale_instances_matrix():
    """ generate medium scale instances matrix """

    medium_scale_instances_matrix = [
        [6, 8, 20, 10, 4, 2],
        [6, 8, 25, 15, 6, 3],
        [6, 8, 30, 20, 8, 4],
        [8, 8, 35, 25, 10, 5],
        [8, 8, 40, 30, 12, 6],
        [8, 8, 45, 35, 14, 7],
        [10, 8, 50, 40, 16, 8],
        [10, 8, 55, 45, 18, 9],
        [10, 8, 60, 50, 20, 10],
    ]
    
    return medium_scale_instances_matrix

def generate_large_scale_instances_matrix():
    """ generate large scale instances matrix """

    large_scale_instances_matrix = [
        [10, 12, 60, 50, 10, 5],
        [10, 12, 80, 60, 15, 5],
        [10, 12, 100, 70, 20, 5],
        [12, 12, 120, 80, 25, 10],
        [12, 12, 140, 90, 30, 10],
        [12, 12, 160, 100, 35, 10],
        [14, 12, 180, 110, 40, 15],
        [14, 12, 200, 120, 45, 15],
        [14, 12, 220, 130, 50, 15],
    ]
    
    return large_scale_instances_matrix


def generate_RL_instances_matrix():
    """ generate RL instances matrix """

    RL_instances_matrix = [
        [5, 5, 30, 30, 10, 6],
        [6, 6, 40, 40, 15, 7],
        [7, 7, 50, 50, 20, 8],
        [8, 8, 60, 60, 25, 9],
        [9, 9, 70, 70, 30, 11],
    ]
    
    return RL_instances_matrix


def generate_instances(instances_matrix):
    """ input instances matrix, output instances """

    instances = []
    for instance_matrix in instances_matrix:
        each_instance = []
        for i in range(10): # 每类算例的规模为10
            instance = Instance(instance_matrix[0], instance_matrix[1], instance_matrix[2], instance_matrix[3], instance_matrix[4], instance_matrix[5], seed=i)
            each_instance.append(instance)
        instances.append(each_instance)
    
    return instances

