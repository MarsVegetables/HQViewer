'''
Date: 2021-06-10 00:36:19
LastEditors: Lei Si
LastEditTime: 2021-06-10 14:29:55
'''
 
import vtk

class QuadHexaPolygenGenerator:
    def __init__(self, _name, _coord, _actorColor, _opacity = 0.6, _3dFlag = False):
        self.name = _name
        self.flag3D = _3dFlag
        self.coord = _coord
        self.actorColor = _actorColor
        self.opacity = _opacity
        self.vtkPoints = self.npPointsToVTKPoints()

    def createCellArray(self, cellList):
        polygons = vtk.vtkCellArray()
        for cell in cellList:
            if self.flag3D:
                polygon = vtk.vtkHexahedron()
            else:
                polygon = vtk.vtkPolygon()
            PointNum = len(cell)
            polygon.GetPointIds().SetNumberOfIds(PointNum)
            for i, x in enumerate(cell):
                polygon.GetPointIds().SetId(i,x)
            if self.flag3D:
                for i in range(polygon.GetNumberOfFaces()):
                    # print(i)
                    face = polygon.GetFace(i)
                    polygons.InsertNextCell(face)
            else:
                polygons.InsertNextCell(polygon)
            # polygons.append(polygon)
        return polygons
        
    def createPolygonActor(self, _cellList):
        polygons = self.createCellArray(_cellList)
        polygonData = vtk.vtkPolyData()
        polygonData.SetPoints(self.vtkPoints)
        polygonData.SetPolys(polygons)
        mapper = self.createPolyDataMapper(polygonData)
        actor = self.createActor(mapper=mapper)
        return actor
    
    def createPolyDataMapper(self, vtkSource):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(vtkSource)
        mapper.ScalarVisibilityOff()
        return mapper
    
    def createActor(self, mapper):
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(self.actorColor)
        actor.GetProperty().SetOpacity(self.opacity)
        return actor
    
    def npPointsToVTKPoints(self):
        vtkpoints = vtk.vtkPoints()
        for x in self.coord:
            vtkpoints.InsertNextPoint(x)
        return vtkpoints