'''
Author: shaoj22 935619774@qq.com
Date: 2024-05-10 10:37:19
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-05-16 09:49:59
FilePath: \Meituan-INFORMS-TSL-Research-Challenge\pdp_module\alns\operators.py
Description: .
'''


import copy
import numpy as np


class Operator:
    def __init__(self, instance):
        """ operator base class, there are some common methods """
        self.instance = instance
    
    def safe_insert(self, sequence, pos, item):
        """ insert item into sequence at position pos, maintaining order """
        if pos == len(sequence):
            sequence.append(item)
        else:
            sequence.insert(pos, item)

    def set(self):
        raise NotImplementedError


class RandomBreak(Operator):
    # 继承父类
    def __init__(self, instance, break_num=1):
        """" random break the solution """
        self.instance = instance
        self.order_num = instance.order_num
        self.courier_num = instance.courier_num
        self.break_num = break_num

    def set(self, solution):
        routes = copy.deepcopy(solution)
        break_p_list = []
        break_d_list = []
        cur_break_num = 0
        while cur_break_num < self.break_num:
            c = np.random.randint(0, self.courier_num)
            p_list = [p for p in routes[c] if p < self.order_num]
            if len(p_list) == 0:
                continue
            p_break = np.random.choice(p_list)
            d_break = p_break + self.order_num
            routes[c].remove(p_break)
            routes[c].remove(d_break)
            break_p_list.append(p_break)
            break_d_list.append(d_break)
            cur_break_num += 1
        break_info = {
            "break_p_list": break_p_list,
            "break_d_list": break_d_list
        }

        return break_info


class RandomRepair(Operator):
    def __init__(self, instance):
        """ random repair the solution """
        super().__init__(instance)
        self.order_num = instance.order_num
        self.courier_num = instance.courier_num

    def set(self, solution, break_info):
        break_p_list, break_d_list = break_info["break_p_list"], break_info["break_d_list"]
        break_num = len(break_p_list)
        for i in range(break_num):
            p_break = break_p_list[i]
            d_break = break_d_list[i]
            # random get one courier.
            c = np.random.randint(0, self.courier_num)
            # random choice one position for p.
            pos_p = np.random.randint(1, len(solution[c])+1)
            # safe insert the order's p into the courier's route.
            self.safe_insert(solution[c], pos_p, d_break)
            # random choice one position for d.
            pos_d = np.random.randint(pos_p, len(solution[c])+1)
            # safe insert the order's d into the courier's route.
            self.safe_insert(solution[c], pos_d, p_break)