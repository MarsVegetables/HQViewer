'''
Date: 2021-05-13 13:46:22
LastEditors: Lei Si
LastEditTime: 2021-05-21 14:58:41
'''
 
# feature point extraction method.
import vtk
import numpy as np
from vtkMeshGenerator import vtkUnstructuredGridGen

class FeaturePointExtractor:
    def __init__(self, _cellList, _bIndex, _points):
        # _bIndex is boundary index
        self.cellList = _cellList
        self.boundaryIndex = _bIndex
        self.points = _points
        self.normalBndEdges = []
        self.boundaryCellFilter()
        self.FeaturePointFilter()
    
    def boundaryCellFilter(self):
        self.boundaryCellList = []
        for cell in self.cellList:
            for point in self.boundaryIndex:
                if point in cell:
                    self.boundaryCellList.append(cell)
                    continue
    
    def FeaturePointFilter(self):
        fpList = []
        for p in self.boundaryIndex:
            subCell = []
            for cell in self.boundaryCellList:
                if p in cell:
                    subCell.append(cell)
            if not self.subCellToBoundaryEdge(p, subCell):
                fpList.append(p)
        self.FeaturePoints = fpList
    
    def subCellToBoundaryEdge(self, _p, _subCell):
        boundaryEdge = []
        for cell in _subCell:
            boundaryEdge = self.cellToBoundaryEdge(_p, cell, boundaryEdge)
        # print(boundaryEdge)
        # print("------------")
        if len(boundaryEdge) == 2:
            eFlag = self.paralleDetection(boundaryEdge)
            if eFlag:
                self.normalBndEdges.append(boundaryEdge)
            return eFlag
        return False
    
    def paralleDetection(self, _bEdges):
        e1 = _bEdges[0]
        e2 = _bEdges[1]
        v1 = self.points[e1[1]] - self.points[e1[0]]
        v2 = self.points[e2[1]] - self.points[e2[0]]
        v1_l = np.linalg.norm(v1)
        v2_l = np.linalg.norm(v2)
        if v1_l != 0 and v2_l != 0:
            v1 = v1 / v1_l
            v2 = v2 / v2_l
            cosTheta = np.dot(v1, v2)
            # print(cosTheta)
            if abs(cosTheta) > 0.999: # the degree of two vectors
                # print(_bEdges)
                return True
        return False

    def cellToBoundaryEdge(self, _p, _cell, _bEdges):
        i = _cell.index(_p)
        i_b = (i - 1) % len(_cell)
        i_a = (i + 1) % len(_cell)
        if _cell[i_b] in self.boundaryIndex:
            edge1 = []
            edge1.append(_p)
            edge1.append(_cell[i_b])
            if edge1 not in _bEdges:
                _bEdges.append(edge1)
        if _cell[i_a] in self.boundaryIndex:
            edge2 = []
            edge2.append(_p)
            edge2.append(_cell[i_a])
            if edge2 not in _bEdges:
                _bEdges.append(edge2)
        return _bEdges

    def BoundaryPointActors(self, _pl):
        colors = vtk.vtkNamedColors()
        sActors = []
        for pointI in _pl:
            point = self.points[pointI]
            sphereStartSource = vtk.vtkSphereSource()
            sphereStartSource.SetCenter(point)
            sphereStartSource.SetRadius(0.01) # sphere size
            sphereStartMapper = vtk.vtkPolyDataMapper()
            sphereStartMapper.SetInputConnection(sphereStartSource.GetOutputPort())
            sphereStart = vtk.vtkActor()
            sphereStart.SetMapper(sphereStartMapper)
            sphereStart.GetProperty().SetColor(colors.GetColor3d('Cyan'))
            sActors.append(sphereStart)
        return sActors
        
    def BoundaryPolygonActor(self):
        self.npToVtkCellArray()
        self.unstructuredGrid = vtkUnstructuredGridGen(self.points, self.vtkBoundaryCells)
        mapper = self.createMapperUseData(self.unstructuredGrid.vtkRawData)
        actor = self.createActor(mapper)
        return actor

    def createMapperUseData(self, polydata):
        polyMapper = vtk.vtkDataSetMapper()
        polyMapper.SetInputData(polydata)
        polyMapper.ScalarVisibilityOff()
        return polyMapper
    
    
    def createActor(self, mapper):
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetLineWidth(1.0)
        return actor

    def npToVtkCellArray(self):
        vtk_cells = vtk.vtkCellArray()
        for cell in self.boundaryCellList:
            vtk_cells.InsertNextCell(len(cell))
            for id in cell:
                vtk_cells.InsertCellPoint(int(id))
        self.vtkBoundaryCells = vtk_cells



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
    fpfObj = FeaturePointExtractor(basicGraphic.cellList, basicGraphic.boundaryPointIndexs,basicGraphic.generateNpPoints())
    '''
    edges = vtk.vtkExtractEdges()
    edges.SetInputConnection(basicGraphic.vtkReader.GetOutputPort())
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(edges.GetOutputPort())
    mapper.ScalarVisibilityOff()
    bgActor = vtk.vtkActor()
    bgActor.SetMapper(mapper)
    bgActor.GetProperty().SetOpacity(0.6)
    '''
    bdActor = fpfObj.BoundaryPolygonActor()
    bdpActors = fpfObj.BoundaryPointActors(fpfObj.FeaturePoints)
    # Visualize
    renderer = vtk.vtkRenderer()
    renderer.AddActor(bdActor)
    for a in bdpActors:
        renderer.AddActor(a)
    renderer.SetBackground(colors.GetColor3d('BkgColor'))

    renderWindow.SetSize(640, 480)
    renderWindow.AddRenderer(renderer)

    interactor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    interactor.Start()

test_main()


