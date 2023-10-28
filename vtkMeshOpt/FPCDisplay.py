import vtk
# from vtkMeshOpt.vtkSectorGenerator import visAngleBySector
from vtkMeshOpt.MeshLoader import MeshLoader
from vtkMeshOpt.hisGen import histGen
# from vtkMeshOpt.ConeGenerator import visCornerByCone
from vtkMeshOpt.CollisionDetection import StarSystem
from vtkMeshOpt.qualityEdges import qualityEdges
from meshStructure.meshDS import meshDS
from vtkMeshOpt.meshQualityMarker import meshVertexQualityMarker
from vtkMeshOpt.utility import vlToVTKLinePolyData
# from vtkMeshOpt.localElementMatrix import getVertexQualityMatrix
from boundaryErrorVis.bndErrorVisUtility import vfToVTKActor
from boundaryErrorVis.echartsComponent import echartsBar
import numpy as np
from tqdm import tqdm

class FPCDisplayObj(MeshLoader):
    def __init__(self, file_path, _MaxRadius = 0.1):
        self.RawDataPath = file_path
        self.loadvtkUnstructuredGrid()
        self.cellList_vtk2np()
        
        print("number of vertices : ")
        print(len(self.generateNpPoints()))
        print("number of cells : ")
        print(len(self.cellList))

        self.flag3D = self.detect3DGraphic()

        self.buildMeshDataStructure()

        self.MaxRadius = _MaxRadius # shpere size
        self.ShpereRadiiTh = 0.0 # threshold
        self.featureEdgeThreshold = 0.0

        # all quality mark include cluster sphere and vertex sphere are generate in this class
        # data type : dictionary of index, ratio, radiiRatio and actors
        self.qualityMarker = meshVertexQualityMarker(self.mesh)

        # print(self.qualityMarker.qualityDict[0].cornerIndex)
        # print(self.qualityMarker.qualityDict[0].qualities)
        self.aggregateFlag = False

        self.actorColors = [[0.5, 0.5, 0.5], # actor color
                            [128/255, 0, 0], # selected actor color
                            [252/255, 140/255, 3/255] # selected corner color
                            ]
        self.actorColor = self.actorColors[0]

        self.pointsShpereDir = {}
        self.shpereSourceDir = {}
        self.genStarMapActorsDir()
    
    def buildMeshDataStructure(self):
        points = self.nppoints
        cells = self.cellList

        print("DS start build.....")
        if self.flag3D:
            self.mesh = meshDS(points, cells, "Hex")
        else:
            self.mesh = meshDS(points, cells, "Quad")
        self.mesh.build()

    def setColors(self, colors):
        self.actorColors = colors
        self.actorColor = colors[0]

    def detect3DGraphic(self):
        return not np.all(self.nppoints[:, 2] == 0) 

    def updateMaxRadius(self, _radius):
        self.MaxRadius = _radius
        self.pointsShpereDir = {}
        self.shpereSourceDir = {}
        self.genStarMapActorsDir()

    def aggregatedGlyph(self, flag):
        self.aggregateFlag = flag
        self.starSystem = StarSystem(len(self.nppoints), self.shpereSourceDir, self.MaxRadius, self.actorColors[0],
                                     self.aggregateFlag, self.flag3D, self.ShpereRadiiTh)

    def basedObjActor(self, _colors=None):
        actors = []
        ugrid = self.vtkReader
        edges = self.extractEdges(ugrid)
        mapper = self.createDataSetMapper(edges, False)
        actor = self.createActor(mapper=mapper)
        actor.GetProperty().SetLineWidth(2.0)
        
        if _colors:
            qualityEdgesObj = qualityEdges(self.mesh, self.qualityMarker.qualityDict,
                                           self.vtkpoints, _colors, _Threshold=self.featureEdgeThreshold)
            emapper = self.createPolyDataMapper(qualityEdgesObj.qualityEdgeData, True)
            eactor = self.createActor(mapper=emapper)
            if self.featureEdgeThreshold == 1:
                eactor.GetProperty().SetLineWidth(2.0)
                actor.GetProperty().SetOpacity(0.05)
                actors.append(eactor)
            else:
                eactor.GetProperty().SetLineWidth(4.0)
                actor.GetProperty().SetOpacity(0.05)
                # actor.GetProperty().SetOpacity(0.03)
                actors.append(eactor)
        if self.flag3D == False:
            actor.GetProperty().SetOpacity(0.2)
        actors.append(actor)

        return actors

    def genStarMapActorsDir(self):
        print("building vertex glyph dict ...")
        point_ratios_dir = self.qualityMarker.qualityDict
        for pointI in tqdm(point_ratios_dir):
            sphereRadiiRatio = point_ratios_dir[pointI].radiiRatio

            actor, sphereSourceRatio = self.createSphere(sphereRadiiRatio, pointI)
            self.addActorToPointsShpereDir(pid=pointI, actor=actor)
            self.addSphereSourceRatioToDir(pid=pointI, sphereRatio=sphereSourceRatio)
        self.starSystem = StarSystem(len(self.nppoints), self.shpereSourceDir, self.MaxRadius, self.actorColors[0],
                                     self.aggregateFlag, self.flag3D, self.ShpereRadiiTh)
        print("vertex glyph dict --- done ...")
        # self.genStarSystemActors()
    
    def BasicGraphic(self, _bFlag):
        starMapActorsDir = self.starSystem.groupStarsDir
        actors = []
        if _bFlag:
            actors.extend(self.basedObjActor())
        else:
            actors.extend(self.basedObjActor(self.starSystem.pcolors))
        histActor = self.displayHistogram(starMapActorsDir.keys(), _clusterFlag = True)
        actors.extend(histActor)
        return actors

    def genStarMapActors(self, selectedPid, _bFlag):
        starMapActorsDir = self.starSystem.groupStarsDir

        basicActor = self.BasicGraphic(_bFlag)
        # no point is selected in the beginning.
        if selectedPid >= 0:
            selectedSphereActor = self.createSphere(0.5, selectedPid)[0]
            selectedSphereActor.GetProperty().SetColor(self.actorColors[1])

            actors = [selectedSphereActor]
        else:
            actors = []

        if _bFlag:
            actors.extend(basicActor)
            return actors

        # locatedPid = self.starSystem.locatePointIndexInDir(selectedPoint=selectedPid)
        for pid in starMapActorsDir:
            actorList = starMapActorsDir[pid]["actor"]
            pRatio = starMapActorsDir[pid]["ratio"]  
            radii = pRatio * self.MaxRadius    
            if radii >= self.ShpereRadiiTh / 10:
                actors.extend(actorList)

        actors.extend(basicActor)
        return actors

    def genStarMapActorsWithoutClusting(self, selectedPid, _bFlag):
        actors = []
        for pointIndex in self.pointsShpereDir:
            actor = self.pointsShpereDir[pointIndex]
            # pRatio = self.shpereSourceDir[pointIndex]["Ratio"]
            # if selectedPid == pointIndex:
            #     actor[0].GetProperty().SetColor(self.actorColors[1])
            actors.extend(actor)
        
        basicActors = self.BasicGraphic(_bFlag)
        if _bFlag:
            return basicActors
        else:
            actors.extend(basicActors)
            return actors

    def subStarBasicActors(self, _subCells, _ids, _colorFlag):
        actors = []
        tmpCells = set(tuple(e) for e in _subCells)
        uniqueCells = [list(t) for t in tmpCells]
        polyActor = self.cellListToPolygon(uniqueCells, _colorFlag)
        actors.append(polyActor)
        histActor = self.displayHistogram(_ids)
        actors.extend(histActor)
        return actors

    def subStarMapActors(self, pid, _bFlag):
        locatedPid = self.starSystem.locatePointIndexInDir(selectedPoint=pid)
        pids = self.starSystem.groupStarsDir[locatedPid]["list"]
        ids = []
        subCells = []
        for p in pids:
            cells, sub_ids = self.subCellListAndPoins(p)
            subCells.extend(cells)
            ids.extend(sub_ids)
        
        basicActors = self.subStarBasicActors(subCells, ids, not _bFlag)

        radii = self.mesh.get_vert_neighbor_edge_average_len(pid)
        pRatio = (0.2 * radii) / self.MaxRadius
        selectedSphereActor = self.createSphere(pRatio, pid)[0]
        selectedSphereActor.GetProperty().SetColor(self.actorColors[1])
        actors = [selectedSphereActor]
        # actors = []

        if _bFlag:
            actors.extend(basicActors)
            return actors

        for pointIndex in ids:
            actor = self.pointsShpereDir[pointIndex]
            pRatio = self.shpereSourceDir[pointIndex]["Ratio"]
            radii = pRatio * self.MaxRadius    
            if radii >= self.ShpereRadiiTh / 10:
                actors.extend(actor)
        
        actors.extend(basicActors)
        return actors

    def createConnectionPoly(self, pid, _sectorFlag = False, _opacity = 1):
        actorList = []

        radii = self.mesh.get_vert_neighbor_edge_average_len(pid)
        pRatio = (0.2 * radii) / self.MaxRadius

        selectedSphereActor = self.createSphere(pRatio, pid)[0]
        selectedSphereActor.GetProperty().SetColor(self.actorColors[1])
        actorList.append(selectedSphereActor)

        subCellList, ids = self.subCellListAndPoins(pid)
        if _sectorFlag:
            actor = self.cellListToPolygon(subCellList, not _sectorFlag)
        else:
            actor = self.cellListToPolygon(subCellList)
        actor.GetProperty().SetOpacity(_opacity) # BUG: opacity could not be changed out side this function.
        actors = self.displayHistogram([pid])
        actorList.extend(actors)
    
        actorList.append(actor)
        return actorList

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

    def subCellListAndPoins(self, pid):
        subCellList = self.cellListFilter(pid)
        uniqueIds = self.remove_duplicates(subCellList)
        return subCellList, uniqueIds

    def remove_duplicates(self, subLists):
        mergedlist = []
        for cell in subLists:
            mergedlist.extend(cell)
        return list(set(mergedlist))

    def cellListFilter(self, pid):
        # return a list which contain pid in each cell.
        targetCellList = []
        for cell in self.cellList:
            if pid in cell:
                targetCellList.append(cell)
        return targetCellList

    def cellListToPolygon(self, _cellList, _visColors = True):
        polygons = self.createCellArray(_cellList)
        polygonData = vtk.vtkPolyData()
        polygonData.SetPoints(self.vtkpoints)
        polygonData.SetPolys(polygons)
        polygonData.GetPointData().SetScalars(self.starSystem.pcolors_a1)
        polygonData.SetPoints(self.vtkpoints)
        mapper = self.createPolyDataMapper(polygonData, _visColors = _visColors)
        actor = self.createActor(mapper=mapper)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetLineWidth(3.0)
        # if self.flag3D:
        actor.GetProperty().SetRepresentationToWireframe()
        return actor

    def addActorToPointsShpereDir(self, pid, actor):
        if pid not in self.pointsShpereDir.keys():
            self.pointsShpereDir[pid]=[]
        self.pointsShpereDir[pid].append(actor)
    
    def addSphereSourceRatioToDir(self, pid, sphereRatio):
        if pid not in self.shpereSourceDir.keys():
            self.shpereSourceDir[pid]={"sphereSource":[], "Ratio":[]}
        self.shpereSourceDir[pid]["sphereSource"] = sphereRatio[0]
        self.shpereSourceDir[pid]["Ratio"] = sphereRatio[1]

    def genStarSystemActors(self):
        for sid in self.starSystem.groupStarsDir.keys():
            pIndex = self.starSystem.groupStarsDir[sid]["list"][0]
            ratio = self.starSystem.groupStarsDir[sid]["ratio"]
            sactor, _ = self.createSphere(ratio=ratio, pIndex=pIndex)
            self.starSystem.groupStarsDir[sid]["actor"].append(sactor)

    def createSphere(self, ratio, pIndex):
        center = self.getPointCoord(pIndex)
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(center)

        Radius = self.ratioWatchDog(ratio=ratio)
        sphereSource.SetRadius(Radius)

        sphereSource.SetPhiResolution(50)
        sphereSource.SetThetaResolution(50)

        mapper = self.createPolyDataConnectionMapper(sphereSource)
        actor = self.createActor(mapper=mapper)
        actor.GetProperty().SetOpacity(0.4) # sphere Opacity
        return actor, [center, ratio]
    
    def createPolyDataConnectionMapper(self, vtkSource):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(vtkSource.GetOutputPort())
        mapper.ScalarVisibilityOff()
        return mapper

    def createPolyDataMapper(self, vtkSource, _visColors = False):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(vtkSource)
        if not _visColors:
            mapper.ScalarVisibilityOff()
        else:
            # do not display the color on points.
            mapper.ScalarVisibilityOn()
            mapper.SelectColorArray('pointColors')
            mapper.SetScalarModeToUsePointFieldData()
            mapper.SetColorModeToDirectScalars()
        return mapper

    def extractEdges(self, vtkAlgorithm):
        edges = vtk.vtkExtractEdges()
        edges.SetInputConnection(vtkAlgorithm.GetOutputPort())
        return edges

    def createDataSetMapper(self, vtkSource, _visColors = False):
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(vtkSource.GetOutputPort())
        if not _visColors:
            mapper.ScalarVisibilityOff()
        else:
            # do not display the color on points.
            mapper.ScalarVisibilityOn()
            mapper.SelectColorArray('pointColors')
            mapper.SetScalarModeToUsePointFieldData()
            mapper.SetColorModeToDirectScalars()
        return mapper
    
    def createActor(self, mapper):
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(self.actorColor)
        # actor.GetProperty().SetOpacity(1)
        return actor

    def setActorColorBack(self, pid):
        actorList = self.pointsShpereDir[pid]
        for actor in actorList:
            actor.GetProperty().SetColor(self.actorColor)

    def setAllActorColorBack(self):
        print("setting all vertices glyph color back ...")
        for pid in tqdm(self.pointsShpereDir):
            actorList = self.pointsShpereDir[pid]
            for actor in actorList:
                actor.GetProperty().SetColor(self.actorColor)
                # actor.GetProperty().SetVisibility(1)
        print("setting all group glyph color back ...")
        for pid in self.starSystem.groupStarsDir:
            actorList = self.starSystem.groupStarsDir[pid]["actor"]
            for actor in actorList:
                actor.GetProperty().SetColor(self.actorColor)
                # actor.GetProperty().SetVisibility(1)

    def allVertexQualityToeChartsBar(self):
        # tableData = {_vi:[cornerIndex, cornerQuality]}
        vids = self.qualityMarker.qualityDict
        ratios = [self.qualityMarker.qualityDict[pi].minQuality for pi in vids]
        htmlName = "AllVertexQuality.html"
        title = "All Vertices"
        # echart need [names, xlabels, ydata]
        names = ["Vertex's Minimum Scaled Jacobian"]
        y, x = zip(*sorted(zip(ratios, vids), reverse = True)) # sort list based on ratios and from big to small.
        xlabels = [str(v) for v in x]
        ydata = [y]
        echartData = [names, xlabels, ydata]
        # print(echartData)
        # print(echartData)

        echartBarObj = echartsBar(htmlName, title, echartData, funcIndex = 2)
        echartBarObj.render()
        return echartBarObj

    def localQualityToeChartsBar(self, pid):
        # tableData = {_vi:[cornerIndex, cornerQuality]}
        vertexQuality = self.qualityMarker.qualityDict[pid]
        htmlName = "LocalQuality.html"
        title = "Vertex - " + str(pid)
        # echart need [names, xlabels, ydata]
        qualities = vertexQuality.qualities
        conerVids = vertexQuality.cornerIndex
        x = [str(x) for x in conerVids]
        y = qualities
        sy, sx = zip(*sorted(zip(y, x), reverse = True))
        names = [str(pid)]
        xlabels = sx
        ydata = [sy]
        echartData = [names, xlabels, ydata]
        # print(echartData)
        # print(echartData)

        echartBarObj = echartsBar(htmlName, title, echartData, funcIndex = 1)
        echartBarObj.render()
        return echartBarObj

    def displayHistogram(self, ids, _clusterFlag = False):
        # add bar chart for each Render....
        metricDir = {}
        idList = []
        average_metric = 0
        total_num = 0
        if _clusterFlag:
            for id in ids:
                tmp = self.starSystem.groupStarsDir[id]["list"]
                idList.extend(tmp)
        else:
            idList = ids
        for id in idList:
            idMetrics = self.qualityMarker.qualityDict[id].qualities
            for mv in idMetrics:
                mv = round(mv, 2)
                average_metric += mv
                total_num += 1

                if mv not in metricDir.keys():
                    metricDir[mv] = 1
                else:
                    metricDir[mv] += 1
        if _clusterFlag:
            print("Avergae of histgram quality :")
            print(average_metric / total_num)
        hg = histGen(metricDir)
        return hg.histActor

    def createCornerActor(self, _f):
        v = self.mesh.pointList
        lf = _f.replace("[", "")
        rf = lf.replace("]", "")
        vids = list(map(int, rf.split()))
        npvids = np.array(vids)

        f = []
        lines = []
        if len(vids) == 4:
            faces = [[0,1,2], [0,1,3], [0,2,3]]
            lids = [[0, 1], [0, 3], [0, 2]]
            for fi in faces:
                f.append(list(npvids[fi]))
        else:
            lids = [[0, 1], [2, 1]]
            f.append(vids)
        
        for l in lids:
            lines.append(list(npvids[l]))

        lineActor = self.linesToVTKActor(lines=lines)

        actor = vfToVTKActor(v, f)
        actor.GetProperty().SetColor(self.actorColors[2])

        return [actor, lineActor]

    def linesToVTKActor(self, lines):
        # input is line list [[vid1, vid2], ...]
        # output is a vtk actor
        linePolyData = vlToVTKLinePolyData(self.vtkpoints, lines)
        mapper = self.createPolyDataMapper(linePolyData)
        actor = self.createActor(mapper)
        actor.GetProperty().SetLineWidth(10.0)
        actor.GetProperty().SetOpacity(1)
        return actor

    def ratioWatchDog(self, ratio):
        if ratio < 0.001:
            Radius = 0.001 * self.MaxRadius
        # elif ratio > 1:
        #      Radius = self.MaxRadius
        else:
            Radius = ratio * self.MaxRadius
        return Radius

