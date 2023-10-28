'''
Date: 2020-11-18 21:08:22
LastEditors: Lei Si
LastEditTime: 2021-07-01 23:52:45
'''

import vtk
import math
import numpy as np
# from MeshLoader import MeshLoader
from vtkMeshOpt.MeshLoader import MeshLoader
# from vtkMeshOpt.vtkSectorGenerator import visAngleBySector
from tqdm import tqdm

class coneGenerator:
    def __init__(self, _center, _radius, _points):
        self.createIntersectionMesh(_center, _radius, _points)
    
    def createIntersectionMesh(self, _center, _radius, _points):
        self.createSphere(in_center=_center, radius=_radius)
        self.createHexahedron(_points = _points)
        # self.coneActor = self.booleanOptActor(self.hex, self.sphereSource)

    def createSphere(self, in_center, radius):
        # center = [in_center[0] + 0.1 * radius, in_center[1] + 0.1 * radius, in_center[2] + 0.1 * radius]
        center = in_center
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetRadius(radius)
        sphereSource.SetCenter(center)
        # Make the surface smooth.
        sphereSource.SetPhiResolution(50)
        sphereSource.SetThetaResolution(21)
        self.sphereSource = sphereSource

    # 8 edge for hexahedron
    def createHexahedron(self, _points):
        if len(_points) != 8:
            print("input is not hex mesh. please check.")
            return 1
        pPoints = vtk.vtkPoints()
        for point in _points:
            pPoints.InsertNextPoint(point)
        hex = vtk.vtkHexahedron()
        for i in range(len(_points)):
            hex.GetPointIds().SetId(i,i)
        # hexs = vtk.vtkCellArray()
        # hexs.InsertNextCell(hex)
        uGrid = vtk.vtkUnstructuredGrid()
        uGrid.SetPoints(pPoints)
        uGrid.InsertNextCell(hex.GetCellType(), hex.GetPointIds())
        self.hex = self.vtkUnstructuredGrid2Polydata(uGrid)
        # print(self.hex.GetOutput().GetCellType(0))
        # print(self.hex.GetOutput().GetBounds())
    
    def vtkUnstructuredGrid2Polydata(self, ugrid):
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(ugrid)
        geometryFilter.Update()
        return geometryFilter

    def sphereSourceActor(self):
        ps = self.sphereSource
        
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(ps.GetOutputPort())
        mapper.ScalarVisibilityOff()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetColor(s)
        # actor.GetProperty().SetOpacity(0.6)
        # actor.GetProperty().SetRepresentationToPoints()
        actor.GetProperty().SetRepresentationToWireframe()
        # actor.GetProperty().SetLineWidth(2.0)
        # BUG: ps.GetOutput() no result
        return actor

    def HexActor(self):
        ps = self.hex
        
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(ps.GetOutput())
        mapper.ScalarVisibilityOff()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetColor(s)
        # actor.GetProperty().SetOpacity(0.6)
        actor.GetProperty().SetRepresentationToWireframe()
        # actor.GetProperty().SetLineWidth(2.0)
        return actor
    
    def cleanPolyData(self, _polygon):
        cleanPoly = vtk.vtkCleanPolyData()
        cleanPoly.SetInputConnection(_polygon.GetOutputPort())
        cleanPoly.Update()
        return cleanPoly

    # only works on the triangle mesh
    def booleanOptActor(self, _cube, _polygon2):
        booleanOperation = vtk.vtkBooleanOperationPolyDataFilter()
        booleanOperation.SetOperationToIntersection()
        tri1 = self.triFilter(_cube)
        cleanTri1 = self.cleanPolyData(tri1)
        tri2 = self.triFilter(_polygon2)
        cleanTri2 = self.cleanPolyData(tri2)
        booleanOperation.SetInputConnection(0, cleanTri1.GetOutputPort())
        booleanOperation.SetInputConnection(1, cleanTri2.GetOutputPort())
        booleanOperation.Update()
        
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(booleanOperation.GetOutput())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetRepresentationToWireframe()
        return actor
    
    def intersectionOptActor(self, _cube, _polygon2):
        intersectionPolyDataFilter = vtk.vtkIntersectionPolyDataFilter()
        tri1 = self.triFilter(_cube)
        intersectionPolyDataFilter.SetInputConnection(0, tri1.GetOutputPort())
        intersectionPolyDataFilter.SetInputConnection(1, _polygon2.GetOutputPort())
        intersectionPolyDataFilter.Update()

        # data = intersectionPolyDataFilter.GetOutput()
        # writeDataSet(_polygon2.GetOutput(), "clipper.vtk")

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(intersectionPolyDataFilter.GetOutput())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetRepresentationToWireframe()
        return actor

    def ClipOpt(self, _cube, _polygon2):
        tri1 = self.triFilter(_cube)
        implicitCube = vtk.vtkBox()
        implicitCube.SetBounds(tri1.GetOutput().GetBounds())
        # clipper = vtk.vtkClipPolyData()
        # clipper.SetClipFunction(implicitCube)
        clipper = vtk.vtkCutter()
        clipper.SetCutFunction(implicitCube)
        clipper.SetInputConnection(_polygon2.GetOutputPort())
        # clipper.InsideOutOn()
        clipper.Update()

        # data = clipper.GetOutput()
        # writeDataSet(_polygon2, "clipper.vtk")

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(clipper.GetOutput())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetRepresentationToWireframe()
        return actor

    def triFilter(self, input):
        triF = vtk.vtkTriangleFilter()
        triF.SetInputConnection(input.GetOutputPort())
        return triF


def calSideLength(p1, p2):
    sl = 0
    for i in range(len(p1)):
        l = (p1[i] - p2[i]) ** 2
        sl = sl+l
    return math.sqrt(sl)

def findTheShortestBound(_bounds):
    boundL = [abs(_bounds[i] - _bounds[i+1]) for i in range(len(_bounds) - 1)]
    return min(boundL)
    
def HexCell2Face(_hexcell):
    faceIds = [[0,1,2,3], [0, 4, 5, 1], [0, 3, 7, 4], [6, 7, 4, 5], [6, 5, 1, 2], [6, 2, 3, 7]]
    faces = []
    np_cell = np.array(_hexcell)
    for ids in faceIds:
        face = np_cell[ids]
        faces.append(list(face))
    return faces


class visCornerByCone(MeshLoader):
    def __init__(self, unstructuredGridReader):
        self.ugridReader = unstructuredGridReader
        self.vtkRawData = self.ugridReader.GetOutput()
        self.vtkpoints = self.vtkRawData.GetPoints()
        self.cells = self.vtkRawData.GetCells()
        self.cellList_vtk2np()
        self.point_cones={}
        self.stopNum = len(self.cellList)
        # self.createConeDir()
        
    def GetFaces(self):
        faces = []
        for i, cell in enumerate(self.cellList):
            facesHex = HexCell2Face(cell)
            faces.extend(facesHex)
            if i > self.stopNum:
                break
        return faces
    
    def createConeDir(self):
        for i, cell in tqdm(enumerate(self.cellList)):
            # if i != 17:
            #     continue
            bounds = self.vtkRawData.GetCell(i).GetBounds()
            # ToDo: may update to the shortest edge.
            minBound = findTheShortestBound(bounds)
            points = []
            for index in cell:
                point = self.getPointCoord(index)
                points.append(point)
            radius = minBound
            # print(minBound)
            ratio = 0.5 # get stuck when this is 0.6, 1, 2, 2.001, ..... 0.5, 0.59 and 2.1. 2.01, 3 is working.
            # print("\n")
            # print("------------------------")
            # print(radius)
            # print(ratio * radius)
            for j, point in enumerate(points):
                pointIdx = cell[j]
                # if j != 6:
                #    continue
                # print(point)

                coneObj = coneGenerator(point, ratio * radius, points)
                # booleanActor = coneObj.coneActor
                booleanActor = coneObj.booleanOptActor(coneObj.hex, coneObj.sphereSource)
                self.addActorToDir(pointIdx, booleanActor)
                # self.hexGridActor = coneObj.HexActor()
                # self.sphereGridActor = coneObj.sphereSourceActor()
    
            if i >= self.stopNum:
                break

    def addActorToDir(self, pointIndex, actor):
        if pointIndex not in self.point_cones.keys():
            self.point_cones[pointIndex]={"booleanActors":[]}
        self.point_cones[pointIndex]["booleanActors"].append(actor)

def test():
    filePath = "/mnt/mdisk/UHResearches/CotrikMesh/VTKExamples/Example_Naeem/"
    fileName = "kitty_hex.vtk"
    MeshL = MeshLoader(file_path=filePath, file_name=fileName)
    
    vcc = visCornerByCone(MeshL.vtkReader)
    vcc.GetFaces()
    vcc.createConeDir()
    
    # * calculate angle and ratio for each face. sector is not correct for 3D space.
    # vas = visAngleBySector(MeshL.vtkReader, faces)

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(MeshL.vtkReader.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetColor(s)
    # actor.GetProperty().SetOpacity(0.6)
    actor.GetProperty().SetRepresentationToPoints()
    actor.GetProperty().SetLineWidth(2.0)

    renderer = vtk.vtkRenderer()
    
    for p in vcc.point_cones:
        for actor in vcc.point_cones[p]["booleanActors"]:
            renderer.AddActor(actor)
    
    renderer.AddActor(vcc.hexGridActor)
    renderer.AddActor(vcc.sphereGridActor)
    
    '''
    for ac in vas.sectorActors:
        renderer.AddActor(ac)
    '''

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    # renderWindow.SetSize(640, 480)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    interactor.Initialize()
    interactor.Start()


# test()