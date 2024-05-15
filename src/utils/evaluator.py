def evaluate_process(tote_status, cache_out_order):
    """
    评估程序输出结果，统计下架、出库、入库和上架的次数。

    :param tote_status: 料箱状态列表，0表示在架上，1表示在暂存区，2表示在缓存池中
    :param cache_out_order: 缓存池出料顺序列表
    :return: 下架、出库、入库和上架的次数
    """
    num_unstack = 0  # 下架次数
    num_checkout = 0  # 出库次数
    num_restock = 0  # 入库次数
    num_stack = 0  # 上架次数

    # 初始化每个料箱的当前状态为0（在架上）
    current_status = tote_status[:]  # 使用原始的tote_status作为当前状态

    # 遍历缓存池出料顺序，统计状态变化
    for sku in cache_out_order:
        if current_status[sku] == 0:
            current_status[sku] = 1 # 料箱现在在暂存区
            num_unstack += 1  # 从0到1，下架
        elif current_status[sku] == 1:
            current_status[sku] = 2  # 从1到2，入库到缓存池
            num_restock += 1
        elif current_status[sku] == 2:
            num_checkout += 1  # 从2到1，出库
            current_status[sku] = 1  # 出库后料箱回到暂存区

    # 在程序结束时，将所有料箱状态重置为0（在架上），统计上架次数
    for i in range(len(current_status)):
        if current_status[i] != 0:
            num_stack += 1  # 从1或2上架回到0
            current_status[i] = 0

    return num_unstack, num_checkout, num_restock, num_stack

# 请注意，您需要根据实际的tote_status和cache_out_order数据来调用此函数。



# 示例：使用提供的程序输出的tote_status和cache_out_order进行评估
# 假设tote_status和cache_out_order是从程序中获取的
#tote_status_example = [0, 1, 2, 0, 1]  # 示例状态列表
#cache_out_order_example = [0, 2, 1, 0, 2]  # 示例出料顺序列表

# 调用评估函数
#unstack, checkout, restock, stack = evaluate_process(tote_status, cache_out_order)

#print(f"下架次数: {unstack}")
#print(f"出库次数: {checkout}")
#print(f"入库次数: {restock}")
#print(f"上架次数: {stack}")