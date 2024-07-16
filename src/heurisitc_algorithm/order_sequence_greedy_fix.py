from collections import defaultdict
from src.Instance.input_data import read_input_data
import numpy as np
import time
import json
from copy import deepcopy

class GREEDY:
    def __init__(self, input_path, T):
        self.input_path = input_path
        self.instance_obj = read_input_data(input_path)
        self.T = T
        self.t = 0
        self.init_global_variables()
        self.init_decision_variables()
        self.station_matrix_gen()

    def init_global_variables(self):
        self.order_list = self.instance_obj.order_list
        self.un_order_list = self.order_list.copy()
        self.co_order_list = deepcopy(self.order_list)
        self.tote_list = self.instance_obj.tote_list
        self.station_list = self.instance_obj.station_list
        self.block_list = self.instance_obj.block_list
        self.station_buffer_num = self.instance_obj.station_buffer_num
        self.num_stations = self.instance_obj.station_num
        self.num_orders = self.instance_obj.order_num
        self.num_totes = len(self.tote_list)
        self.num_blocks = len(self.block_list)
        self.station_buffer = []
        self.temporary_storage = []
        self.tote_status = [0] * len(self.tote_list)
        self.cache_out_order = []
        self.skipped_orders = []
        self.T_list = [0] * len(self.tote_list)
        self.final_sku_list = []
        pass

    def init_decision_variables(self):
        # x_op
        self.x_op = []
        for o in range(self.num_orders):
            self.x_op.append([])
            for p in range(self.num_stations):
                self.x_op[o].append(0)
        # x_itb_1
        self.x_itb_1 = []
        for i in range(self.num_totes):
            self.x_itb_1.append([])
            for t in range(self.T):
                self.x_itb_1[i].append([])
                for b in range(self.num_blocks):
                    self.x_itb_1[i][t].append(0)
        # x_it_2
        self.x_it_2 = []
        for i in range(self.num_totes):
            self.x_it_2.append([])
            for t in range(self.T):
                self.x_it_2[i].append(0)
        # x_itp_2
        self.x_itp_2 = []
        for i in range(self.num_totes):
            self.x_itp_2.append([])
            for t in range(self.T):
                self.x_itp_2[i].append([])
                for p in range(self.num_stations):
                    self.x_itp_2[i][t].append(0)
        # x_it_3
        self.x_it_3 = []
        for i in range(self.num_totes):
            self.x_it_3.append([])
            for t in range(self.T):
                self.x_it_3[i].append(0)
        # x_itb_4
        self.x_itb_4 = []
        for i in range(self.num_totes):
            self.x_itb_4.append([])
            for t in range(self.T):
                self.x_itb_4[i].append([])
                for b in range(self.num_blocks):
                    self.x_itb_4[i][t].append(0)
        # y_it_2
        self.y_it_2 = []
        for i in range(self.num_totes):
            self.y_it_2.append([])
            for t in range(self.T):
                self.y_it_2[i].append(0)
        # y_itb_2
        self.y_itb_2 = []
        for i in range(self.num_totes):
            self.y_itb_2.append([])
            for t in range(self.T):
                self.y_itb_2[i].append([])
                for b in range(self.num_blocks):
                    self.y_itb_2[i][t].append(0)
        # y_it_3
        self.y_it_3 = []
        for i in range(self.num_totes):
            self.y_it_3.append([])
            for t in range(self.T):
                self.y_it_3[i].append(0)
        # y_it_4
        self.y_it_4 = []
        for i in range(self.num_totes):
            self.y_it_4.append([])
            for t in range(self.T):
                self.y_it_4[i].append(1)
        # z_oit_p
        self.z_oit_p = []
        for o in range(self.num_orders):
            self.z_oit_p.append([])
            for i in range(self.num_totes):
                self.z_oit_p[o].append([])
                for t in range(self.T):
                    self.z_oit_p[o][i].append([])
                    for p in range(self.num_stations):
                        self.z_oit_p[o][i][t].append(0)
        # z_ot_p
        self.z_ot_p = []
        for o in range(self.num_orders):
            self.z_ot_p.append([])
            for t in range(self.T):
                self.z_ot_p[o].append([])
                for p in range(self.num_stations):
                    self.z_ot_p[o][t].append(0)

    def station_matrix_gen(self):
        # 初始相似度最高的订单
        Initial_orders = self.similarity_matrix_calculate()
        # 删除第一波次中的订单
        self.delete_order(Initial_orders)

        # 迭代进入拣选站
        self.station_matrix = [Initial_orders]
        self.station_order_list = [order for order in Initial_orders]
        for i in range(self.num_stations):
            round = self.station_matrix[i]
            while len(round) < self.station_buffer_num:
                if len(self.order_list) == 0:
                    break
                round_sku_list = self.combline_order_sku()  # 合并拣选站里订单的sku

                # 计算进入拣选站的order
                similarity_max = -1
                order_inter_index = -1
                for order in self.order_list:
                    sim = self.similarity_calculate(round_sku_list, order['sku'])
                    if sim > similarity_max:
                        similarity_max = sim
                        order_inter_index = order['orderIdx']
                    else:
                        continue
                for order in self.order_list:
                    if order['orderIdx'] == order_inter_index:
                        self.station_order_list.append(order)  # 拣选站处理订单
                        round.append(order)  # 在该波次中添加该订单
                        self.delete_order([order])  # 从剩余订单里删除该订单
                        break
                    else:
                        continue
            if i < self.num_stations - 1:
                cur_initial_round = []  # 构建下一个拣选站的订单list
                self.station_matrix.append(cur_initial_round)  # 在波次列表中添加新波次
        # 初始订单指派情况
        for i, station in enumerate(self.station_matrix):
            for o in station:
                self.x_op[o['orderIdx']][i] = 1
                self.z_ot_p[o['orderIdx']][self.t][i] = 1


    def similarity_matrix_calculate(self):
        # 定义记录各订单相似度的矩阵
        Similarity_matrix = np.zeros(shape=(len(self.order_list), len(self.order_list)))
        # 求第一波次的前两个订单
        Similarity_max = -1
        initial_round = []
        for i in range(len(self.order_list)):
            for j in range(len(self.order_list)):
                if j >= i:
                    Similarity_matrix[j][i] = Similarity_matrix[i][j] = self.similarity_calculate(self.order_list[i]['sku'],
                                                                                             self.order_list[j]['sku'])
                    if i != j:
                        if Similarity_matrix[i][j] > Similarity_max:
                            Similarity_max = Similarity_matrix[i][j]
                            initial_round = [self.order_list[i], self.order_list[j]]  # 构建初始波次sku列表
                        else:
                            continue
                    else:
                        continue
                else:
                    break
        return initial_round

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
    def combline_order_sku(self):
        sku_list = []  # 存储订单sku的并集
        for order in self.station_order_list:
            for sku in order['sku']:
                if sku in sku_list:
                    continue
                else:
                    sku_list.append(sku)
        return sku_list

    # 在订单列表中删除指定订单
    def delete_order(self, order_list2):
        for order in order_list2:
            self.order_list.remove(order)
        pass

    def order_devide(self, t):

        for station in self.station_list:
            while len(self.station_matrix[station]) < self.station_buffer_num:
                # x = len(station_matrix[station])
                if len(self.order_list) == 0:
                    return None
                sku_combine = self.combline_order_sku()
                sim = -1
                for order in self.order_list:
                    simlarity = self.similarity_calculate(order['sku'], sku_combine)
                    if simlarity > sim:
                        sim = simlarity
                        order_choose = order
                self.station_order_list.append(order_choose)
                self.station_matrix[station].append(order_choose)
                self.order_list.remove(order_choose)
                self.x_op[order_choose['orderIdx']][station] = 1
                self.z_ot_p[order_choose['orderIdx']][t][station] = 1
                # station_matrix[station].append(order_list.pop(0))
        return None

    def sku_sevice(self, sorted_sku_list):
        for sku_process in sorted_sku_list:
            self.final_sku_list.append(sku_process)
            # if len(self.final_sku_list) == 0:
            #     self.final_sku_list.append(sku_process)
            # else:
            #     if sku_process != self.final_sku_list[-1]:
            #         self.final_sku_list.append(sku_process)
            block_idx = self.belong_block(sku_process)
            if self.t < self.T_list[sku_process]:
                self.t = self.T_list[sku_process]
            if self.tote_status[sku_process] == 0:  # 说明料箱在架上
                # y_it_4[sku_process][t] = 1
                self.x_itb_1[sku_process][self.t][block_idx] = 1
                self.tote_status[sku_process] = 1  # 暂存区
                self.y_it_2[sku_process][self.t + 1] = 1
                self.y_it_4[sku_process][self.t + 1] = 0  # 不在架上
                self.y_itb_2[sku_process][self.t + 1][block_idx] = 1
                # 出库 t+1
                self.x_it_2[sku_process][self.t + 1] = 1
                t_actual = self.t + 1
            # 记录去了几个拣选站
            delta_t = 0
            remove_order = False
            for i, station in enumerate(self.station_matrix):
                st = 0
                for order in station:
                    if sku_process in order['sku']:
                        order['sku'].remove(sku_process)
                        self.z_oit_p[order['orderIdx']][sku_process][t_actual][i] = 1
                        self.x_itp_2[sku_process][t_actual][i] = 1
                        st = 1
                        for order_other in station:
                            if order['orderIdx'] != order_other['orderIdx']:
                                if sku_process in self.co_order_list[order_other['orderIdx']]['sku']:
                                    self.z_oit_p[order_other['orderIdx']][sku_process][t_actual][i] = 1
                delta_t = delta_t + st
                remove_orders = []
                for order in self.station_matrix[i].copy():  # 使用.copy()复制列表进行迭代，避免在迭代中修改原列表
                    if len(order['sku']) == 0:
                        # 记录订单的完成时刻
                        self.z_ot_p[order['orderIdx']][t_actual][i] = 1
                        remove_orders.append(order)
                        remove_order = True
                # 从各个列表中移除待移除的订单
                for order in remove_orders:
                    self.station_matrix[i].remove(order)
                    self.station_order_list.remove(order)
                    self.un_order_list.remove(order)
            for j in range(delta_t):
                self.y_it_3[sku_process][t_actual + j + 1] = 1
                self.y_it_4[sku_process][t_actual + j + 1] = 0  # 不在架上
            # 入库
            self.x_it_3[sku_process][t_actual + delta_t] = 1
            self.tote_status[sku_process] = 1  # 暂存区
            self.y_it_2[sku_process][t_actual + delta_t + 1] = 1
            self.y_itb_2[sku_process][t_actual + delta_t + 1][block_idx] = 1
            self.y_it_4[sku_process][t_actual + delta_t + 1] = 0  # 不在架上
            # 上架
            for tt in range(t_actual + delta_t + 1, self.T):
                xibt4 = 0
                for tote in self.tote_list:
                    xibt4 = xibt4 + self.x_itb_4[tote][tt][block_idx]
                if xibt4 > 0:
                    # 继续留在暂存区
                    self.y_it_2[sku_process][tt + 1] = 1
                    self.y_itb_2[sku_process][tt + 1][block_idx] = 1
                    self.y_it_4[sku_process][tt + 1] = 0  # 不在架上
                else:
                    self.x_itb_4[sku_process][tt][block_idx] = 1
                    # 上架后状态才可以改变
                    self.T_list[sku_process] = tt + 1
                    self.tote_status[sku_process] = 0  # 架上
                    break
            self.t = self.t + 1
            if self.t > self.T - 3 - self.station_buffer_num:
                print('error')
            if remove_order:
                return t_actual

    def process_orders(self):

        # 处理订单需要的sku_list
        # 统计每个商品编号的出现次数和所属订单编号
        sku_count = defaultdict(list)
        for order in self.station_order_list:
            order_idx = order['orderIdx']
            for sku in order['sku']:
                sku_count[sku].append(order_idx)

        # 按照出现次数从高到低、订单编号从小到大排序
        sorted_skus = sorted(sku_count.items(), key=lambda x: (-len(x[1]), min(x[1])))
        # 提取排序后的商品编号
        sorted_sku_list = [sku for sku, _ in sorted_skus]

        if len(sorted_sku_list) != 0:
            # 料箱到达
            t_actual = self.sku_sevice(sorted_sku_list)
        if len(self.order_list) != 0:
            # 有订单已完成需添加订单
            self.order_devide(t=t_actual+1)

        return None

    def belong_block(self, sku):
        for block in self.block_list:
            if sku in block['sku']:
                block_idx = block['blockIdx']
        return block_idx

    def check(self):
        # 订单上墙
        for order in self.co_order_list:
            for station in self.station_list:
                if self.x_op[order['orderIdx']][station] == 1:
                    change = 0
                    while change < 2:
                        while change < 1:
                            for t in range(self.T):
                                if self.z_ot_p[order['orderIdx']][t][station] == 1:
                                    change = change + 1
                                    t_begin = t
                                    break
                        for t in range(t_begin + 1, self.T):
                            if self.z_ot_p[order['orderIdx']][t][station] != 1:
                                self.z_ot_p[order['orderIdx']][t][station] = 1
                            else:
                                change = change + 1
                                break
                else:
                    continue

        # 检查订单上墙的正确
        for order in self.co_order_list:
            for station in self.station_list:
                for t in range(self.T):
                    zoitp = 0
                    for sku in self.tote_list:
                        zoitp = zoitp + self.z_oit_p[order['orderIdx']][sku][t][station]
                    if zoitp > self.z_ot_p[order['orderIdx']][t][station]:
                        print('error3')

        # 检查状态和动作的正确（中心约束）
        for sku in self.tote_list:
            for t in range(self.T):
                if self.y_it_2[sku][t] + self.y_it_3[sku][t] + self.y_it_4[sku][t] != 1:
                    print('error1')
                    print(sku, t, self.y_it_2[sku][t], self.y_it_3[sku][t], self.y_it_4[sku][t])
                xitb1 = 0
                xitb4 = 0
                for block in self.block_list:
                    xitb1 = xitb1 + self.x_itb_1[sku][t][block['blockIdx']]
                    xitb4 = xitb4 + self.x_itb_4[sku][t][block['blockIdx']]
                if xitb1 + xitb4 + self.x_it_2[sku][t] + self.x_it_3[sku][t] > 1:
                    print('error2', xitb1, xitb4, self.x_it_2[sku][t], self.x_it_3[sku][t])

        # 检验订单完成
        for order in self.co_order_list:
            for station in self.station_list:
                for t in range(self.T):
                    for sku in self.tote_list:
                        if sku in order['sku']:
                            a_oi = 1
                        else:
                            a_oi = 0
                        if self.x_itp_2[sku][t][station] + self.z_ot_p[order['orderIdx']][t][station] + a_oi - 2 > \
                                self.z_oit_p[order['orderIdx']][sku][t][station]:
                            print('err', self.x_itp_2[sku][t][station], self.z_ot_p[order['orderIdx']][t][station], a_oi,
                                  self.z_oit_p[order['orderIdx']][sku][t][station], sku)
                        if self.x_itp_2[sku][t][station] < self.z_oit_p[order['orderIdx']][sku][t][station]:
                            print('err2', self.x_itp_2[sku][t][station], self.z_oit_p[order['orderIdx']][sku][t][station], sku)

    def result_to_file(self):
        # 存储结果
        result_info = {
            'x_op': self.x_op,
            'x_itb_1': self.x_itb_1,
            'x_it_2': self.x_it_2,
            'x_itp_2': self.x_itp_2,
            'x_it_3': self.x_it_3,
            'x_itb_4': self.x_itb_4,
            'y_it_2': self.y_it_2,
            'y_itb_2': self.y_itb_2,
            'y_it_3': self.y_it_3,
            'y_it_4': self.y_it_4,
            'z_oit_p': self.z_oit_p,
            'z_ot_p': self.z_ot_p,
        }

        json_data = json.dumps(result_info, indent=4)

        with open('/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/gurobi/Initial_gurobi.json', 'w') as json_file:
            json_file.write(json_data)

    def variables_to_sequence(self):
        # 订单指派情况
        greedy_op_matrix = []
        for p in range(self.num_stations):
            greedy_op_matrix.append([])
        for o in range(self.num_orders):
            for p in range(self.num_stations):
                if self.x_op[o][p] == 1:
                    greedy_op_matrix[p].append(o)
        for p in range(self.num_stations):
            print(f"拣选站{p}：{greedy_op_matrix[p]}")
        # 下架顺序
        down = [[] for block in self.block_list]
        # 上架顺序
        up = [[] for block in self.block_list]
        for block in self.block_list:
            for t in range(self.T):
                for sku in self.tote_list:
                    if self.x_itb_1[sku][t][block['blockIdx']] == 1:
                        down[block['blockIdx']].append(sku)
                    if self.x_itb_4[sku][t][block['blockIdx']] == 1:
                        up[block['blockIdx']].append(sku)
        # 出库顺序
        out_storage = []
        # 入库顺序
        in_storage = []
        for t in range(self.T):
            for sku in self.tote_list:
                if self.x_it_2[sku][t] == 1:
                    out_storage.append(sku)
                if self.x_it_3[sku][t] == 1:
                    in_storage.append(sku)
        # print(f"下架顺序：", down)
        # print(f"出库顺序：", out_storage)
        # print(f"入库顺序：", in_storage)
        # print(f"上架顺序：", up)
        # 计算次数
        len_down = 0
        up_down = 0
        for block in self.block_list:
            len_down = len_down + len(down[block['blockIdx']])
            up_down = up_down + len(up[block['blockIdx']])
        total = len_down + up_down + len(out_storage) + len(in_storage)
        # print(f"总次数：", total)
        return total

if __name__ == "__main__":
    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/myRandomInstanceGurobi.json"
    start = time.time()
    g_initial = GREEDY(input_path, T=50)
    # 调用主函数，得到料箱出库顺序
    while len(g_initial.un_order_list) != 0:
        # 输出拣选站矩阵
        for station in g_initial.station_list:
            orders_in_station = g_initial.station_matrix[station]
            print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")
        g_initial.process_orders()
    # print("出库顺序和入库顺序:", g_initial.final_sku_list)
    # 部分约束限制检查
    end = time.time()
    print("时长；", end - start)
    g_initial.check()
    # 存储决策变量
    g_initial.result_to_file()
    # 顺序
    g_initial.variables_to_sequence()
