'''
Date: 2020-09-30 21:02:12
LastEditors: Lei Si
LastEditTime: 2021-05-13 21:29:27
'''
 
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import numpy as np
# from vtkMeshOpt.MeshLoader import MeshLoader
from MeshLoader import MeshLoader


class vtkUnstructuredGridGen(MeshLoader):
    '''
        This class creates a Unstructured Grid based on a 2d points array and a vtkCellArray.
    '''
    def __init__(self, points2d, cells):
        # covert points 2d to 3d
        if len(points2d[0]) == 2:
            points3d = np.append(points2d,np.zeros([len(points2d),1]),1)
        else:
            points3d = points2d
        # vtkpoints = numpy_to_vtk(points3d)
        ugrid = vtk.vtkUnstructuredGrid()
        vtkpoints = vtk.vtkPoints()
        for x in points3d:
            vtkpoints.InsertNextPoint(x)
        ugrid.SetPoints(vtkpoints)
        # https://vtk.org/doc/release/4.2/html/vtkCellType_8h.html
        ugrid.SetCells(vtk.VTK_QUAD, cells)
        # self.ugrid = ugrid
        self.vtkRawData = ugrid
        self.cells = cells
        self.points3d = points3d

    def writeToFile(self, fn):
        writer = vtk.vtkUnstructuredGridWriter()
        # writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(fn)
        writer.SetInputData(self.vtkRawData)
        writer.Update()
        writer.Write()
    
    def writeQuadMeshto30format(self, newVtkPath):
        '''
        Save Quad Mesh to VTK 3.0 File Format
        newVtkPath : file save full path
        '''
        # np.set_printoptions(precision=7)
        points = self.points3d
        cells = self.cells
        with open(newVtkPath, "w") as writer:
            writer.write("# vtk DataFile Version 3.0\n")
            filename = newVtkPath.split("/")[-1]
            writer.write(filename + "\n")
            writer.write("ASCII\n")
            writer.write("\n")

            writer.write("DATASET UNSTRUCTURED_GRID\n")
            
            # points
            p_l_str = str(len(points))
            points_line = "POINTS " + p_l_str + " double\n" 
            writer.write(points_line)
            # npoints = np.around(points, decimals = 7)
            npoints = points
            for p in npoints:
                str_p = ' '.join(['{:.7f}'.format(x) for x in p])
                writer.write(str_p + "\n")
            writer.write("\n")
            
            # cells
            cellsData = cells.GetData()
            cellsArray = vtk_to_numpy(cellsData).reshape([-1,5])
            cells_l = len(cellsArray)
            # assume all cells are quad cell 
            numberofValues = cellsData.GetNumberOfValues()
            CELLS_line = "CELLS " + str(cells_l) + " " + str(numberofValues) + "\n"
            writer.write(CELLS_line)
            for cell in cellsArray:
                str_cell = ' '.join([str(z) for z in cell])
                writer.write(str_cell + "\n")
            writer.write("\n")

            # cell types
            CELL_TYPES_line = "CELL_TYPES " + str(cells_l) + "\n"
            writer.write(CELL_TYPES_line)
            for i in range(0, cells_l):
                writer.write(str(9) + "\n")
            
            writer.write("\nPOINT_DATA " + p_l_str)
            writer.close()
            print("save file : \n" + newVtkPath)
            print("successfully.")