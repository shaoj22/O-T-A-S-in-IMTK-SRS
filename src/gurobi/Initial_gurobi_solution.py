"hh"
from collections import defaultdict
from src.Instance.input_data import read_input_data
from itertools import groupby
import json

def order_devide(t):
    global station_buffer_num, order_list, station_matrix, station_list, x_op

    for i, station in enumerate(station_list):
        while len(station_matrix[station]) < station_buffer_num:
            if len(order_list) == 0:
                return None
            # x = len(station_matrix[station])
            order = order_list.pop(0)
            station_matrix[station].append(order)
            x_op[order['orderIdx']][i] = 1
            z_ot_p[order['orderIdx']][t][i] = 1

    # 输出拣选站矩阵
    for station in station_list:
        orders_in_station = station_matrix[station]
        print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")
    return None


def process_orders():
    global station_buffer_num, order_list, station_matrix, un_order_list, t, T_list, tote_list

    # 优先考虑最小批时的订单
    process_order = []
    batch = 10000
    for station in station_matrix:
        for order in station_matrix[station]:
            if order['orderIdx'] // (station_buffer_num * num_stations) < batch:
                batch = order['orderIdx'] // (station_buffer_num * num_stations)
    for station in station_matrix:
        for order in station_matrix[station]:
            if order['orderIdx'] // (station_buffer_num * num_stations) == batch:
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
        block_idx = belong_block(sku_process)
        if t < T_list[sku_process]:
            t = T_list[sku_process]
        if tote_status[sku_process] == 0:  # 说明料箱在架上
            # y_it_4[sku_process][t] = 1
            x_itb_1[sku_process][t][block_idx] = 1
            tote_status[sku_process] = 1  # 暂存区
            y_it_2[sku_process][t + 1] = 1
            y_it_4[sku_process][t + 1] = 0  #不在架上
            y_itb_2[sku_process][t + 1][block_idx] = 1
            # 出库 t+1
            x_it_2[sku_process][t + 1] = 1
            t_actual = t + 1
        # else:
        #     print("zancun")
        #     y_it_2[sku_process][t] = 1
        #     y_itb_2[sku_process][t][block_idx] = 1
        #     # 料箱在暂存区 直接出库
        #     block_storage[block_idx].remove(sku)
        #     tote_status[sku] = 2  # 拣选站
        #     x_it_2[sku_process][t] = 1
        #     t_actual = t
        # 记录去了几个拣选站
        delta_t = 0
        remove_order = False
        for i, station in enumerate(station_matrix):
            st = 0
            for order in station_matrix[station]:
                for sku in order['sku']:
                    if sku == sku_process:
                        order['sku'].remove(sku)
                        z_oit_p[order['orderIdx']][sku_process][t_actual][i] = 1
                        x_itp_2[sku_process][t_actual][i] = 1
                        st = 1
            delta_t = delta_t + st
            remove_orders = []
            for order in station_matrix[station].copy():
                if len(order['sku']) == 0:
                    remove_order = True
                    # 记录订单的完成时刻
                    z_ot_p[order['orderIdx']][t_actual][i] = 1
                    remove_orders.append(order)
            for order in remove_orders:
                station_matrix[station].remove(order)
                un_order_list.remove(order)
        for j in range(delta_t):
            y_it_3[sku_process][t_actual + j + 1] = 1
            y_it_4[sku_process][t_actual + j + 1] = 0  # 不在架上
        # 入库
        x_it_3[sku_process][t_actual + delta_t] = 1
        tote_status[sku_process] = 1  # 暂存区
        y_it_2[sku_process][t_actual + delta_t + 1] = 1
        y_itb_2[sku_process][t_actual + delta_t + 1][block_idx] = 1
        y_it_4[sku_process][t_actual + delta_t + 1] = 0  # 不在架上
        # 上架
        for tt in range(t_actual + delta_t + 1, T):
            xibt4 = 0
            for tote in tote_list:
                xibt4 = xibt4 + x_itb_4[tote][tt][block_idx]
            if xibt4 > 0:
                # 继续留在暂存区
                y_it_2[sku_process][tt+1] = 1
                y_itb_2[sku_process][tt+1][block_idx] = 1
                y_it_4[sku_process][tt+1] = 0  # 不在架上
            else:
                x_itb_4[sku_process][tt][block_idx] = 1
                # 上架后状态才可以改变
                T_list[sku_process] = tt + 1
                tote_status[sku_process] = 0  # 架上
                break
        if remove_order:
            # 来一个料箱就需判断是否有订单已完成
            order_devide(t_actual+1)
        t = t + 1
        if t > T - 3 - station_buffer_num:
            print('error')
    return sorted_sku_list


def belong_block(sku):
    global block_list
    for block in block_list:
        if sku in block['sku']:
            block_idx = block['blockIdx']
    return block_idx

def Initial_variables():
    global num_stations, num_totes, num_orders, num_blocks, T
    # x_op
    x_op = []
    for o in range(num_orders):
        x_op.append([])
        for p in range(num_stations):
            x_op[o].append(0)
    # x_itb_1
    x_itb_1 = []
    for i in range(num_totes):
        x_itb_1.append([])
        for t in range(T):
            x_itb_1[i].append([])
            for b in range(num_blocks):
                x_itb_1[i][t].append(0)
    # x_it_2
    x_it_2 = []
    for i in range(num_totes):
        x_it_2.append([])
        for t in range(T):
            x_it_2[i].append(0)
    # x_itp_2
    x_itp_2 = []
    for i in range(num_totes):
        x_itp_2.append([])
        for t in range(T):
            x_itp_2[i].append([])
            for p in range(num_stations):
                x_itp_2[i][t].append(0)
    # x_it_3
    x_it_3 = []
    for i in range(num_totes):
        x_it_3.append([])
        for t in range(T):
            x_it_3[i].append(0)
    # x_itb_4
    x_itb_4 = []
    for i in range(num_totes):
        x_itb_4.append([])
        for t in range(T):
            x_itb_4[i].append([])
            for b in range(num_blocks):
                x_itb_4[i][t].append(0)
    # y_it_2
    y_it_2 = []
    for i in range(num_totes):
        y_it_2.append([])
        for t in range(T):
            y_it_2[i].append(0)
    # y_itb_2
    y_itb_2 = []
    for i in range(num_totes):
        y_itb_2.append([])
        for t in range(T):
            y_itb_2[i].append([])
            for b in range(num_blocks):
                y_itb_2[i][t].append(0)
    # y_it_3
    y_it_3 = []
    for i in range(num_totes):
        y_it_3.append([])
        for t in range(T):
            y_it_3[i].append(0)
    # y_it_4
    y_it_4 = []
    for i in range(num_totes):
        y_it_4.append([])
        for t in range(T):
            y_it_4[i].append(1)
    # z_oit_p
    z_oit_p = []
    for o in range(num_orders):
        z_oit_p.append([])
        for i in range(num_totes):
            z_oit_p[o].append([])
            for t in range(T):
                z_oit_p[o][i].append([])
                for p in range(num_stations):
                    z_oit_p[o][i][t].append(0)
    # z_ot_p
    z_ot_p = []
    for o in range(num_orders):
        z_ot_p.append([])
        for t in range(T):
            z_ot_p[o].append([])
            for p in range(num_stations):
                z_ot_p[o][t].append(0)
    return x_op, x_itb_1, x_it_2, x_itp_2, x_it_3, x_itb_4, y_it_2, y_itb_2, y_it_3, y_it_4, z_oit_p, z_ot_p


if __name__ == "__main__":

    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/Instance-small-1.json"
    instance_obj = read_input_data(input_path)
    order_list = instance_obj.order_list
    un_order_list = order_list.copy()
    co_order_list = order_list.copy()
    # 设置初始状态
    tote_list = instance_obj.tote_list

    station_list = instance_obj.station_list
    block_list = instance_obj.block_list
    station_buffer_num = instance_obj.station_buffer_num
    block_storage_num = instance_obj.block_storage_num
    num_stations = instance_obj.station_num
    num_orders = instance_obj.order_num
    num_totes = len(tote_list)
    num_blocks = len(block_list)
    T = 20

    # 初始化全局变量并调用主函数
    station_buffer = []
    temporary_storage = []
    # block_storage = {blk['blockIdx']: blk['sku'].copy() for blk in block_list}
    tote_status = [0] * len(tote_list)
    cache_out_order = []
    skipped_orders = []

    # 初始化决策变量
    x_op, x_itb_1, x_it_2, x_itp_2, x_it_3, x_itb_4, y_it_2, y_itb_2, y_it_3, y_it_4, z_oit_p, z_ot_p = Initial_variables()

    # 初始化拣选站矩阵，用字典表示，键是拣选站编号，值是订单列表
    station_matrix = {station: [] for station in station_list}
    # 上架时间
    T_list = [0] * len(tote_list)

    # 分配订单到拣选站
    t = 0
    order_devide(t)


    # 调用主函数，得到料箱出库顺序
    or_final_sku_list = []
    while len(un_order_list) != 0:
        sku_list = process_orders()
        for sku in sku_list:
            or_final_sku_list.append(sku)
    # 出库顺序
    final_sku_list = [sku for sku, _ in groupby(or_final_sku_list)]

    #下架、出库、上架顺序和出库一样
    print(f"总次数：", 4 * len(final_sku_list))

    # 订单上墙
    for order in co_order_list:
        for station in station_list:
            if x_op[order['orderIdx']][station] == 1:
                change = 0
                while change < 2:
                    while change < 1:
                        for t in range(T):
                            if z_ot_p[order['orderIdx']][t][station] == 1:
                                change = change + 1
                                t_begin = t
                                break
                    for t in range(t_begin + 1, T):
                        if z_ot_p[order['orderIdx']][t][station] != 1:
                            z_ot_p[order['orderIdx']][t][station] = 1
                        else:
                            change = change + 1
                            break
            else:
                continue

    # 检查订单上墙的正确
    for order in co_order_list:
        for station in station_list:
            for t in range(T):
                zoitp = 0
                for sku in tote_list:
                    zoitp = zoitp + z_oit_p[order['orderIdx']][sku][t][station]
                if zoitp > z_ot_p[order['orderIdx']][t][station]:
                    print('error3')


    # 检查状态和动作的正确（中心约束）
    for sku in tote_list:
        for t in range(T):
            if y_it_2[sku][t] + y_it_3[sku][t] + y_it_4[sku][t] != 1:
                print('error1')
                print(sku, t, y_it_2[sku][t], y_it_3[sku][t], y_it_4[sku][t])
            xitb1 = 0
            xitb4 = 0
            for block in block_list:
                xitb1 = xitb1 + x_itb_1[sku][t][block['blockIdx']]
                xitb4 = xitb4 + x_itb_4[sku][t][block['blockIdx']]
            if xitb1 + xitb4 + x_it_2[sku][t] + x_it_3[sku][t] > 1:
                print('error2', xitb1, xitb4, x_it_2[sku][t], x_it_3[sku][t])

    # 存储结果
    result_info = {
        'x_op': x_op,
        'x_itb_1': x_itb_1,
        'x_it_2': x_it_2,
        'x_itp_2': x_itp_2,
        'x_it_3': x_it_3,
        'x_itb_4': x_itb_4,
        'y_it_2': y_it_2,
        'y_itb_2': y_itb_2,
        'y_it_3': y_it_3,
        'y_it_4': y_it_4,
        'z_oit_p': z_oit_p,
        'z_ot_p': z_ot_p,
    }

    json_data = json.dumps(result_info, indent=4)

    with open('Initial_gurobi.json', 'w') as json_file:
        json_file.write(json_data)


