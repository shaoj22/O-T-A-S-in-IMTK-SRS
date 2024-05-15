from collections import defaultdict
from collections import Counter
from src.utils.evaluator import evaluate_process
from src.Instance.input_data import read_input_data
input_path= "/Users/macbookpro/PycharmProjects/O-T-A-S-in-IMTK-SRS/src/Instance/myRandomInstanceGurobi.json"
instance_obj = read_input_data(input_path)
order_list = instance_obj.order_list
tote_list=instance_obj.tote_list
station_list=instance_obj.station_list
block_list=instance_obj.block_list
station_buffer_num=instance_obj.station_buffer_num
block_storage_num=instance_obj.block_storage_num

# 初始化全局变量并调用主函数
station_buffer = []
temporary_storage = []
block_storage = {blk['blockIdx']: blk['sku'].copy() for blk in block_list}
tote_status = [0] * len(tote_list)
cache_out_order = []
skipped_orders = []
# 缓存池和暂存区初始化
station_buffer = []  # 缓存池
block_storage = {i: [] for i in range(block_storage_num)}  # 暂存区 Block

num_stations = len(station_list)
num_orders = len(order_list)

# 初始化拣选站矩阵，用字典表示，键是拣选站编号，值是订单列表
station_matrix = {station: [] for station in station_list}

# 分配订单到拣选站
for i, order in enumerate(order_list):
    order_idx = order['orderIdx']
    station_idx = station_list[order_idx % num_stations]  # 计算订单应该分配到的拣选站
    station_matrix[station_idx].append(order_idx)
# 输出拣选站矩阵
for station in station_list:
    orders_in_station = station_matrix[station]
    print(f"拣选站 {station} 目前处理的订单：{orders_in_station}")

# 输出排序结果列表（仅包含商品编号）
#print("按照出现次数和订单编号排序的商品编号列表：")
#print(sorted_sku_list)
def process_orders(order_list):
    global station_buffer, temporary_storage, block_storage, tote_status, block_order, cache_out_order, skipped_orders

    for i in range(0, len(order_list), 5):
        future_orders = order_list[i:i+5]
        process_order_group(future_orders)

    # 处理完所有订单后，继续处理被跳过的订单
    while skipped_orders:
        order_idx = skipped_orders.pop(0)
        handle_order(order_list[order_idx])

    # 按照料箱出缓存池的顺序确定每个料箱属于哪个 Block，并将每个 Block 的下架顺序存储到结果列表中
    block_result = [[] for _ in range(len(block_list))]  # 每个 Block 的下架顺序列表
    for sku in cache_out_order:
        for block in block_list:
            if sku in block['sku']:
                block_idx = block['blockIdx']
                block_result[block_idx].append(sku)
                break
        for i in range(len(tote_list)):
            if tote_status[i] != 0:
                tote_status[i] = 0  # 更新状态为0，即强制上架
    return cache_out_order, block_result
def process_order_group(orders):
    global station_buffer, temporary_storage, block_storage, tote_status, block_order, cache_out_order, skipped_orders
    # 统计每个商品编号的出现次数和所属订单编号
    sku_count = defaultdict(list)
    for order in order_list:
        order_idx = order['orderIdx']
        for sku in order['sku']:
            sku_count[sku].append(order_idx)

    # 按照出现次数从高到低、订单编号从小到大排序
    sorted_skus = sorted(sku_count.items(), key=lambda x: (-len(x[1]), min(x[1])))
    # 提取排序后的商品编号
    sorted_sku_list = [sku for sku, _ in sorted_skus]

    for sku in sorted_sku_list:
        if tote_status[sku] == 0:  # 确保料箱在架上
            tote_status[sku] = 1
            station_buffer.append(sku)
            tote_status[sku] = 2  # 更新状态为在缓存池中
    while station_buffer:
        sku = station_buffer.pop(0)  # 从缓存池的前端弹出
        cache_out_order.append(sku)
        tote_status[sku] = 1
        if sku in block_storage:
            blockIdx = next(idx for idx, block in block_storage.items() if sku in block_storage[idx])
            block_storage[blockIdx].append(sku)
            if not block_storage[blockIdx]:
                del block_storage[blockIdx]

        tote_status[sku] =0 # 更新状态为在架上
    for order in orders:
        order_idx = order['orderIdx']
        #can_process_order = True

        for sku in order['sku']:
            if tote_status[sku] != 0:  # 如果料箱不在架上
                skipped_orders.append(order_idx)
                print(f"订单 {order_idx} 中的料箱 {sku} 不在架上，跳过此料箱。")
                can_process_order = False
            elif tote_status[sku] == 0:
                tote_status[sku] = 1
                can_process_order = True
                station_buffer.append(sku)  # 将料箱移动到缓存池
                tote_status[sku] = 2  # 更新状态为在缓存池中
        if can_process_order:
            print(f"处理订单 {order_idx}中的料箱")
            # 处理满的缓存池
    if len(station_buffer) > station_buffer_num:
         move_to_temporary_storage()
def move_to_temporary_storage():
    global station_buffer, temporary_storage, block_storage, tote_status

    future_demand = determine_future_demand()
    while len(station_buffer) > station_buffer_num:
        sku_to_move = determine_sku_to_move(station_buffer, future_demand)
        station_buffer.remove(sku_to_move)

        if len(temporary_storage) < block_storage_num:
            temporary_storage.append(sku_to_move)
            tote_status[sku_to_move] = 1  # 更新状态为在暂存区中
        else:
            block_idx = determine_block_idx(sku_to_move)
            if block_idx is not None:
                block_storage[block_idx].append(sku_to_move)
                tote_status[sku_to_move] = 0  # 更新状态为在架上
def handle_order(order):
    global skipped_orders

    print(f"处理订单 {order['orderIdx']}")
    # 可以在这里添加处理订单的其他逻辑

    # 检查是否有被跳过的订单中所有料箱已经在架上的订单
    new_skipped_orders = []
    for idx in skipped_orders:
        if all(tote_status[sku] == 0 for sku in order_list[idx]['sku']):
            new_skipped_orders.append(idx)  # 将可以重新处理的订单加入新的列表
        else:
            new_skipped_orders.append(idx)  # 无法处理的订单仍然加入新的列表

    skipped_orders = new_skipped_orders  # 更新被跳过的订单列表

def determine_future_demand():
    future_demand = Counter()
    for order in order_list:
        for sku in order['sku']:
            future_demand[sku] += 1
    return future_demand

def determine_sku_to_move(station_buffer, future_demand):
    sku_to_move = None
    earliest_sku = station_buffer[0]
    for sku in station_buffer:
        if future_demand[sku] == 0:
            return sku
        if station_buffer.index(sku) < station_buffer.index(earliest_sku):
            earliest_sku = sku
    return earliest_sku

def determine_block_idx(sku):
    for block in block_list:
        if sku in block['sku']:
            return block['blockIdx']
    return None

# 初始化全局变量并调用主函数
station_buffer = []
temporary_storage = []
block_storage = {blk['blockIdx']: blk['sku'].copy() for blk in block_list}
tote_status = [0] * len(tote_list)
cache_out_order = []
skipped_orders = []

# 调用主函数
cache_out_result, block_result = process_orders(order_list)
print("缓存池出料顺序:", cache_out_result)

print("Block 出料顺序:")
for idx, block_order_list in enumerate(block_result):
    print(f"Block {idx} 下架顺序:", block_order_list)
# 确保所有料箱的状态都回到了0
assert all(status == 0 for status in tote_status), "所有料箱应最终在架上"
# 调用评估函数
unstack, checkout, restock, stack = evaluate_process(tote_status, cache_out_order)

print(f"下架次数: {unstack}")
print(f"出库次数: {checkout}")
print(f"入库次数: {restock}")
print(f"上架次数: {stack}")