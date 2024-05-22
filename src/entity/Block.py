class Block:
    def __init__(self, idx=None, sku=None):
        self.idx = idx  # 订单编号
        if sku is None:  # 订单包括的sku列表
            self.sku = []
        else:
            self.sku = sku