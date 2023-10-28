'''
Date: 2020-11-07 23:40:09
LastEditors: Lei Si
LastEditTime: 2021-08-13 15:06:31
'''
 
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy

class MeshLoader:
    def __init__(self, file_path, file_name, _loadFlag = True):
        self.file_path = file_path
        self.file_name = file_name
        self.RawDataPath = file_path + file_name
        if _loadFlag:
            self.loadvtkUnstructuredGrid()
    
    def loadvtkUnstructuredGrid(self):
        reader = vtk.vtkUnstructuredGridReader()
        reader.SetFileName(self.RawDataPath)
        reader.Update()
        self.vtkReader = reader
        self.cells = self.vtkReader.GetOutput().GetCells()
        self.vtkpoints = self.vtkReader.GetOutput().GetPoints()
        if self.vtkReader.GetOutput().GetFaces():
            self.faces = self.vtkReader.GetOutput().GetFaces()

    def facesList_vtk2np(self):
        faces = self.faces
        self.np_faces = vtk_to_numpy(faces.GetData())

    def getPointCoord(self, Index):
        '''
            get point coordinate based on the point index.
        '''
        p = [0, 0, 0]
        self.vtkpoints.GetPoint(Index, p)
        return p

    def cellList_vtk2np(self):
        # cell list
        cells = self.cells
        np_cells = vtk_to_numpy(cells.GetData())
        np_offset = vtk_to_numpy(cells.GetOffsetsArray())
        cell_list = []
        startIndex = 1
        pPointIndex = 0
        for x in np_offset:
            if x == 0:
                continue 
            offset = x - pPointIndex
            endIndex = startIndex + offset
            cell = np_cells[startIndex : endIndex]
            startIndex = endIndex + 1
            pPointIndex = x
            cell_list.append(cell.tolist())
        self.cellList = cell_list
        return self.cellList
        
    def generateBoundaryPoints(self):
        vtkRawDataPort = self.vtkReader.GetOutputPort()
        vtk_filter = vtk.vtkDataSetSurfaceFilter()
        vtk_filter.SetInputConnection(vtkRawDataPort)
        vtk_filter.Update()
        vtk_geometry = vtk.vtkFeatureEdges()
        vtk_geometry.SetInputConnection(vtk_filter.GetOutputPort())
        vtk_geometry.BoundaryEdgesOn()
        vtk_geometry.FeatureEdgesOff()
        vtk_geometry.ManifoldEdgesOff()
        vtk_geometry.NonManifoldEdgesOff()
        vtk_geometry.Update()
        vtk_geometry_output = vtk_geometry.GetOutput()
        vtkBoundaryLines = vtk_geometry_output.GetLines()
        npBoundaryLines = vtk_to_numpy(vtkBoundaryLines.GetData())
        self.npBoundaryLines = np.reshape(npBoundaryLines, (-1,3))
        vtkBoundaryPoints = vtk_geometry_output.GetPoints()
        self.npBoundaryPoints = vtk_to_numpy(vtkBoundaryPoints.GetData())
    
    def generateNpPoints(self):
        # points array
        points = self.vtkpoints
        self.nppoints = vtk_to_numpy(points.GetData())
        return self.nppoints

    def generateBoundaryPointsIndexList(self):
        npBP = self.npBoundaryPoints
        npPoints = self.nppoints
        indexList = []
        for x in npBP:
            index_tmp = np.all(x == npPoints, axis=1)
            index_list = index_tmp.tolist()
            index_p = index_list.index(True)
            indexList.append(index_p)

        self.boundaryPointIndexs = indexList