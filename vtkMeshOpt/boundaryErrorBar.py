'''
Date: 2021-05-27 12:30:20
LastEditors: Lei Si
LastEditTime: 2021-06-15 16:47:39
'''
 
# feature point extraction method.
import vtk

class BoundaryErrorBar:
    def __init__(self, _bIndex, _oldPoints, _newPoints, _npBoundaryLines):
        # _bIndex is boundary index
        self.oldPoints = _oldPoints
        self.boundaryIndex = _bIndex
        self.npBoundaryLines = _npBoundaryLines
        self.newPoints = _newPoints
    
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

    def createVtkPoints(self):
        vtkpoints = vtk.vtkPoints()
        points = self.oldPoints
        for i in self.boundaryIndex:
            x = points[i]
            vtkpoints.InsertNextPoint(x)
        points = self.newPoints
        for i in self.boundaryIndex:
            x = points[i]
            vtkpoints.InsertNextPoint(x)
        return vtkpoints
    
    def createLine(self, _np):
        n = len(self.boundaryIndex)
        line = vtk.vtkLine()
        line.GetPointIds().SetNumberOfIds(2)
        line.GetPointIds().SetId(0, _np)
        line.GetPointIds().SetId(1, n + _np)
        return line
    
    def createLineByLineCell(self, _lineCell, _offset):
        line = vtk.vtkLine()
        line.GetPointIds().SetNumberOfIds(_lineCell[0])
        line.GetPointIds().SetId(0, _offset + _lineCell[1])
        line.GetPointIds().SetId(1, _offset + _lineCell[2])
        return line

    def createQuadByLineCell(self, _lineCell, _offset):
        quad = vtk.vtkQuad()
        quad.GetPointIds().SetId(0,_lineCell[1])
        quad.GetPointIds().SetId(1,_lineCell[2])
        quad.GetPointIds().SetId(2, _offset + _lineCell[2])
        quad.GetPointIds().SetId(3, _offset + _lineCell[1])
        return quad
    
    def createQuads(self):
        polygons = vtk.vtkCellArray()

        n = len(self.boundaryIndex)
        for lc in self.npBoundaryLines:
            line = self.createQuadByLineCell(lc, n)
            polygons.InsertNextCell(line)

        return polygons

    def createPolygon(self):
        polygons = vtk.vtkCellArray()

        n = len(self.boundaryIndex)
        for i in range(n):
            line = self.createLine(i)
            polygons.InsertNextCell(line)
        
        for lc in self.npBoundaryLines:
            line = self.createLineByLineCell(lc, 0)
            polygons.InsertNextCell(line)
        
        for lc in self.npBoundaryLines:
            line = self.createLineByLineCell(lc, n)
            polygons.InsertNextCell(line)
        return polygons

    def BoundaryPointActors(self, _pl, _points):
        colors = vtk.vtkNamedColors()
        sActors = []
        for pointI in _pl:
            point = _points[pointI]
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
        
    def BoundaryErrorPolygonActor(self):
        vPoints = self.createVtkPoints()
        # vPolygons = self.createPolygon()
        vQuads = self.createQuads()
        polygonPolyData =  vtk.vtkPolyData()
        polygonPolyData.SetPoints(vPoints)
        polygonPolyData.SetPolys(vQuads)
        mapper = self.createMapperUseData(polygonPolyData)
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
        actor.GetProperty().EdgeVisibilityOff()
        actor.GetProperty().SetColor([230/255, 25/255, 75/255])
        # actor.GetProperty().SetLineWidth(1.0)
        return actor

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

    fpfObj = BoundaryErrorBar(basicGraphic.boundaryPointIndexs,basicGraphic.generateNpPoints(),newGraphic.generateNpPoints(), basicGraphic.npBoundaryLines)

    # edges = vtk.vtkExtractEdges()
    # edges.SetInputConnection(basicGraphic.vtkReader.GetOutputPort())
    # mapper = vtk.vtkDataSetMapper()
    # mapper.SetInputConnection(edges.GetOutputPort())
    # mapper.ScalarVisibilityOff()
    # bgActor = vtk.vtkActor()
    # bgActor.SetMapper(mapper)
    # bgActor.GetProperty().SetOpacity(0.6)

    bdActor = fpfObj.BoundaryErrorPolygonActor()
    bdpActors = fpfObj.BoundaryPointActors(fpfObj.boundaryIndex, fpfObj.oldPoints)
    bdpActors2 = fpfObj.BoundaryPointActors(fpfObj.boundaryIndex, fpfObj.newPoints)
    # Visualize
    renderer = vtk.vtkRenderer()
    renderer.AddActor(bdActor)
    bpFlag = False
    if bpFlag:
        for a in bdpActors:
            renderer.AddActor(a)
        for a in bdpActors2:
            renderer.AddActor(a)
    renderer.SetBackground(colors.GetColor3d('BkgColor'))

    renderWindow.SetSize(640, 480)
    renderWindow.AddRenderer(renderer)

    interactor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    interactor.Start()

'''
# test_main()
