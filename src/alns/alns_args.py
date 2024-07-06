from src.alns.tool.operators import *

class ALNSArgs:
    def __init__(self, params_info):
        """ alns's args"""
        self.iter_num = params_info['iter_num']
        # 1. ALNS params
        self.adaptive_period = params_info['adaptive_period']
        self.sigma1 = params_info['sigma1']
        self.sigma2 = params_info['sigma2']
        self.sigma3 = params_info['sigma3']
        # 2. SA params
        self.max_temp = params_info['max_temp']
        self.min_temp = params_info['min_temp']
        self.cooling_rate = params_info['cooling_rate']
        self.cooling_period = params_info['cooling_period']
        self.break_operators_list = params_info['break_operators_list']
        self.repair_operators_list = params_info['repair_operators_list']

def get_common_alns_args(instance_obj, operator_num):
    """ get common ALNS args"""
    break_operators_list = []
    repair_operators_list = []
    for i in range(operator_num):
        break_operators_list.append(RandomBreak(instance_obj=instance_obj, break_num=i+1))
        repair_operators_list.append(RandomRepair(instance_obj=instance_obj))
    params_info = {
        "iter_num": 1000,
        "adaptive_period": 1000,
        "sigma1": 2,
        "sigma2": 1,
        "sigma3": 0.1,
        "max_temp": 0.01,
        "min_temp": 1e-10,
        "cooling_rate": 0.97,
        "cooling_period": 30,
        "break_operators_list": break_operators_list,
        "repair_operators_list": repair_operators_list,
    }
    return ALNSArgs(params_info)
