'''
File: order_sequence_random.py
Project: Joint_Optimization_of_Order_and_Totes_for_WayZim.
Description:
-----------
generate the random init solution of the order sequence.
-----------
Author: 626
Created Date: 2023-1110
'''


import random


class OrderAssignmentRandom:
    def __init__(self, instance):
        """ init the OrderAssignmentRandom """
        self.instance = instance
        self.order_num = self.instance.order_num
        self.order_assignment_solution = self.assign()

    def assign(self):
        """ assign order to station """
        order_list = [] # order's idx list 
        for order in range(self.order_num):
            order_list.append(self.instance.order_list[order]['orderIdx'])
        # random change the order_list idx
        random.shuffle(order_list)
        return self.split_list(order_list, self.instance.station_num)

    def split_list(self, lst, n):
        """ random split the order into each station """
        # 计算每份的基本长度
        base_length = len(lst) // n
        # 计算余数
        remainder = len(lst) % n
        result = []
        start = 0
        # 遍历每份
        for i in range(n):
            # 计算当前份的长度
            length = base_length + 1 if i < remainder else base_length
            # 获取当前份的元素
            sublist = lst[start:start+length]
            # 将当前份添加到结果中
            result.append(sublist)
            # 更新下一份的起始位置
            start += length
        return result