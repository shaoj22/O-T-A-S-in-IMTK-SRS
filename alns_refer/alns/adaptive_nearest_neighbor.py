'''
Author: shaoj22 935619774@qq.com
Date: 2024-05-10 20:56:21
LastEditors: shaoj22 935619774@qq.com
LastEditTime: 2024-05-15 16:25:33
FilePath: \Meituan-INFORMS-TSL-Research-Challenge\pdp_module\alns\adaptive_nearest_neighbor.py
Description: adaptive_nearest_neighbor for pdptw's initial solution.
'''


class AdaptiveNearestNeighbor:
    def __init__(self, instance):
        """ adaptive_nearest_neighbor for pdptw's initial solution.

        Args:
            instance (class): instance of pdptw.
        
        Return:
            solution ([[]]): initial solution.
          
        """
        self.order_num = instance.order_num
        self.courier_num = instance.courier_num
        self.node_num = instance.node_num
        self.capacity = instance.capacity
        self.distance_matrix = instance.distance_matrix

    def main(self):
        """ main adaptive_nearest_neighbor """
        # initialize the solution
        solution = [[] for i in range(self.courier_num)]
        # add courier's depot to each courier's solution
        for c in range(self.courier_num):
            solution[c].append(2*self.order_num+c)
        # finished order's num and unfinished order's list
        unfinished_order_list = [i for i in range(self.order_num)]
        while len(unfinished_order_list)>0:
            # add an order to each courier
            for c in range(self.courier_num):
                # get the current nearest order
                nearest_order = self.get_nearest_order(solution[c], unfinished_order_list)
                # add the nearest order to the solution
                solution[c].append(nearest_order)
                solution[c].append(nearest_order+self.order_num)
                # remove the nearest order from the unfinished order list
                unfinished_order_list.remove(nearest_order)
                # check if all orders are finished
                if len(unfinished_order_list) == 0:
                    break

        return solution

    def get_nearest_order(self, solution, unfinished_order_list):
        """ get the nearest order

        Args:
            solution ([]): current solution of the c courier.
            unfinished_order_list ([]): unfinished order list.

        Returns:
            int: the nearest order."""
        cur_node = solution[-1]
        nearest_order = None
        min_distance = float('inf')
        for order in unfinished_order_list:
            # Calculate the distance from the current node to the order node
            distance = self.distance_matrix[cur_node][order]
            if distance < min_distance:
                min_distance = distance
                nearest_order = order
        
        return nearest_order

    def run(self):
        """ run adaptive_nearest_neighbor """
        solution = self.main()

        return solution



