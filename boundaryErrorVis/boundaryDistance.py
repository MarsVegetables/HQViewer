'''
Date: 2021-10-04 01:08:41
LastEditors: Lei Si
LastEditTime: 2021-10-19 16:15:10
'''

import vtk
import numpy as np
from boundaryErrorVis.bndErrorVisUtility import cellListToPolygon, normalizeV
from vtk.util.numpy_support import vtk_to_numpy
from tqdm import tqdm

class hexToSurface:
    def __init__(self, _vtkReader) -> None:
        self.vtkReader = _vtkReader
        self.DSToSurfacePolyData()
        vtkPoints = self.SurfaceFilter.GetOutput().GetPoints().GetData()
        self.npPoints = vtk_to_numpy(vtkPoints)
        vtkCells = self.SurfaceFilter.GetOutput().GetPolys().GetConnectivityArray()
        self.npCells = vtk_to_numpy(vtkCells).reshape((-1, 4))

    def HexVidToSurfaceVidMapper(self):
        print("mapping Hex Vid to surface Vid ...")
        self.SurfaceIdMapper = {}
        HexPoints = self.vtkReader.GetOutput().GetPoints().GetData()
        HexNpPoints = vtk_to_numpy(HexPoints)
        for i, point in tqdm(enumerate(HexNpPoints)):
            pCount = 0
            for j, sp in enumerate(self.npPoints):
                r = (point == sp).all()
                if r:
                    pCount += 1
                    if pCount > 1:
                        print("one point id on Hex have two point id on surface.")
                        print(i, "-", j)
                    self.SurfaceIdMapper[i] = j

    def DSToSurfacePolyData(self):
        SurfaceFilter = vtk.vtkDataSetSurfaceFilter()
        SurfaceFilter.SetInputConnection(self.vtkReader.GetOutputPort())
        SurfaceFilter.Update()
        self.SurfaceFilter = SurfaceFilter
        self.polyNormals = self.polyDataNormals(self.SurfaceFilter)
        return self.SurfaceFilter

    def polyDataNormals(self, _pd):
        polyNormals = vtk.vtkPolyDataNormals()
        polyNormals.SetInputData(_pd.GetOutput())
        polyNormals.ComputeCellNormalsOff()
        polyNormals.ComputePointNormalsOn()
        # polyNormals.SplittingOff()
        # polyNormals.FlipNormalsOff()
        # polyNormals.ConsistencyOn()
        # polyNormals.AutoOrientNormalsOn()
        polyNormals.Update()
        vtkPoints = polyNormals.GetOutput().GetPointData().GetNormals()
        vtkcells = polyNormals.GetOutput().GetCellData().GetNormals()
        # npPoints = vtk_to_numpy(vtkcells)
        # print(npPoints)
        return polyNormals

class bndDistance:
    def __init__(self, _sampleVTKReader, _targetVTKReader) -> None:
        self.samepleVTKReader = _sampleVTKReader
        self.targetVTKReader = _targetVTKReader
        self.makeSurfacePolyData()
        self.getTargetDiagonal()
        self.getSurfaceDistance()
        self.distanceToPercentage()
        self.distanceToPercentage_hexId()

    def makeSurfacePolyData(self):
        self.sampleSurface = hexToSurface(self.samepleVTKReader)
        self.sampleSurfacePolyData = self.sampleSurface.SurfaceFilter.GetOutput()
        self.sampleSurface.HexVidToSurfaceVidMapper()
        self.targetSurface = hexToSurface(self.targetVTKReader)
        self.targetSurfacePolyData = self.targetSurface.SurfaceFilter.GetOutput()

    def getSurfaceDistance(self):
        # The signed distance to the second input is computed 
        # at every point in the first input 
        # using vtkImplicitPolyDataDistance.
        distanceFilter = vtk.vtkDistancePolyDataFilter()
        distanceFilter.SetInputData(0, self.sampleSurfacePolyData)
        distanceFilter.SetInputData(1, self.targetSurfacePolyData) # surface that want to compare.
        distanceFilter.Update()
        scales = distanceFilter.GetOutput().GetPointData().GetScalars()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(distanceFilter.GetOutputPort())
        mapper.SetScalarRange(scales.GetRange()[0], scales.GetRange()[1])
        print(scales.GetRange()[0], scales.GetRange()[1])
        self.filterActor = vtk.vtkActor()
        self.filterActor.SetMapper(mapper)
        
        # scaleRange = scales.GetRange()
        self.npScales = vtk_to_numpy(scales)
        self.vtkScalesToPyDict()
        # self.testMapper(distanceFilter.GetOutput().GetPoints().GetData())

    def getTargetDiagonal(self):
        targetCOords = self.targetSurface.npPoints
        xmax = max(targetCOords[:,0])
        xmin = min(targetCOords[:,0])
        ymax = max(targetCOords[:,1])
        ymin = min(targetCOords[:,1])
        zmax = max(targetCOords[:,2])
        zmin = min(targetCOords[:,2])
        svx = (xmax - xmin) ** 2
        svy = (ymax - ymin) ** 2
        svz = (zmax - zmin) ** 2
        self.targetDiagonal = np.sqrt(svx + svy + svz)

    def baseLength(self):
        # diagonal_10p = self.mesh_diagonal * 0.1
        diagonal_10p = self.targetDiagonal
        max_input = diagonal_10p
        return max_input

    def vtkScalesToPyDict(self):
        vids = range(len(self.npScales))
        self.distanceDict = {v:self.npScales[v] for v in vids}
        
    def distanceToPercentage(self):
        max_input = self.baseLength()
        self.distancePercentageDict_surfaceIds = {}
        for k, v in self.distanceDict.items():
            sign = 1
            if v < 0:
                sign = -1
            distancePercentage = normalizeV(abs(v), max_input, 0)
            self.distancePercentageDict_surfaceIds[k] = sign * distancePercentage     
    
    def distanceToPercentage_hexId(self):
        self.distancePercentageDict_HexIds = {}
        for hexId, surfaceId in self.sampleSurface.SurfaceIdMapper.items():
            v = self.distancePercentageDict_surfaceIds[surfaceId]
            self.distancePercentageDict_HexIds[hexId] = v  