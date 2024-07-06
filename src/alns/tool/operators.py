import copy
import numpy as np
from src.Instance.input_data import read_input_data

class Operator:

    def __init__(self, instance_obj):
        """ operator base class, there are some common methods """
        self.instance_obj = instance_obj
        self.stations_num = instance_obj.station_num

    def safe_change(self, greedy_op_matrix, break_list, repair_list):
        """change the order between break_list and repair_list"""
        for i in range(self.stations_num):
            break_pos = break_list[i]
            repair_pos = repair_list[i]
            temp = greedy_op_matrix[break_pos[0]][break_pos[1]]
            greedy_op_matrix[break_pos[0]][break_pos[1]] = greedy_op_matrix[repair_pos[0]][repair_pos[1]]
            greedy_op_matrix[repair_pos[0]][repair_pos[1]] = temp
        return greedy_op_matrix

    def set(self):
        raise NotImplementedError

class RandomBreak(Operator):
    # 继承父类
    def __init__(self, instance_obj, break_num=1):
        """" random break the solution """
        self.instance_obj = instance_obj
        self.break_num = break_num
        self.order_num = instance_obj.order_num
        self.stations_num = instance_obj.station_num

    def set(self, greedy_op_matrix):
        op_matrix = copy.deepcopy(greedy_op_matrix)
        break_list = [] # [p,o_pos]
        while len(break_list) < self.break_num:
            p = np.random.randint(0, self.stations_num)
            o_pos_break = np.random.randint(0, len(op_matrix[p]))
            if [p, o_pos_break] not in break_list:
                break_list.append([p, o_pos_break])
        return break_list



class RandomRepair(Operator):
    def __init__(self, instance_obj):
        """ random repair the solution """
        super().__init__(instance_obj)
        self.order_num = instance_obj.order_num
        self.stations_num = instance_obj.station_num
        self.stations_buffer_num = instance_obj.station_buffer_num

    def set(self, greedy_op_matrix, break_info_list):
        break_list = break_info_list
        break_num = len(break_list)
        repair_list = []
        for i in range(break_num):
            repair = False
            # 2种repair算子
            choose = np.random.randint(0, 2)
            break_p = break_list[i][0]
            break_p_pos = break_list[i][1]

            while not repair:
                if choose == 0:
                    # 算子1：拣选站内交换，不和当时同时在墙上的订单交换
                    choose_p = break_p
                    p_len = len(greedy_op_matrix[break_p])
                    p_pos = break_list[i][1]
                    p_own = -1
                    o_own = break_p_pos // self.stations_buffer_num
                    while p_pos == break_p_pos or o_own == p_own:
                        p_pos = np.random.randint(0, p_len)
                        p_own = p_pos // self.stations_buffer_num
                else:
                    # 算子2：拣选站间交换，包括和同时在墙和不同时在墙
                    choose_p = break_list[i][0]
                    while choose_p == break_p:
                        choose_p = np.random.randint(0, self.stations_num)
                    p_len = len(greedy_op_matrix[choose_p])
                    p_pos = np.random.randint(0, p_len)

                if [choose_p, p_pos] not in repair_list:
                    repair_list.append([choose_p, p_pos])
                    repair = True

        # repair
        self.safe_change(greedy_op_matrix, break_list, repair_list)
        return greedy_op_matrix
