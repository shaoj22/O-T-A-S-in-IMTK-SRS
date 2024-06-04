from collections import defaultdict
from src.Instance.input_data import read_input_data
from itertools import groupby
import time


def order_devide():
    global station_buffer_num, order_list, station_matrix, station_list

    for station in station_list:
        while len(station_matrix[station]) < station_buffer_num:
            if len(order_list) == 0:
                return None
            # x = len(station_matrix[station])
            station_matrix[station].append(order_list.pop(0))
    # 输出拣选站矩阵
    for station in station_list:
        orders_in_station = station_matrix[station]
        print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")
    return None


def process_orders():
    global station_buffer_num, order_list, station_matrix, un_order_list

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
        remove_order = False
        for station in station_matrix:
            for order in station_matrix[station]:
                for sku in order['sku']:
                    if sku == sku_process:
                        order['sku'].remove(sku)
            remove_orders = []
            for order in station_matrix[station].copy():
                if len(order['sku']) == 0:
                    remove_order = True
                    remove_orders.append(order)
            for order in remove_orders:
                station_matrix[station].remove(order)
                un_order_list.remove(order)
        if remove_order:
            # 来一个料箱就需判断是否有订单已完成
            order_devide()

    return sorted_sku_list


def belong_block(sku):
    global block_list
    for block in block_list:
        if sku in block['sku']:
            block_idx = block['blockIdx']
    return block_idx






if __name__ == "__main__":
    start_time = time.time()  # 记录开始时间的时间戳
    input_path = "/Users/xiekio/Desktop/研一/组会/毕设/My/O-T-A-S-in-IMTK-SRS/src/Instance/Instance-large-2.json"
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

    # 初始化拣选站矩阵，用字典表示，键是拣选站编号，值是订单列表
    station_matrix = {station: [] for station in station_list}

    # 分配订单到拣选站
    order_devide()


    # 调用主函数，得到料箱出库顺序
    or_final_sku_list = []
    while len(un_order_list) != 0:
        sku_list = process_orders()
        for sku in sku_list:
            or_final_sku_list.append(sku)

    final_sku_list = [sku for sku, _ in groupby(or_final_sku_list)]


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
                if final_sku_list[i+b+1] == sku:
                    block_storage[block_idx].append(sku) # 暂存
                    break
                if b == min_un - 1:
                    block_back[block_idx].append(sku) # 上架
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
    count = 0
    for idx, block_order_list in enumerate(block_result):
        count = count + len(block_order_list)
        print(f"Block {idx} 下架顺序:", block_order_list)
        print(f"Block {idx} 下架次数:", len(block_order_list))

    count = count + len(final_sku_list) * 2
    print("出库顺序和入库顺序:", final_sku_list)
    print("出库和入库次数:", len(final_sku_list), len(final_sku_list))

    for idx, block_order_list in enumerate(block_back):
        count = count + len(block_order_list)
        print(f"Block {idx} 上架顺序:", block_order_list)
        print(f"Block {idx} 上架次数:", len(block_order_list))
    print(f"总次数：", count)
    end_time = time.time()
    print(f"经过时间：{end_time - start_time}秒")


