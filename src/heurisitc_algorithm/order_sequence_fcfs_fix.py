from collections import defaultdict
from src.Instance.input_data import read_input_data
from itertools import groupby
import json
from copy import deepcopy


class FCFS:
    def __init__(self, input_path, T):
        self.input_path = input_path
        self.instance_obj = read_input_data(input_path)
        self.T = T
        self.t = 0
        self.init_global_variables()
        self.init_decision_variables()

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
        # block_storage = {blk['blockIdx']: blk['sku'].copy() for blk in block_list}
        self.tote_status = [0] * len(self.tote_list)
        self.cache_out_order = []
        self.skipped_orders = []
        self.station_matrix = {station: [] for station in self.station_list}
        self.T_list = [0] * len(self.tote_list)
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

    def order_devide(self, t):

        for i, station in enumerate(self.station_list):
            while len(self.station_matrix[station]) < self.station_buffer_num:
                if len(self.order_list) == 0:
                    return None
                # x = len(station_matrix[station])
                order = self.order_list.pop(0)
                self.station_matrix[station].append(order)
                self.x_op[order['orderIdx']][i] = 1
                self.z_ot_p[order['orderIdx']][t][i] = 1

        # 输出拣选站矩阵
        for station in self.station_list:
            orders_in_station = self.station_matrix[station]
            print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")
        return None

    def process_orders(self):

        # 优先考虑最小批时的订单
        process_order = []
        batch = 10000
        for station in self.station_matrix:
            for order in self.station_matrix[station]:
                if order['orderIdx'] // (self.station_buffer_num * self.num_stations) < batch:
                    batch = order['orderIdx'] // (self.station_buffer_num * self.num_stations)
        for station in self.station_matrix:
            for order in self.station_matrix[station]:
                if order['orderIdx'] // (self.station_buffer_num * self.num_stations) == batch:
                    process_order.append(order)

        # 最小批时的订单需要的sku_list
        # 统计每个商品编号的出现次数和所属订单编号
        sku_count = defaultdict(list)
        for order in process_order:
            order_idx = order['orderIdx']
            for sku in order['sku']:
                sku_count[sku].append(order_idx)

        # 按照出现次数从高到低、订单编号从小到大排序
        sorted_skus = sorted(sku_count.items(), key=lambda x: (-len(x[1]), min(x[1])))
        # 提取排序后的商品编号
        sorted_sku_list = [sku for sku, _ in sorted_skus]

        for sku_process in sorted_sku_list:
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
                for order in self.station_matrix[station]:
                    if sku_process in order['sku']:
                        order['sku'].remove(sku_process)
                        self.z_oit_p[order['orderIdx']][sku_process][t_actual][i] = 1
                        self.x_itp_2[sku_process][t_actual][i] = 1
                        st = 1
                        for order_other in self.station_matrix[station]:
                            if order['orderIdx'] != order_other['orderIdx']:
                                if sku_process in self.co_order_list[order_other['orderIdx']]['sku']:
                                    self.z_oit_p[order_other['orderIdx']][sku_process][t_actual][i] = 1
                delta_t = delta_t + st
                remove_orders = []
                for order in self.station_matrix[station].copy():
                    if len(order['sku']) == 0:
                        remove_order = True
                        # 记录订单的完成时刻
                        self.z_ot_p[order['orderIdx']][t_actual][i] = 1
                        remove_orders.append(order)
                for order in remove_orders:
                    self.station_matrix[station].remove(order)
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
            if remove_order:
                # 来一个料箱就需判断是否有订单已完成
                self.order_devide(t=t_actual + 1)
            self.t = self.t + 1
            if self.t > self.T - 3 - self.station_buffer_num:
                print('error')
        return sorted_sku_list

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


if "__main__" == __name__:
    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/myRandomInstanceGurobi.json"
    f_initial = FCFS(input_path, T=55)
    # 分配订单到拣选站
    f_initial.order_devide(t=0)
    # 调用主函数，得到料箱出库顺序
    or_final_sku_list = []
    while len(f_initial.un_order_list) != 0:
        sku_list = f_initial.process_orders()
        for sku in sku_list:
            or_final_sku_list.append(sku)
    # 出库顺序
    final_sku_list = [sku for sku, _ in groupby(or_final_sku_list)]
    print(final_sku_list)
    print(or_final_sku_list)
    # 部分约束限制检查
    f_initial.check()
    # 存储决策变量
    f_initial.result_to_file()
    # 顺序
    f_initial.variables_to_sequence()
