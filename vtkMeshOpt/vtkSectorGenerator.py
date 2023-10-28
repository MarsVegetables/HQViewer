import vtk
from vtkMeshOpt.MeshLoader import MeshLoader
from vtkMeshOpt.utility import valueToRGB
from vtkMeshOpt.quadMetric import Quad_ScaledJacobian
# from MeshLoader import MeshLoader
# from utility import valueToRGB
import math
import numpy as np
from tqdm import tqdm
from vtkMeshOpt.localViewMarker import overlappingPointCircle, overlappingEdgeMarker

class SectorGenerator:
    '''
        This function is used to generate a sector.
    '''
    def __init__(self, center=(0,0,0), point1=(1,0,0), point2=(0,1,0), _maxRadius = 1, _inputRatio = 1):
        '''
        setup center, point1, and point2
        '''
        self.maxRadius = _maxRadius
        self.center = center # (0,0,0)
        self.point1 = point1 # (1,0,0)
        self.point2 = point2 # (0,1,0)
        # self.balanceSideBasedOnElement()
        # self.updateRadius(0.5)
        self.ratio = _inputRatio
        # ratio should be [-1, 1]
        if self.ratio < 0:
            self.mainArc = True
            self.rgb = valueToRGB(self.ratio)
            self.ratio = (abs(self.ratio) + 1) / 2
        else:
            self.mainArc = False
            if self.ratio <= 1:
                self.ratio = (1 - self.ratio) / 2
            self.rgb = valueToRGB(self.ratio)
        # self.martic_value = _inputRatio
        # self.updateBasedOnAngle()

    def updateRadius(self, lamb):
        '''
            use lamb to control the length of side.
        '''
        side1_x = self.point1[0] - self.center[0]
        side1_y = self.point1[1] - self.center[1]
        side1_z = self.point1[2] - self.center[2]
        side2_x = self.point2[0] - self.center[0]
        side2_y = self.point2[1] - self.center[1]
        side2_z = self.point2[2] - self.center[2]

        self.point1[0] = lamb * side1_x + self.center[0]
        self.point1[1] = lamb * side1_y + self.center[1]
        self.point1[2] = lamb * side1_z + self.center[2]
        self.point2[0] = lamb * side2_x + self.center[0]
        self.point2[1] = lamb * side2_y + self.center[1]
        self.point2[2] = lamb * side2_z + self.center[2]
        
    def calAngle(self):
        '''
            calculate angle based on the coordinates.
        '''
        side1_x = self.point1[0] - self.center[0]
        side1_y = self.point1[1] - self.center[1]
        side1_z = self.point1[2] - self.center[2]
        side2_x = self.point2[0] - self.center[0]
        side2_y = self.point2[1] - self.center[1]
        side2_z = self.point2[2] - self.center[2]
        vector_1 = np.array([side1_x, side1_y, side1_z])
        vector_2 = np.array([side2_x, side2_y, side2_z])
        unit_v1 = vector_1 / np.linalg.norm(vector_1)
        unit_v2 = vector_2 / np.linalg.norm(vector_2)
        dot_product = np.dot(unit_v1, unit_v2)
        angle = 180 * np.arccos(np.clip(dot_product, -1.0, 1.0)) / math.pi
        self.angle = angle
        return angle

    def balanceSide(self):
        '''
            The Radius shold equal to the maximum radius
        '''
        side1_x = self.point1[0] - self.center[0]
        side1_y = self.point1[1] - self.center[1]
        side1_z = self.point1[2] - self.center[2]
        side1_line = math.sqrt(side1_x**2 + side1_y**2 + side1_z**2)
        side2_x = self.point2[0] - self.center[0]
        side2_y = self.point2[1] - self.center[1]
        side2_z = self.point2[2] - self.center[2]
        side2_line = math.sqrt(side2_x**2 + side2_y**2 + side2_z**2)
        # print(side1_line)
        # print(side2_line)
        if side1_line != self.maxRadius:
            if side1_line == 0:
                side_ratio = 0
            else:
                side_ratio = self.maxRadius/side1_line
            # print(side_ratio)
            self.point1[0] = side_ratio * side1_x + self.center[0]
            self.point1[1] = side_ratio * side1_y + self.center[1]
            self.point1[2] = side_ratio * side1_z + self.center[2]
        if side2_line != self.maxRadius:
            if side2_line == 0:
                side_ratio = 0
            else:
                side_ratio = self.maxRadius/side2_line
            # print(side_ratio)
            self.point2[0] = side_ratio * side2_x + self.center[0]
            self.point2[1] = side_ratio * side2_y + self.center[1]
            self.point2[2] = side_ratio * side2_z + self.center[2]

    def balanceSideBasedOnElement(self):
        '''
            The Radius shold equal to the maximum radius
        '''
        side1_x = self.point1[0] - self.center[0]
        side1_y = self.point1[1] - self.center[1]
        side1_z = self.point1[2] - self.center[2]
        side1_line = math.sqrt(side1_x**2 + side1_y**2 + side1_z**2)
        side2_x = self.point2[0] - self.center[0]
        side2_y = self.point2[1] - self.center[1]
        side2_z = self.point2[2] - self.center[2]
        side2_line = math.sqrt(side2_x**2 + side2_y**2 + side2_z**2)
        # print(side1_line)
        # print(side2_line)
        if side1_line > side2_line:
            side_ratio1 = 0.5 * side2_line/side1_line
            side_ratio2 = 0.5
            
        if side1_line <= side2_line:
            side_ratio1 = 0.5
            side_ratio2 = 0.5 * side1_line/side2_line
        self.point1[0] = side_ratio1 * side1_x + self.center[0]
        self.point1[1] = side_ratio1 * side1_y + self.center[1]
        self.point1[2] = side_ratio1 * side1_z + self.center[2]
        self.point2[0] = side_ratio2 * side2_x + self.center[0]
        self.point2[1] = side_ratio2 * side2_y + self.center[1]
        self.point2[2] = side_ratio2 * side2_z + self.center[2]

    def createMapperUseConnection(self, polydata):
        polyMapper = vtk.vtkDataSetMapper()
        polyMapper.SetInputConnection(polydata.GetOutputPort())
        polyMapper.ScalarVisibilityOff()
        return polyMapper
    
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
        actor.GetProperty().SetEdgeColor([0,0,0])
        actor.GetProperty().SetColor(self.rgb)
        return actor
    
    def createCellArray(self, PointNum):
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(PointNum)
        for x in range(PointNum):
            polygon.GetPointIds().SetId(x,x)
        
        polygons = vtk.vtkCellArray()
        polygons.InsertNextCell(polygon)
        return polygons

    def createPoints(self, arcPoints):
        points = vtk.vtkPoints()
        points.SetData(arcPoints.GetPoints().GetData())
        points.InsertNextPoint(self.center)
        # points.InsertNextPoint(0.0, 2.0, 0.0)
        return points

    def createSectorBasedOnPoints(self):
        arcPolygon = self.createArc()

        points = self.createPoints(arcPolygon.GetOutput())
        pointNum = arcPolygon.GetOutput().GetNumberOfPoints()
        polygons = self.createCellArray(pointNum)

        polygonData = vtk.vtkPolyData()
        polygonData.SetPoints(points)
        polygonData.SetPolys(polygons)

        return polygonData

    def createArc(self):
        arcPolygon = vtk.vtkArcSource()

        arcPolygon.SetPoint1(self.point1)
        arcPolygon.SetPoint2(self.point2)
        arcPolygon.SetCenter(self.center)
        
        arcPolygon.SetResolution(50)
        arcPolygon.SetNegative(self.mainArc)
        arcPolygon.SetOutputPointsPrecision(vtk.vtkAlgorithm.SINGLE_PRECISION)
        arcPolygon.Update()
        return arcPolygon

    def createSector(self):
        self.balanceSide()
        self.updateRadius(self.ratio)

        sectorPolygon = self.createSectorBasedOnPoints()

        sectorMapper = self.createMapperUseData(sectorPolygon)
        sectorActor = self.createActor(sectorMapper)

        return sectorActor

class visAngleBySector(MeshLoader):
    '''
        To Do: if a angle is greater than 180 degrees, the color and sector need to be changed since I am using vector to calculate angle.
        To Do: change the method to evaluate the quality of a angle.
        
        current method only correctly polt a angle smaller than 180 degrees.
    '''
    def __init__(self, unstructuredGridReader, _maxRadius, _facesList = None):
        self.maxRadius = _maxRadius
        self.ugridReader = unstructuredGridReader
        self.vtkRawData = self.ugridReader.GetOutput()
        self.vtkpoints = self.vtkRawData.GetPoints()
        self.cells = self.vtkRawData.GetCells()
        self.cellList_vtk2np()
        # self.sectorActors = self.createSectors()
        self.point_sectors_ratios={}
        self.point_cells = {}
        self.facesList = _facesList
        if self.facesList:
            self.sectorActors = self.createSectorsAndColor4Faces()
        else:
            self.sectorActors = self.createSectorsAndColor()
        self.addOverlappingMarkActor()
    
    def updateMaxRadius(self, _newRadius):
        self.maxRadius = _newRadius
        self.point_sectors_ratios={}
        self.point_cells = {}
        if self.facesList:
            self.sectorActors = self.createSectorsAndColor4Faces()
        else:
            self.sectorActors = self.createSectorsAndColor()
        self.addOverlappingMarkActor()

    def createSectorsAndColor(self):
        cellColors = vtk.vtkFloatArray()
        cellColors.SetNumberOfComponents(4)
        cellColors.SetNumberOfTuples(len(self.cellList))
        cellColors.SetName("QualityRgb")

        meshActors = []
        for i, cell in enumerate(tqdm(self.cellList)):
            # print(cell)
            cellActors = self.createSectors4Cell(cell)
            meshActors.extend(cellActors)
            # i/len(self.cellList)
            rgbArray = [0.7, 0.2, 0.2, 1]
            cellColors.SetTuple(i, rgbArray)
        # self.vtkRawData.GetCellData().SetScalars(cellColors)
        return meshActors
    
    def createSectorsAndColor4Faces(self):
        faceColors = vtk.vtkFloatArray()
        faceColors.SetNumberOfComponents(4)
        faceColors.SetNumberOfTuples(len(self.facesList))
        faceColors.SetName("QualityRgb")

        meshActors = []
        for i, face in enumerate(tqdm(self.facesList)):
            # if 1 in face:
            #     print(face)
            faceActors = self.createSectors4Cell(face)
            if len(faceActors) == 0:
                continue
            meshActors.extend(faceActors)
            # i/len(self.cellList)
            rgbArray = [0.7, 0.2, 0.2, 1]
            faceColors.SetTuple(i, rgbArray)
        # self.vtkRawData.GetCellData().SetScalars(faceColors)
        return meshActors

    def createSectors(self):
        meshActors = []
        for cell in self.cellList:
            cellActors = self.createSectors4Cell(cell)
            meshActors.extend(cellActors)
        return meshActors

    def createSectors4Cell(self, cellArray):
        # save actors and ratios to point_sectors_ratios dir.
        actors = []
        opacity = 0
        self.set_quad_metric("scaled Jacobian")
        # not sure !!!
        ratio_cell = self.quad_metric.scaledJacobian_cell(cellArray)
        for center_i in cellArray:
            '''
            center_i : center index value in the cell array
            '''
            if self.detectDuplicateCell(center_i, cellArray):
                continue
            # print(center_i)
            p1_i, p2_i = self.getOtherPoints(center_i, cellArray)
            center = [0,0,0]
            p1 = [0,0,0]
            p2 = [0,0,0]
            self.vtkpoints.GetPoint(center_i, center)
            self.vtkpoints.GetPoint(p1_i, p1)
            self.vtkpoints.GetPoint(p2_i, p2)
            # print(center_i, p1_i, p2_i)
            pointIndexes = [center_i, p1_i, p2_i]
            points = [center, p1, p2]
            center_ratio = ratio_cell[cellArray.index(center_i)]

            sectorActor = np.NAN
            sectorGen = SectorGenerator(center=center, point1=p1, point2=p2, _maxRadius = self.maxRadius, _inputRatio = center_ratio)

            if not self.checkOverlapping(pointIndexes, points):
                # opacity = opacity + sectorGen.ratio
                sectorActor = sectorGen.createSector()
                actors.append(sectorActor)
            
            metric_bins = round(center_ratio, 2)
            self.addActorAndRatioToDir(center_i, sectorActor, sectorGen.ratio, metric_bins)
            self.avoidDuplicateCellsDir(center_i, cellArray)
        # opacity = opacity / len(cellArray)
        return actors # , opacity
    
    def addActorAndRatioToDir(self, pointIndex, actor, ratio, _metric_value):
        if pointIndex not in self.point_sectors_ratios.keys():
            self.point_sectors_ratios[pointIndex]={"actors":[], "ratios":[], "metric": [],\
                "overlappingPoints" : [], "overlappingEdges" : []}
        if actor is not np.NAN:
            self.point_sectors_ratios[pointIndex]["actors"].append(actor)
        self.point_sectors_ratios[pointIndex]["ratios"].append(ratio)
        self.point_sectors_ratios[pointIndex]["metric"].append(_metric_value)

    def avoidDuplicateCellsDir(self, pointIndex, _cell):
        if pointIndex not in self.point_cells.keys():
            self.point_cells[pointIndex]={"cells" : []}
        self.point_cells[pointIndex]["cells"].append(_cell)
    
    def detectDuplicateCell(self, pointIndex, _cell):
        if pointIndex in self.point_cells.keys():
            cellList = self.point_cells[pointIndex]["cells"]
            for cell in cellList:
                if set(cell) == set(_cell):
                    return True
        else:
            return False
            
    def set_quad_metric(self, _mIndex):
        if _mIndex == "scaled Jacobian":
            self.metric_min = -1
            self.metric_max = 1
            self.quad_metric = Quad_ScaledJacobian("FPC", [], self.generateNpPoints())
    
    def metric_bins(self, _mValue):
        metric_range = (self.metric_max - self.metric_min)
        norm_value = (_mValue - self.metric_min) / metric_range
        # (0 - 1) -> (0 - 100)
        bins = ((int(norm_value * 100) / 100) * metric_range + self.metric_min)
        return round(bins,2)

    def getOtherPoints(self, center, cellArray):
        node_index = cellArray.index(center)
        tmp1 = (node_index - 1)
        point1_index = tmp1 if tmp1 >= 0 else (len(cellArray) - 1)
        point1 = cellArray[point1_index]

        tmp2 = node_index + 1
        point2_index = tmp2 if tmp2 < len(cellArray) else 0
        point2 = cellArray[point2_index]

        return point1, point2
   
    def checkOverlapping(self, _pointIndexes, _points):
        # first check current overlapping points and overlapping edges indexes.
        # then based on the index list to generate mark.
        if _pointIndexes[0] not in self.point_sectors_ratios.keys():
            self.point_sectors_ratios[_pointIndexes[0]]={"actors":[], "ratios":[], "metric": [],\
                "overlappingPoints" : [], "overlappingEdges" : []}
        
        v1 = np.array(_points[1]) - np.array(_points[0])
        v2 = np.array(_points[2]) - np.array(_points[0])

        v1_len = np.sqrt(np.sum(v1 ** 2))
        v2_len = np.sqrt(np.sum(v2 ** 2))
        flag = False
        if v1_len == 0 and _pointIndexes[1] not in self.point_sectors_ratios[_pointIndexes[0]]["overlappingPoints"]:
            self.point_sectors_ratios[_pointIndexes[0]]["overlappingPoints"].append(_pointIndexes[1])
            flag = True
        if v2_len == 0 and _pointIndexes[2] not in self.point_sectors_ratios[_pointIndexes[0]]["overlappingPoints"]:
            self.point_sectors_ratios[_pointIndexes[0]]["overlappingPoints"].append(_pointIndexes[2])
            flag = True
        if v1_len != 0 and v2_len != 0: # overlapping edges
            cos = np.dot(v1, v2) / v1_len * v2_len
            if cos == 1 and _pointIndexes[1] not in self.point_sectors_ratios[_pointIndexes[0]]["overlappingEdges"] \
                and _pointIndexes[2] not in self.point_sectors_ratios[_pointIndexes[0]]["overlappingEdges"]:
                self.point_sectors_ratios[_pointIndexes[0]]["overlappingEdges"].extend(_pointIndexes[1:])
                flag = True
        return flag
    
    def addOverlappingMarkActor(self):
        for key in self.point_sectors_ratios:
            # overlapping points
            pNum = len(self.point_sectors_ratios[key]["overlappingPoints"])
            if pNum > 0:
                center = [0,0,0]
                self.vtkpoints.GetPoint(key, center)
                pointCircle = overlappingPointCircle(center=np.array(center), _maxRadius = self.maxRadius)
                pcActors = pointCircle.run(pNum + 1)
                self.point_sectors_ratios[key]["actors"].extend(pcActors)
            # overlapping edges
            eNum = len(self.point_sectors_ratios[key]["overlappingEdges"])
            if eNum > 0:
                cp = self.findFarestPoint(key, self.point_sectors_ratios[key]["overlappingEdges"])
                print(cp)
                barTopLine = overlappingEdgeMarker(center=np.array(cp[0]), point1=np.array(cp[1]), _maxRadius = self.maxRadius)
                barTopLineActors = barTopLine.run(eNum + 1)
                self.point_sectors_ratios[key]["actors"].extend(barTopLineActors)
                self.point_sectors_ratios[key]["actors"].append(barTopLine.showLine())
    
    def findFarestPoint(self, k, ids):
        center = [0,0,0]
        self.vtkpoints.GetPoint(k, center)
        farestP = []
        dis = 0
        for i in ids:
            p = [0,0,0]
            self.vtkpoints.GetPoint(i, p)
            v = np.array(p) - np.array(center)
            tmpDis = np.sqrt(np.sum( v ** 2))
            if tmpDis > dis:
                dis = tmpDis
                farestP = p
        return [center, farestP]

            