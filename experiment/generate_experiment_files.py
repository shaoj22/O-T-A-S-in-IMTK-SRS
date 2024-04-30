"""
"""



import sys
sys.path.append('..')
from src.instance.generate_random_instance import genRandomInstance

small_scale_experiment_list = [

    [5,5,3],
    [5,10,3],
    [5,15,3],
    [5,20,3],
    [5,25,3],

    [10,10,5],
    [10,15,5],
    [10,20,5],
    [10,25,5],
    [10,30,5],


    [15,15,5],
    [15,20,5],
    [15,25,5],
    [15,30,5],
    [15,35,5],


    [20,20,8],
    [20,25,8],
    [20,30,8],
    [20,35,8],
    [20,40,8],


]

large_scale_experiment_list = [

    [50,60,5],
    [50,70,5],
    [50,80,5],
    [50,90,5],
    [50,100,5],

    [100,100,10],
    [100,120,10],
    [100,140,10],
    [100,160,10],
    [100,180,10],

    
    [150,150,15],
    [150,200,15],
    [150,250,15],
    [150,300,15],
    [150,350,15],

    
    [200,200,20],
    [200,250,20],
    [200,300,20],
    [200,350,20],
    [200,400,20],

]


for i in range(len(small_scale_experiment_list)):
    instance_name = "D:\\Desktop\python_code\\Joint_Optimization_of_Orders_and_Totes_for_WayZim\\experiment\\small_scale_experiment\\myRandomInstanceGurobi" + str(i)
    random_instance = genRandomInstance(order_nums=small_scale_experiment_list[i][0],\
                    tote_nums=small_scale_experiment_list[i][1],\
                    station_nums=small_scale_experiment_list[i][2],\
                    instance_name=instance_name)
    
for i in range(len(large_scale_experiment_list)):
    instance_name = "D:\\Desktop\python_code\\Joint_Optimization_of_Orders_and_Totes_for_WayZim\\experiment\\large_scale_experiment\\myRandomInstance" + str(i)
    random_instance = genRandomInstance(order_nums=large_scale_experiment_list[i][0],\
                    tote_nums=large_scale_experiment_list[i][1],\
                    station_nums=large_scale_experiment_list[i][2],\
                    instance_name=instance_name)