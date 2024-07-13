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
        for i in range(len(break_list)):
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
        super().__init__(instance_obj)
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

class WorstBreak(Operator):
    # 继承父类
    def __init__(self, instance_obj, break_num=1):
        """" Break the solution by worst order"""
        super().__init__(instance_obj)
        self.instance_obj = instance_obj
        self.break_num = break_num
        self.order_num = instance_obj.order_num
        self.stations_num = instance_obj.station_num
        self.order_list = self.instance_obj.order_list

    def similarity_calculate(self, sku_list1, sku_list2):
        # # 两个sku列表的sku数总和
        # sku_num1 = len(sku_list1) + len(sku_list2)

        # 两个sku列表相同sku数
        sku_num2 = 0
        if len(sku_list1) <= len(sku_list2):
            for sku in sku_list1:
                if sku in sku_list2:
                    sku_num2 += 1
                else:
                    continue
        else:
            for sku in sku_list2:
                if sku in sku_list1:
                    sku_num2 += 1
                else:
                    continue

        # 计算相似度
        # similarity = sku_num2 / sku_num1
        return sku_num2

    # 合并订单的sku数
    def combline_order_sku(self, order_idx_list):
        order_list = []
        for idx in order_idx_list:
            order_list.append(self.order_list[idx])
        sku_list = []  # 存储订单sku的并集
        for order in order_list:
            for sku in order['sku']:
                if sku in sku_list:
                    continue
                else:
                    sku_list.append(sku)
        return sku_list
    def set(self, greedy_op_matrix):
        op_matrix = copy.deepcopy(greedy_op_matrix)
        break_list = [] # [p,o_pos]
        while len(break_list) < self.break_num:
            sim_min = 100000
            for p, station in enumerate(op_matrix):
                if len(station) <= 1:
                    break
                else:
                    for i, orderIdx in enumerate(station):
                        order_list_except = station.copy()
                        order_list_except.remove(orderIdx)
                        except_sku = self.combline_order_sku(order_list_except)
                        sim = self.similarity_calculate(self.order_list[orderIdx]['sku'], except_sku)
                        if sim < sim_min:
                            sim_min = sim
                            bk = [p, i]
            if bk not in break_list:
                break_list.append(bk)
            del op_matrix[p][i]
        return break_list

class ShawBreak(Operator):
    # 继承父类
    def __init__(self, instance_obj, break_num=2):
        """" Break the solution by two order have the max similarity """
        super().__init__(instance_obj)
        self.instance_obj = instance_obj
        self.break_num = break_num
        self.order_num = instance_obj.order_num
        self.stations_num = instance_obj.station_num
        self.order_list = self.instance_obj.order_list

    def similarity_calculate(self, sku_list1, sku_list2):

        # 两个sku列表相同sku数
        sku_num2 = 0
        if len(sku_list1) <= len(sku_list2):
            for sku in sku_list1:
                if sku in sku_list2:
                    sku_num2 += 1
                else:
                    continue
        else:
            for sku in sku_list2:
                if sku in sku_list1:
                    sku_num2 += 1
                else:
                    continue
        return sku_num2

    def similarity_matrix_calculate(self, s_order_list):
        # 定义记录各订单相似度的矩阵
        Similarity_matrix = np.zeros(shape=(len(s_order_list), len(s_order_list)))
        # 求第一波次的前两个订单
        Similarity_max = -1
        break_pos = []
        for i, idx in enumerate(s_order_list):
            for j, jdx in enumerate(s_order_list):
                if j >= i:
                    Similarity_matrix[j][i] = Similarity_matrix[i][j] = self.similarity_calculate(self.order_list[idx]['sku'],
                                                                                             self.order_list[jdx]['sku'])
                    if i != j:
                        if Similarity_matrix[i][j] > Similarity_max:
                            Similarity_max = Similarity_matrix[i][j]
                            break_pos = [i, j]  # 构建初始波次sku列表
                        else:
                            continue
                    else:
                        continue
                else:
                    break
        return break_pos, Similarity_max

    def set(self, greedy_op_matrix):
        op_matrix = copy.deepcopy(greedy_op_matrix)
        break_list = [] # [p,o_pos]
        break_list_pos = []
        while len(break_list) < self.break_num:
            sim_max = -1
            for p, station in enumerate(op_matrix):
                if len(station) <= 2:
                    break
                else:
                    break_idx, sim = self.similarity_matrix_calculate(station)
                    if sim > sim_max:
                        break_list_pos = break_idx
                        choose_p = p
            for i, pos in enumerate(break_list_pos):
                bk = [choose_p, pos]
                if bk not in break_list:
                    break_list.append(bk)
                del op_matrix[choose_p][pos - i]
        return break_list

class RandomRepairSame(Operator):
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
            break_p = break_list[i][0]
            break_p_pos = break_list[i][1]

            while not repair:
                # 拣选站内交换
                choose_p = break_p
                p_len = len(greedy_op_matrix[break_p])
                p_pos = break_list[i][1]
                while p_pos == break_p_pos:
                    p_pos = np.random.randint(0, p_len)

                if [choose_p, p_pos] not in repair_list:
                    repair_list.append([choose_p, p_pos])
                    repair = True
        # repair
        op_matrix = self.safe_change(greedy_op_matrix, break_list, repair_list)
        return op_matrix


class RandomRepairDif(Operator):
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
            break_p = break_list[i][0]

            while not repair:
                # 拣选站间交换，包括和同时在墙和不同时在墙
                choose_p = break_list[i][0]
                while choose_p == break_p:
                    choose_p = np.random.randint(0, self.stations_num)
                p_len = len(greedy_op_matrix[choose_p])
                p_pos = np.random.randint(0, p_len)

                if [choose_p, p_pos] not in repair_list:
                    repair_list.append([choose_p, p_pos])
                    repair = True

        # repair
        op_matrix = self.safe_change(greedy_op_matrix, break_list, repair_list)
        return op_matrix

class GreedyRepair(Operator):
    def __init__(self, instance_obj):
        """ random repair the solution """
        super().__init__(instance_obj)
        self.order_num = instance_obj.order_num
        self.stations_num = instance_obj.station_num
        self.stations_buffer_num = instance_obj.station_buffer_num
        self.order_list = self.instance_obj.order_list

    def similarity_calculate(self, sku_list1, sku_list2):
        # # 两个sku列表的sku数总和
        # sku_num1 = len(sku_list1) + len(sku_list2)

        # 两个sku列表相同sku数
        sku_num2 = 0
        if len(sku_list1) <= len(sku_list2):
            for sku in sku_list1:
                if sku in sku_list2:
                    sku_num2 += 1
                else:
                    continue
        else:
            for sku in sku_list2:
                if sku in sku_list1:
                    sku_num2 += 1
                else:
                    continue

        # 计算相似度
        # similarity = sku_num2 / sku_num1
        return sku_num2

    # 合并订单的sku数
    def combline_order_sku(self, order_idx_list):
        order_list = []
        for idx in order_idx_list:
            order_list.append(self.order_list[idx])
        sku_list = []  # 存储订单sku的并集
        for order in order_list:
            for sku in order['sku']:
                if sku in sku_list:
                    continue
                else:
                    sku_list.append(sku)
        return sku_list
    def set(self, greedy_op_matrix, break_info_list):
        break_list = break_info_list
        break_num = len(break_list)
        repair_list = []
        for i in range(break_num):
            repair = False
            sim_max = -1
            while not repair:
                for p, station in enumerate(greedy_op_matrix):
                    if p == break_list[i][0]:
                        continue
                    else:
                        p_order_list = self.combline_order_sku(station)
                        orderIdx = greedy_op_matrix[break_list[i][0]][break_list[i][1]]
                        sim = self.similarity_calculate(self.order_list[orderIdx]['sku'], p_order_list)
                        if sim > sim_max:
                            sim_max = sim
                            choose_p = p
                station = greedy_op_matrix[choose_p]
                sim_min = 10000
                for pos, orderIdx in enumerate(station):
                    orderIdx_ap = greedy_op_matrix[break_list[i][0]][break_list[i][1]]
                    order_list_except = station.copy()
                    order_list_except.remove(orderIdx)
                    order_list_except.append(orderIdx_ap)
                    except_sku = self.combline_order_sku(order_list_except)
                    sim = self.similarity_calculate(self.order_list[orderIdx]['sku'], except_sku)
                    if sim < sim_min and [choose_p, pos] not in repair_list:
                        sim_min = sim
                        bk = [choose_p, pos]
                        repair = True
                repair_list.append(bk)

        # repair
        op_matrix = self.safe_change(greedy_op_matrix, break_list, repair_list)
        return op_matrix

class RegretRepair(Operator):
    def __init__(self, instance_obj):
        """ maximize the  similarity"""
        super().__init__(instance_obj)
        self.order_num = instance_obj.order_num
        self.stations_num = instance_obj.station_num
        self.stations_buffer_num = instance_obj.station_buffer_num
        self.order_list = self.instance_obj.order_list

    def similarity_calculate(self, sku_list1, sku_list2):
        # 两个sku列表相同sku数
        sku_num2 = 0
        if len(sku_list1) <= len(sku_list2):
            for sku in sku_list1:
                if sku in sku_list2:
                    sku_num2 += 1
                else:
                    continue
        else:
            for sku in sku_list2:
                if sku in sku_list1:
                    sku_num2 += 1
                else:
                    continue
        return sku_num2

    # 合并订单的sku数
    def combline_order_sku(self, order_idx_list):
        order_list = []
        for idx in order_idx_list:
            order_list.append(self.order_list[idx])
        sku_list = []  # 存储订单sku的并集
        for order in order_list:
            for sku in order['sku']:
                if sku in sku_list:
                    continue
                else:
                    sku_list.append(sku)
        return sku_list

    def set(self, greedy_op_matrix, break_info_list):
        break_list = break_info_list
        break_num = len(break_list)
        repair_list = []
        for i in range(break_num):
            repair = False
            sim_max = -100000
            while not repair:
                for p, station in enumerate(greedy_op_matrix):
                    if p == break_list[i][0]:
                        continue
                    else:
                        sim_min = 10000
                        for pos, orderIdx in enumerate(station):
                            orderIdx_ap = greedy_op_matrix[break_list[i][0]][break_list[i][1]]
                            order_list_except = station.copy()
                            order_list_except.remove(orderIdx)
                            except_sku = self.combline_order_sku(order_list_except)
                            sim = self.similarity_calculate(self.order_list[orderIdx]['sku'], except_sku)
                            if sim < sim_min and [p, pos] not in repair_list:
                                sim_min = sim
                                bk = [p, pos]
                                final_except_sku = except_sku.copy()
                        sim_after = self.similarity_calculate(self.order_list[orderIdx_ap]['sku'], final_except_sku)
                        sim_diff = sim_after - sim_min
                        if sim_diff > sim_max:
                            sim_max = sim_diff
                            bk_choose = bk
                            repair = True
            repair_list.append(bk_choose)

        # repair
        op_matrix = self.safe_change(greedy_op_matrix, break_list, repair_list)
        return op_matrix