def evaluate_process(tote_status, cache_out_order):
    num_unstack = 0    # 下架次数（从架上到暂存区）
    num_checkout = 0   # 出库次数（从缓存池到暂存区或上架）
    num_restock = 0    # 入库次数（从架上或暂存区到缓存池）
    num_stack = 0      # 上架次数（从暂存区回架上）

    # 使用原始的tote_status作为当前状态的起始点
    current_status = tote_status[:]

    # 遍历缓存池出料顺序，统计状态变化
    for sku in cache_out_order:
        if current_status[sku] == 0:  # 料箱在架上
            current_status[sku] = 1  # 下架，状态变为1（暂存区）
            num_unstack += 1
        elif current_status[sku] == 1:  # 料箱在暂存区
            current_status[sku] = 2  # 入库，状态变为2（缓存池）
            num_restock += 1
        elif current_status[sku] == 2:  # 料箱在缓存池
            num_checkout += 1  # 出库，料箱去往暂存区
            current_status[sku] = 1

    # 统计上架次数
    for i, status in enumerate(current_status):
        if status == 1:  # 从暂存区上架
            num_stack += 1
            current_status[i] = 0
        elif status == 2: # 从缓存池直接上架
            num_stack += 1
            num_checkout += 1
            current_status[i] = 0
    return num_unstack, num_checkout, num_restock, num_stack