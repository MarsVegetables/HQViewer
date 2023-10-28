'''
Date: 2021-03-11 20:44:55
LastEditors: Lei Si
LastEditTime: 2021-09-18 17:02:28
'''
import numpy as np
import vtk
import math

class Quad_ScaledJacobian:
    # this class is almost same with the code in the vtk verdict lib.
    def __init__(self, _name, _nodes_cells, _coords):
        self.name = _name
        self.nodes_cells = _nodes_cells
        self.coords = _coords.copy()
        self.test_flag = False
        self.dbl_min = 0.1 # should set a very small value

    def scaledJacobian_all_node(self):
        for node_cells in self.nodes_cells:
            node = node_cells[0]
            cells = node_cells[1:]
            for cell in cells:
                scaled_jac = self.scaledJacobian_cell(cell)
                print(scaled_jac)

    def scaledJacobian_cell(self, _cell):
        coords = self.cell_coord(_cell)
        scaled_jac = self.quad_scaled_jacobian(coords)
        index_scaled_jac = self.valuesToIndexAndValue(np.array(_cell), scaled_jac)
        return index_scaled_jac

    def valuesToIndexAndValue(self, _cell, _values):
        index_scaled_Jac = []
        angleIndex = [[1,0,3], [2,1,0], [3,2,1], [0,3,2]]
        for i, v in enumerate(_values):
            indexs = _cell[angleIndex[i]]
            i_v = [indexs, v]
            index_scaled_Jac.append(i_v)
        return index_scaled_Jac

    def cell_coord(self, _index_list):
        return self.coords[_index_list] 
    
    def signed_corner_areas(self, _coordinates):
        # in VTK verdict vector. 
        # https://github.com/Kitware/VTK/blob/master/ThirdParty/verdict/vtkverdict/VerdictVector.hpp
        # * is cross product
        # % is dot product

        edges = self.make_quad_edges(_coordinates)
        corner_normals = []
        corner_normals.append(np.cross(edges[3], edges[0]))
        corner_normals.append(np.cross(edges[0], edges[1]))
        corner_normals.append(np.cross(edges[1], edges[2]))
        corner_normals.append(np.cross(edges[2], edges[3]))

        principal_axes = []
        principal_axes.append(edges[0] - edges[2])
        principal_axes.append(edges[1] - edges[3])

        # quad center unit normal
        unit_center_normal = np.cross(principal_axes[0], principal_axes[1])
        unit_center_normal = unit_center_normal / np.linalg.norm(unit_center_normal) 

        # calculate areas
        areas = []
        areas.append(np.dot(unit_center_normal, corner_normals[0]))
        areas.append(np.dot(unit_center_normal, corner_normals[1]))
        areas.append(np.dot(unit_center_normal, corner_normals[2]))
        areas.append(np.dot(unit_center_normal, corner_normals[3]))
        
        return areas
    
    def make_quad_edges(self, _coordinates):
        edges = np.zeros((4,3))
        # edge 0-1
        edges[0][0] = _coordinates[1][0] - _coordinates[0][0]
        edges[0][1] = _coordinates[1][1] - _coordinates[0][1]
        edges[0][2] = _coordinates[1][2] - _coordinates[0][2]
        #edge 1-2
        edges[1][0] = _coordinates[2][0] - _coordinates[1][0]
        edges[1][1] = _coordinates[2][1] - _coordinates[1][1]
        edges[1][2] = _coordinates[2][2] - _coordinates[1][2]
        #edge 2-3
        edges[2][0] = _coordinates[3][0] - _coordinates[2][0]
        edges[2][1] = _coordinates[3][1] - _coordinates[2][1]
        edges[2][2] = _coordinates[3][2] - _coordinates[2][2]
        #edge 3-0
        edges[3][0] = _coordinates[0][0] - _coordinates[3][0]
        edges[3][1] = _coordinates[0][1] - _coordinates[3][1]
        edges[3][2] = _coordinates[0][2] - _coordinates[3][2]
        
        return edges

    def quad_scaled_jacobian(self, _coordinates):
        edges = self.make_quad_edges(_coordinates)
        corner_areas = self.signed_corner_areas(_coordinates)
        lengths = []
        for i in edges:
            lengths.append(np.linalg.norm(i))

        scaled_jac = []
        if jacobin_watch_dog(lengths[0]) and jacobin_watch_dog(lengths[3]):
            j0 = corner_areas[0] / (lengths[0] * lengths[3])
        else:
            j0 = -1
        scaled_jac.append(j0)
        if jacobin_watch_dog(lengths[1]) and jacobin_watch_dog(lengths[0]):
            j1 = corner_areas[1] / (lengths[1] * lengths[0])
        else:
            j1 = -1
        scaled_jac.append(j1)
        if jacobin_watch_dog(lengths[1]) and jacobin_watch_dog(lengths[2]):
            j2 = corner_areas[2] / (lengths[2] * lengths[1])
        else:
            j2 = -1
        scaled_jac.append(j2)
        if jacobin_watch_dog(lengths[3]) and jacobin_watch_dog(lengths[2]):
            j3 = corner_areas[3] / (lengths[3] * lengths[2])
        else:
            j3 = -1
        scaled_jac.append(j3)

        return scaled_jac

def jacobin_watch_dog(_value):
    if _value == 0:
        return False
    else:
        return True

def test_case():
    cell_indexs = [[0,[0,1,2,3]]]
    test_coords = np.array([[0.,   0.,  0.],  # 0
                            [1.,   0.,  0.],  # 1
                            [1.,   1.,  0.],  # 2
                            [0.,   1.,  0.]]) # 3
    
    quad_j = Quad_ScaledJacobian("test", cell_indexs, test_coords)
    quad_j.scaledJacobian_all_node()

def test_case2():
    cell_indexs = [[0,[0,1,2,3]]]
    test_coords = np.array([[-0.5,   -0.5,  0.],  # 0
                            [1.,   0.,  0.],  # 1
                            [1.,   1.,  0.],  # 2
                            [0.,   1.,  0.]]) # 3
    
    quad_j = Quad_ScaledJacobian("test", cell_indexs, test_coords)
    quad_j.scaledJacobian_all_node()

# test_case2()