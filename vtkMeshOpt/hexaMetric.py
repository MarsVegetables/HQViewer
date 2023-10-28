'''
Date: 2021-03-11 20:45:13
LastEditors: Lei Si
LastEditTime: 2021-09-19 01:13:02

https://github.com/Kitware/VTK/blob/master/ThirdParty/verdict/vtkverdict/verdict.h.in
'''

from math import sqrt
import numpy as np

class Hexa_ScaledJacobian:
    #
    # scaled Jacobian of a hex
    #
    # Minimum Jacobian divided by the lengths of the 3 edge vectors.
    #

    # this class is almost same with the code in the vtk verdict lib.
    def __init__(self, _name, _cells, _coords):
        self.name = _name
        self.cells = _cells
        self.coords = _coords.copy()
        self.test_flag = False
        self.dbl_min = 0.001 # should set a very small value

    def cell_coord(self, _index_list):
        return self.coords[_index_list] 
            
    # coordinates should be np array.
    def scaledJacobian_cell(self, _cell):
        scaled_j_list = []
        np_cell = np.array(_cell)

        # J (0,0,0)
        J_index = [0,1,3,4]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])

        # J (1,0,0)
        J_index = [1,2,0,5]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])

        # J (1,1,0)
        J_index = [2,3,1,6]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])

        # J (0,1,0)
        J_index = [3,0,2,7]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])
        
        # J (0,0,1)
        J_index = [4,7,5,0]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])

        # J (1,0,1)
        J_index = [5,4,6,1]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])

        # J (1,1,1)
        J_index = [6,5,7,2]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])

        # J (0,1,1)
        J_index = [7,6,4,3]
        node_indexs = np_cell[J_index]
        node_pos = self.cell_coord(node_indexs)
        # print(node_pos)
        scaled_j = self.scaledJacobian_corner(node_pos)
        scaled_j_list.append([node_indexs ,scaled_j])
        return scaled_j_list

    def scaledJacobian_all_node(self):
        for cell in self.cells:
            self.scaledJacobian_cell(cell)

    def scaledJacobian_corner(self, _node_pos):
        if len(_node_pos) > 4:
            print("input to many coordinates.")
            return -1
        
        # J
        node_pos = _node_pos
        xxi = node_pos[1] - node_pos[0]
        xet = node_pos[2] - node_pos[0]
        xze = node_pos[3] - node_pos[0]
        # dot product and cross product
        # in VTK verdict vector. 
        # https://github.com/Kitware/VTK/blob/master/ThirdParty/verdict/vtkverdict/VerdictVector.hpp
        # * is cross product
        # % is dot product
        Jacobi = np.dot(xxi,np.cross(xet,xze)) # this part require vertcor operators 
        
        # calculate squared length for each vector
        len1_sq = np.linalg.norm(xxi) ** 2
        len2_sq = np.linalg.norm(xet) ** 2
        len3_sq = np.linalg.norm(xze) ** 2
        
        # if len1_sq < self.dbl_min or len2_sq < self.dbl_min or len3_sq < self.dbl_min:
        #     return -1 # return a value to see error
        
        lengths = sqrt(len1_sq * len2_sq * len3_sq)
        if lengths == 0:
            return 0
        norm_jac = Jacobi / lengths
        return norm_jac
    
    def scaledJacobian_efg(self, _node_pos):
        pass

    def calc_hex_efg(self, efg_index, _node_pos):
        if efg_index == 1:
            efg = _node_pos[1]
            efg += _node_pos[2]
            efg += _node_pos[5]
            efg += _node_pos[6]
            efg -= _node_pos[0]
            efg -= _node_pos[3]
            efg -= _node_pos[4]
            efg -= _node_pos[7]
            return efg

        if efg_index == 2:
            efg = _node_pos[2]
            efg += _node_pos[3]
            efg += _node_pos[6]
            efg += _node_pos[7]
            efg -= _node_pos[0]
            efg -= _node_pos[1]
            efg -= _node_pos[4]
            efg -= _node_pos[5]
            return efg

        if efg_index == 3:
            efg = _node_pos[4]
            efg += _node_pos[5]
            efg += _node_pos[6]
            efg += _node_pos[7]
            efg -= _node_pos[0]
            efg -= _node_pos[1]
            efg -= _node_pos[2]
            efg -= _node_pos[3]
            return efg


def test_case():
    cell_indexs = [[0,1,2,3,4,5,6,7]]
    test_coords = np.array([[0.,   0.,  0.],  # 0
                            [1.,   0.,  0.],  # 1
                            [1.,   1.,  0.],  # 2
                            [0.,   1.,  0.],  # 3
                            [0.,   0.,  1.],  # 4
                            [1.,   0.,  1.],  # 5
                            [1.,   1.,  1.],  # 6
                            [0.,   1.,  1.]])  # 7
    
    hex_j = Hexa_ScaledJacobian("test", cell_indexs, test_coords)
    hex_j.scaledJacobian_all_node()

def test_case2():
    cell_indexs = [[0,1,2,3,4,5,6,7]]
    test_coords = np.array([[2.,   2.,  2.],  # 0
                            [1.,   0.,  0.],  # 1
                            [1.,   1.,  0.],  # 2
                            [0.,   1.,  0.],  # 3
                            [0.,   0.,  1.],  # 4
                            [1.,   0.,  1.],  # 5
                            [1.,   1.,  1.],  # 6
                            [0.,   1.,  1.]])  # 7
    
    hex_j = Hexa_ScaledJacobian("test", cell_indexs, test_coords)
    hex_j.scaledJacobian_all_node()

# test_case2()