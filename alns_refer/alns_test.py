'''
Author: shaoj22 935619774@qq.com
Date: 2024-05-10 10:41:17
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-05-15 21:20:29
FilePath: \Meituan-INFORMS-TSL-Research-Challenge\pdp_module\test.py
Description: alns test.
'''


import sys
sys.path.append("..")
from pdp_module.data.input_alns_data import input_alns_data
from pdp_module.alns.alns_main import ALNS
from pdp_module.alns_args import get_common_alns_args


instance = input_alns_data('../data/input.json')
alns_args = get_common_alns_args(instance=instance)
alns_algorithm = ALNS(instance, alns_args=alns_args)
best_solution, best_obj = alns_algorithm.run()