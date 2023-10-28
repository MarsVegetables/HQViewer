'''
Date: 2021-05-29 11:00:20
LastEditors: Lei Si
LastEditTime: 2023-04-27 23:35:04
'''
 
# feature point extraction method.
import vtk
import numpy as np
from tqdm import tqdm
# vtkMeshOpt.
# from vtkMeshOpt.vtkMeshGenerator import vtkUnstructuredGridGen
from vtkMeshOpt.pointsToArrows import PointsToArrows
from vtkMeshOpt.quadHexaPolygonGen import QuadHexaPolygenGenerator
from boundaryErrorVis.bndErrorVisUtility import cellListToPolygon
from vtk.util.numpy_support import vtk_to_numpy

class IntersectMarker:
    def __init__(self, _coord, _cells, _MaxRadius, _arrowColor, _polygonColor):
        # _bIndex is boundary index
        self.coords = _coord
        self.cells = _cells
        self.p2a = PointsToArrows(_MaxRadius, _arrowColor)
        self.arrowActors = []
        self.intersectingPointNum = 0
        if len(_cells[0]) == 8:
            # hex
            self.quadGen = QuadHexaPolygenGenerator("intersecting", _coord, _polygonColor, _3dFlag = True)
        else:
            # quad
            self.quadGen = QuadHexaPolygenGenerator("intersecting", _coord, _polygonColor)
    
    def updateMaxRadius(self, _maxR):
        self.p2a.updateMaxRadius(_maxR)

    def run(self):
        print("checking intersecting element ...")
        self.overlappingCells = []
        self.overlappingCellActor = []
        self.arrowActors = []
        self.intersectingPointNum = 0
        for cell in tqdm(self.cells):
            result = self.intersectDet(cell)
            if len(result) > 0:
                # overlapping cell list
                for p in result:
                    location = np.where(self.cells == p)
                    rowNum = location[0]
                    for r in rowNum:
                        self.addCellInList(self.cells[r])
                self.addCellInList(cell)
                # Arrow actors
                enclosedPointCoords = self.coords[result]
                actors = self.points2Actor(enclosedPointCoords)
                self.arrowActors.extend(actors)
                # break
        # intersecting count
        self.intersectingPointNum = len(self.overlappingCells)
        self.overlappingCellActor = self.quadGen.createPolygonActor(self.overlappingCells)

    def addCellInList(self, _cell):
        if _cell not in self.overlappingCells:
            self.overlappingCells.append(_cell)
        
    def points2Actor(self, _points):
        unique = np.unique(_points, axis=0)
        p2aStructure = []
        for x in unique:
            tmp = [x, 1]
            p2aStructure.append(tmp)
        endPoints = self.p2a.pointsToArrowEnds(p2aStructure)
        return self.p2a.pointsToArrowAction(endPoints)
    
    def intersectDet(self, _cell):
        if len(_cell) == 8:
                cellPolydata = cellListToPolygon(self.coords, [_cell], [],  meshType = "Hex")
        else:
            cellPolydata = cellListToPolygon(self.coords, [_cell], [],  meshType = "Quad")
        pointPolydata = coordToVtkPointPolyData(self.coords)
        enclosedPids = findEncodesPoints(pointPolydata, cellPolydata)
        result = []
        for pid in enclosedPids:
            if not pid in _cell:
                result.append(pid)
        return result

def coordToVtkPointPolyData(_coords):
    vtkPoints = vtk.vtkPoints()
    for c in _coords:
        vtkPoints.InsertNextPoint(c)
    pointsPolydata = vtk.vtkPolyData()
    pointsPolydata.SetPoints(vtkPoints)
    return pointsPolydata

def findEncodesPoints(_input, _surface):
    epfilter = vtk.vtkSelectEnclosedPoints()
    epfilter.SetInputData(_input)
    epfilter.SetSurfaceData(_surface)
    epfilter.Update()

    enclosedPoints = epfilter.GetOutput().GetPointData().GetArray("SelectedPoints")
    selectedPoints = vtk_to_numpy(enclosedPoints)
    pids = np.where(selectedPoints == 1)
    # pids is (array([  9,  45,  92, 120, 138, 229, 314, 421, 432]),)
    return pids[0]
        
'''
from MeshLoader import MeshLoader

def test_main():
    renderWindow = vtk.vtkRenderWindow()
    interactor = vtk.vtkRenderWindowInteractor()
    colors = vtk.vtkNamedColors()
    # Set the background color.
    colors.SetColor('BkgColor', [26, 51, 77, 255])

    filePath = "/mnt/mdisk/UHResearches/VTK_2D/Smoothing_Examples/"
    fileName = "mazewheel3.vtk"
    basicGraphic = MeshLoader(filePath, fileName)
    basicGraphic.generateNpPoints()
    basicGraphic.generateBoundaryPoints()
    basicGraphic.generateBoundaryPointsIndexList()
    basicGraphic.cellList_vtk2np()
    basicGraphic.generateNpPoints()

    newGraphicfilePath = "/mnt/mdisk/UHClasses/CG-6372/final_Project/results/Lei_res/"
    newGraphicfileName = "glp_bnd_10_mazewheel3.vtk"
    newGraphic = MeshLoader(newGraphicfilePath, newGraphicfileName)
    newGraphic.generateNpPoints()
    newGraphic.generateBoundaryPoints()
    newGraphic.generateBoundaryPointsIndexList()
    newGraphic.cellList_vtk2np()
    newGraphic.generateNpPoints()

    fpfObj = IntersectMarker(newGraphic.generateNpPoints(), newGraphic.cellList, 0.03, [50, 0, 255])
    
    edges = vtk.vtkExtractEdges()
    edges.SetInputConnection(newGraphic.vtkReader.GetOutputPort())
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(edges.GetOutputPort())
    mapper.ScalarVisibilityOff()
    bgActor = vtk.vtkActor()
    bgActor.SetMapper(mapper)
    bgActor.GetProperty().SetOpacity(0.6)
    
    fpfObj.run()
    
    # Visualize
    renderer = vtk.vtkRenderer()
    renderer.AddActor(bgActor)
    for a in fpfObj.arrowActors:
        renderer.AddActor(a)
    renderer.AddActor(fpfObj.overlappingCellActor)
    renderer.SetBackground(colors.GetColor3d('BkgColor'))

    renderWindow.SetSize(640, 480)
    renderWindow.AddRenderer(renderer)

    interactor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    interactor.Start()
'''
# test_main()

