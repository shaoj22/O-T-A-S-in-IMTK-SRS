from collections import defaultdict
from src.Instance.input_data import read_input_data
import numpy as np

# 计算订单列表中各列表之间的相似度
def similarity_matrix_calculate():
    global order_list
    # 定义记录各订单相似度的矩阵
    Similarity_matrix = np.zeros(shape=(len(order_list), len(order_list)))
    # 求第一波次的前两个订单
    Similarity_max = -1
    initial_round = []
    for i in range(len(order_list)):
        for j in range(len(order_list)):
            if j >= i:
                Similarity_matrix[j][i] = Similarity_matrix[i][j] = similarity_calculate(order_list[i]['sku'], order_list[j]['sku'])
                if i != j:
                    if Similarity_matrix[i][j] > Similarity_max:
                        Similarity_max = Similarity_matrix[i][j]
                        initial_round = [order_list[i], order_list[j]]  # 构建初始波次sku列表
                    else:
                        continue
                else:
                    continue
            else:
                break
    return initial_round

def similarity_calculate(sku_list1, sku_list2):
    # 两个sku列表的sku数总和
    sku_num1 = len(sku_list1) + len(sku_list2)

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
    similarity = sku_num2 / sku_num1
    return similarity

# 合并订单的sku数
def combline_order_sku(order_list):
    sku_list = []  # 存储订单sku的并集
    for order in order_list:
        for sku in order['sku']:
            if sku in sku_list:
                continue
            else:
                sku_list.append(sku)
    return sku_list

# 在订单列表中删除指定订单
def delete_order(order_list1, order_list2):
    for order in order_list2:
        order_list1.remove(order)
    return order_list1

def order_devide():
    global station_buffer_num, order_list, station_matrix, station_list

    for station in station_list:
        while len(station_matrix[station]) < station_buffer_num:
            # x = len(station_matrix[station])
            if len(order_list) == 0:
                return None
            sku_combine = combline_order_sku(station_matrix[station])
            sim = -1
            for order in order_list:
                simlarity = similarity_calculate(order['sku'], sku_combine)
                if simlarity > sim:
                    sim = simlarity
                    order_choose = order
            station_matrix[station].append(order)
            order_list.remove(order)
            # station_matrix[station].append(order_list.pop(0))
    # 输出拣选站矩阵
    for station in station_list:
        orders_in_station = station_matrix[station]
        print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")
    return None


def sku_sevice(sorted_sku_list):
    global final_sku_list
    for sku_process in sorted_sku_list:
        if len(final_sku_list) == 0:
            final_sku_list.append(sku_process)
        else:
            if sku_process != final_sku_list[-1]:
                final_sku_list.append(sku_process)
        for i, station in enumerate(station_matrix):
            for order in station:
                for sku in order['sku']:
                    if sku == sku_process:
                        order['sku'].remove(sku)
                if len(order['sku']) == 0:
                    station_matrix[i].remove(order)
                    un_order_list.remove(order)
                    return None


def process_orders():
    global station_buffer_num, order_list, station_matrix, un_order_list

    process_order = []
    for station in station_matrix:
        for order in station:
            process_order.append(order)

    # 处理订单需要的sku_list
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

    # 料箱到达
    sku_sevice(sorted_sku_list)

    # 有订单已完成需添加订单
    order_devide()

    return None

def belong_block(sku):
    global block_list
    for block in block_list:
        if sku in block['sku']:
            block_idx = block['blockIdx']
    return block_idx

if __name__ == "__main__":

    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/myRandomInstanceGurobi.json"
    instance_obj = read_input_data(input_path)
    order_list = instance_obj.order_list
    un_order_list = order_list.copy()
    # 设置初始状态
    tote_list = instance_obj.tote_list

    station_list = instance_obj.station_list
    block_list = instance_obj.block_list
    station_buffer_num = instance_obj.station_buffer_num
    block_storage_num = instance_obj.block_storage_num
    num_stations = instance_obj.station_num
    num_orders = instance_obj.order_num

    # 初始化全局变量并调用主函数
    station_buffer = []
    temporary_storage = []
    # block_storage = {blk['blockIdx']: blk['sku'].copy() for blk in block_list}
    tote_status = [0] * len(tote_list)
    cache_out_order = []
    skipped_orders = []

    # # 初始化拣选站矩阵，用字典表示，键是拣选站编号，值是订单列表
    # station_matrix = {station: [] for station in station_list}

    # 初始相似度最高的订单
    Initial_orders = similarity_matrix_calculate()

    # 删除第一波次中的订单
    cur_order_list = delete_order(order_list, Initial_orders)

    # 迭代进入拣选站
    station_matrix = [Initial_orders]
    for i in range(num_stations):
        round = station_matrix[i]
        while len(round) < station_buffer_num:
            round_sku_list = combline_order_sku(round)  # 合并波次里订单的sku

            # 计算进入该波次的order
            similarity_max = -1
            order_inter_index = -1
            for order in order_list:
                sim = similarity_calculate(round_sku_list, order['sku'])
                if sim > similarity_max:
                    similarity_max = sim
                    order_inter_index = order['orderIdx']
                else:
                    continue
            for order in order_list:
                if order['orderIdx'] == order_inter_index:
                    round.append(order)  # 在该波次中添加该订单
                    order_list = delete_order(order_list, [order])  # 从剩余订单里删除该订单
                    break
                else:
                    continue
        if i < num_stations - 1:
            cur_initial_round = similarity_matrix_calculate()  # 构建下一个拣选站的初始两个订单
            station_matrix.append(cur_initial_round)  # 在波次列表中添加新波次
            order_list = delete_order(order_list, cur_initial_round)  # 在剩余订单中删除新波次的初始订单


    # 调用主函数，得到料箱出库顺序
    final_sku_list = []
    while len(un_order_list) != 0:
        process_orders()

    # 倒退顺序
    block_result = [[] for _ in range(len(block_list))]  # 每个 Block 的下架顺序列表
    block_back = [[] for _ in range(len(block_list))]  # 每个 Block 的上架顺序列表
    block_storage = {blk['blockIdx']: [] for blk in block_list}  # block中暂存情况

    for i, sku in enumerate(final_sku_list):
        block_idx = belong_block(sku)
        if tote_status[sku] == 0:  # 说明料箱在架上
            block_result[block_idx].append(sku)  # 下架
            tote_status[sku] = 1  # 暂存区
            # 出库
            tote_status[sku] = 2  # 拣选站
            # 入库
            # block_storage[block_idx].append(sku)
            tote_status[sku] = 1  # 暂存区
            un_storage_num = block_storage_num - len(block_storage[block_idx])
            len_un = len(final_sku_list) - i - 1
            min_un = min(un_storage_num, len_un)
            for b in range(min_un):
                if final_sku_list[i + b + 1] == sku:
                    block_storage[block_idx].append(sku) # 暂存
                    break
                if b == min_un - 1:
                    block_back[block_idx].append(sku)  # 上架
                    # block_storage[block_idx].remove(sku)
                    tote_status[sku] = 0  # 说明料箱在架上
        else:
            # 料箱在暂存区 直接出库
            block_storage[block_idx].remove(sku)
            tote_status[sku] = 2  # 拣选站
            # 入库
            tote_status[sku] = 1  # 暂存区
            # block_storage[block_idx].append(sku)
            un_storage_num = block_storage_num - len(block_storage[block_idx])
            len_un = len(final_sku_list) - i - 1
            min_un = min(un_storage_num, len_un)
            for b in range(min_un):
                if final_sku_list[i + b + 1] == sku:
                    block_storage[block_idx].append(sku)  # 暂存
                    break
                if b == un_storage_num - 1:
                    block_back[block_idx].append(sku)  # 上架
                    # block_storage[block_idx].remove(sku)
                    tote_status[sku] = 0  # 说明料箱在架上
    # 强制上架
    for sku in final_sku_list:
        if tote_status[sku] != 0:  # 料箱不在架上
            block_idx = belong_block(sku)
            block_back[block_idx].append(sku)  # 上架
            tote_status[sku] = 0  # 说明料箱在架上

    for idx, block_order_list in enumerate(block_result):
        print(f"Block {idx} 下架顺序:", block_order_list)
        print(f"Block {idx} 下架次数:", len(block_order_list))

    print("出库顺序和入库顺序:", final_sku_list)
    print("出库和入库次数:", len(final_sku_list), len(final_sku_list))

    for idx, block_order_list in enumerate(block_back):
        print(f"Block {idx} 上架顺序:", block_order_list)
        print(f"Block {idx} 上架次数:", len(block_order_list))
    print(f"总次数：", len(block_order_list) + 2 * len(final_sku_list) + len(block_order_list))





