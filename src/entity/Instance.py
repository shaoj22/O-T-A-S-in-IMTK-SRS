class Instance:
    def __init__(self, order_list=None, tote_list=None, station_list=None, block_list=None, station_buffer_num=None, block_storage_num=None, max_T=None):
        self.order_list = order_list  # 订单列表
        self.tote_list = tote_list  # 料箱列表
        self.station_list = station_list  # 工作站列表
        self.block_list = block_list  # 工作站列表
        self.order_num = len(self.order_list)  # 订单数量
        self.tote_num = len(self.tote_list)  # 料箱数量
        self.station_num = len(self.station_list)  # 工作站数量
        self.block_num = len(self.block_list)  # 货架数量
        self.station_buffer_num = station_buffer_num  # 工作站订单缓存数量
        self.block_storage_num = block_storage_num  # block暂存区缓存料箱数量
        self.max_T = max_T
        self.to_matrix_oi = self.gen_tote_and_order_matrix()
        self.to_matrix_ib = self.gen_tote_and_block_matrix()

    def gen_tote_and_order_matrix(self):
        """ generate the tote and order's matrix """
        to_matrix = [[0 for j in range(self.tote_num)] for i in range(self.order_num)]
        for order in self.order_list:
            for sku in order['sku']:
                to_matrix[order['orderIdx']][sku] = 1
        return to_matrix

    def gen_tote_and_block_matrix(self):
        """ generate the tote and block's matrix """
        to_matrix = [[0 for i in range(self.block_num)] for j in range(self.tote_num)]
        for block in self.block_list:
            for sku in block['sku']:
                to_matrix[sku][block['blockIdx']] = 1
        return to_matrix