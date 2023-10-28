'''
Date: 2021-08-10 22:59:23
LastEditors: Lei Si
LastEditTime: 2021-10-10 21:29:53
'''
import numpy as np

class meshConfig:
    #    
    #       7 -------- 6
    #      /|         /|
    #     / |        / |
    #    4 -------- 5  |
    #    |  3 ------|- 2
    #    | /        | /
    #    |/         |/
    #    0 -------- 1
    #   
    VTK_HexFaceConf = [ [0, 1,  2,  3], 
                    [0, 4,  5,  1], 
                    [0, 3,  7,  4], 
                    [6, 7,  4,  5], 
                    [6, 5,  1,  2], 
                    [6, 2,  3,  7]]

    VTK_HexEdgeConf = [[0, 1], [1, 2], [2, 3], [3, 0],
                    [0, 4], [1, 5], [2, 6], [3, 7],
                    [4, 5], [5, 6], [6, 7], [7, 4]]

    #  
    #   0 -- -- 1
    #   |       |
    #   |       |
    #   3 -- -- 2
    #
    VTK_QaudEdgeConf = [[0, 1],
                    [1, 2],
                    [2, 3],
                    [3, 0]]
    

    def cellToFaces(self, _cell):
    # split cell array to face list
        faces = []
        if len(_cell) == 4:
            faces.append(_cell)
        else:
            for ids in self.VTK_HexFaceConf:
                face = np.array(_cell)[ids]
                # newface = np.flip(face)
                faces.append(face) # if direction is not correct, we need to flip the face ides.
        return faces

    def faceToEdges(self, _face):
        # split face array to edge list
        edges = []
        edgeConf = self.VTK_QaudEdgeConf
    
        for ids in edgeConf:
            edge = np.array(_face)[ids]
            edges.append(edge)

        return edges

    def cellToEdges(self, _cell):
        # split cell array to edge list
        edges = []
        if len(_cell) == 4:
            edgeConf = self.VTK_QaudEdgeConf
        else:
            edgeConf = self.VTK_HexEdgeConf
        
        for ids in edgeConf:
            edge = np.array(_cell)[ids]
            edges.append(edge)

        return edges

    def __init__(self) -> None:
        pass