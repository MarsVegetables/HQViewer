'''
Date: 2020-12-17 16:53:19
LastEditors: Lei Si
LastEditTime: 2021-10-22 11:31:13
'''

import numpy as np
import vtk
import math
from tqdm import tqdm
import multiprocessing as mp
from multiprocessing.pool import Pool
import time

class StarSystem:
    def __init__(self, _NumberOfV, _sphereDir, _MaxRadius, _actorColor, _aggregateFlag, _meshType, _mini_radii):
        # self.shpereSourceDir[pid]={"sphereSource":[], "Ratio":[]} 
        # sphereSource is the coordinate of sphere.
        self.sphereDir = _sphereDir
        self.numberOfS = len(self.sphereDir.keys())
        self.numberOfV = _NumberOfV
        # self.baceObjActor = _baceObjActor
        self.MaxRadius = _MaxRadius
        self.actorColor = _actorColor
        self.groupStarsDir = {}

        self.meshType = 1 if _meshType else 0 # 0 quad, 1 hex
        self.aggregateFlag = _aggregateFlag
        self.minimum_radii = _mini_radii / 10
        self.actorAlphaThreshold = self.minimum_radii + 0.8
        
        # for cluster color
        self.colorPic = 0
        self.clusterColorList = [[230, 25, 75], [60, 180, 75], [255, 225, 25], 
        [0, 130, 200], [245, 130, 48], [145, 30, 180], 
        [70, 240, 240], [240, 50, 230], [210, 245, 60], 
        [250, 190, 212], [0, 128, 128], [220, 190, 255],
        [255, 250, 200], [170, 255, 195],[128, 128, 0], 
        [255, 215, 180], [0, 0, 128], [128, 255, 128]]

        self.buildGlyphDict()

    def colliDet(self, center0, r0, center1, r1):
        '''
            input requires the center coordinate, format : [x,y,z].
        '''
        dist = [(a - b)**2 for a,b in zip(center0, center1)]
        distanceBetween = math.sqrt(sum(dist))
        # print(distanceBetween)
        
        radius0 = self.ratioWatchDog(ratio=r0)
        radius1 = self.ratioWatchDog(ratio=r1)
        d = radius0 + radius1
        
        # print(d)
        intersectionFlag = distanceBetween - d
        if intersectionFlag < 0: # intersected when distanceBetween small than d
            return 1
        else:
            return 0
    
    def locatePointIndexInDir(self, selectedPoint):
        for sid in self.groupStarsDir.keys():
            if selectedPoint in self.groupStarsDir[sid]["list"]:
                return sid
        print("error not found, point : " + str(selectedPoint))
        return 1

    def findOverlappingGlyph(self, _pid):
        collisionSet = set([_pid])
        pids = [pid for pid in self.sphereDir.keys()]
        i = pids.index(_pid)
        center0 = self.sphereDir[_pid]["sphereSource"]
        ratio0 = self.sphereDir[_pid]["Ratio"]
        radii = ratio0 * self.MaxRadius
        # ShpereRadiiTh
        if radii <= self.minimum_radii:
            return set([-1])
        for rpid in pids[i:]:
            if rpid == _pid:
                continue
            center1 = self.sphereDir[rpid]["sphereSource"]
            ratio1 = self.sphereDir[rpid]["Ratio"]
            # radii = ratio1 * self.MaxRadius
            # if radii <= self.minimum_radii:
            #     continue
            if self.colliDet(center0=center0, r0=ratio0, center1=center1, r1=ratio1):
                collisionSet.add(rpid)
        return collisionSet

    def buildGlyphDict(self):
        # flag is True build Aggregated glyph
        if self.aggregateFlag:
            self.groupStars()
        else:
            self.singleStars()
        
    # groupOverlappingGlyph
    def singleStars(self):
        pids = self.sphereDir.keys()

        print("building non-aggregated glyph dict ...")

        uLists = [set([pid]) for pid in tqdm(pids)]

        for i, l in tqdm(enumerate(uLists)):
            self.addGroupRaioToDir(list(l), i)
        if self.meshType == 0:
            self.adjustRatioAndGenerateActor(0.5)
        else:
            self.adjustRatioAndGenerateActor(0.1)
        print("building non-aggregated glyph dict --- done ...")

    # groupOverlappingGlyph
    def groupStars(self):
        pids = self.sphereDir.keys()

        print("detecting collision ...")

        # https://tqdm.github.io/docs/contrib.concurrent/
        # https://leimao.github.io/blog/Python-tqdm-Multiprocessing/
        start_time = time.time()

        pool = Pool(mp.cpu_count() - 1)
        collisionList = pool.map(self.findOverlappingGlyph, [pid for pid in pids])
        pool.close()

        # collisionList = []
        # for pid in pids:
        #     collisionList.append(self.findOverlappingGlyph(pid))
        
        print(" --- %s seconds --- " % (time.time() - start_time))
        
        print("grouping vertex glyph ...")
        uLists = unionList(collisionList)
        i = 0
        for l in tqdm(uLists):
            y = list(l)
            if y[0] < 0:
                continue
            else:
                self.addGroupRaioToDir(list(l), i)
                i += 1
        if self.meshType == 0:
            self.adjustRatioAndGenerateActor(0.5)
        else:
            self.adjustRatioAndGenerateActor(0.05)
        print("vertex glyph group --- done ...")

    def addGroupRaioToDir(self, ulist, newId):
        ratio = 0
        for l in ulist:
            tmpRatio = self.sphereDir[l]["Ratio"]
            
            if tmpRatio > ratio:
                ratio = tmpRatio
            
            # if ratio < 1:
            #    ratio = ratio + tmpRatio
            
        if newId not in self.groupStarsDir.keys():
            self.groupStarsDir[newId]={"list":[], "ratio":0, "actor":[]}
        self.groupStarsDir[newId]["list"] = ulist
        # if the sum of this group is larger than 1, we will use 1 as based ratio.
        # after this ratio, we will add a precentage of number of vertex in this cluster.
        self.groupStarsDir[newId]["ratio"] = ratio # if ratio < 1 else 1
        
    def adjustRatioAndGenerateActor(self, _alpha):
        # generate self.pointColors here
        self.pointColors(_alpha)
        
        for nid in tqdm(self.groupStarsDir.keys()):
            ulist = self.groupStarsDir[nid]["list"]
            ratio = self.groupStarsDir[nid]["ratio"]
            if len(ulist) > 1:
                # print(ulist)

                # xyzList, minxyz = self.findMaxMin(ulist)
                # center = [(xyzList[i] * 0.5) + minxyz[i] for i in range(len(xyzList))] # center of bounding box.
                center = self.findAverageOfVerticesCoords(ulist)
                ncenter = self.findClosestPoint(ulist, center) # the point that closest the center of bounding box.

                # the wrost situation, the nRatio is 11.
                # sum of vertex ratio is larget than 1, and all vertices in same cluster.
                # 10% vertices in a cluster, the size will increase 1 * max radius.
                # nRatio = ratio + ((len(ulist) - 1) / (self.numberOfS - 1)) * 10
                # --------
                # Vnumber_percentage = ((len(ulist) - 1) / (self.numberOfS - 1))
                # if Vnumber_percentage < 0.1:
                #    adjustRatio = int(100 * Vnumber_percentage) * 0.3
                # else:
                #    adjustRatio = 3
                # -----------
                Vnumber_percentage = (len(ulist)/ 10)
                if Vnumber_percentage < 10:
                   adjustRatio = int(Vnumber_percentage) * 0.1
                else:
                   adjustRatio = 1
                nRatio = ratio + adjustRatio
                
                # change colors for all points in the ulist
                alpha = 1
                if nRatio < self.actorAlphaThreshold:
                    alpha = 0.1
                # if nRatio < 0.5:
                #     alpha = 0.1
                # else:
                #     if nRatio < self.actorAlphaThreshold:
                #         alpha = nRatio / 2

                if self.meshType == 0:
                    self.updatePointColors(ulist, 0.5)
                else:
                    self.updatePointColors(ulist, alpha)
                self.groupStarsDir[nid]["ratio"] = nRatio
                ratio = nRatio
            else:
                ncenter = self.sphereDir[ulist[0]]["sphereSource"]
            sector, _ = self.createSphere(ratio=ratio, _centerCoord=ncenter)
            self.groupStarsDir[nid]["actor"].append(sector)
    
    def findMaxMin(self, _ulist):
        centerList_x = []
        centerList_y = []
        centerList_z = []
        for pid in _ulist:
            centerCoord = self.sphereDir[pid]["sphereSource"]
            centerList_x.append(centerCoord[0])
            centerList_y.append(centerCoord[1])
            centerList_z.append(centerCoord[2])
        
        mx = max(centerList_x) # max x
        mix = min(centerList_x) # min x
        my = max(centerList_y)
        miy = min(centerList_y)
        mz = max(centerList_z)
        miz = min(centerList_z)

        return [mx - mix, my - miy, mz - miz], [mix,miy,miz]
    
    def findAverageOfVerticesCoords(self, _ulist):
        centerList_x = []
        centerList_y = []
        centerList_z = []
        for pid in _ulist:
            centerCoord = self.sphereDir[pid]["sphereSource"]
            centerList_x.append(centerCoord[0])
            centerList_y.append(centerCoord[1])
            centerList_z.append(centerCoord[2])
        
        nV = len(_ulist)
        aveX = sum(centerList_x) / nV 
        aveY = sum(centerList_y) / nV
        aveZ = sum(centerList_z) / nV

        return [aveX, aveY, aveZ]

    def findClosestPoint(self, _ulist, _bboxCenter):
        closestdis = math.inf
        closestPoint = []
        for pid in _ulist:
            centerCoord = self.sphereDir[pid]["sphereSource"]
            dis = self.p2pDistance(centerCoord, _bboxCenter)
            if dis <= closestdis:
                closestdis = dis
                closestPoint = centerCoord
        return closestPoint
    
    def p2pDistance(self, p1, p2):
        # point to point distance
        distanceBetween = 0
        for ind in range(len(p1)):
            distanceBetween = distanceBetween + (p1[ind] - p2[ind]) ** 2
        distanceBetween = math.sqrt(distanceBetween)
        return distanceBetween

    def calNewRatioForGroup(self, _xyzList):
        newRadius = 0
        for v in _xyzList:
            newRadius = newRadius + (v ** 2)
        newRadius = math.sqrt(newRadius) * 0.5
        if newRadius > self.MaxRadius:
            newRatio = newRadius/self.MaxRadius
        else:
            newRatio = 1
        return newRatio

    def ratioWatchDog(self, ratio):
        if ratio < 0.001:
            Radius = 0.001 * self.MaxRadius  
        # elif ratio > 1:
        #      Radius = self.MaxRadius
        else:
            Radius = ratio * self.MaxRadius
        return Radius

    def createSphere(self, ratio, _centerCoord):
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(_centerCoord)

        Radius = self.ratioWatchDog(ratio=ratio)
        sphereSource.SetRadius(Radius)

        sphereSource.SetPhiResolution(50)
        sphereSource.SetThetaResolution(50)

        mapper = self.createPolyDataConnectionMapper(sphereSource)
        if ratio > self.actorAlphaThreshold or not self.aggregateFlag or self.meshType == 0:
            actor = self.createActor(mapper=mapper, opacity = 0.6)
        else:
            actor = self.createActor(mapper=mapper, opacity = 0.05)
        return actor, [_centerCoord, ratio]
    
    def createPolyDataConnectionMapper(self, vtkSource):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(vtkSource.GetOutputPort())
        mapper.ScalarVisibilityOff()
        return mapper
    
    def createActor(self, mapper, opacity):
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(self.actorColor)
        actor.GetProperty().SetOpacity(opacity)
        return actor
    
    # set defult point colors and return the char array
    def pointColors(self, alpha):
        self.pcolors = vtk.vtkDoubleArray()
        self.pcolors.SetNumberOfComponents(4)
        self.pcolors.SetName("pointColors")
        c = [100,100,100, alpha]

        self.pcolors_a1 = vtk.vtkDoubleArray()
        self.pcolors_a1.SetNumberOfComponents(4)
        self.pcolors_a1.SetName("pointColors")
        c_a1 = [100,100,100, 1]

        for i in range(self.numberOfV):
            self.pcolors.InsertNextTypedTuple(c)
            self.pcolors_a1.InsertNextTypedTuple(c_a1)
    
    def updatePointColors(self, _plist, _opacity):
        self.colorPic = (self.colorPic + 1) % len(self.clusterColorList)
        for pid in _plist:
            self.changeSpecificPointColors(pid, _opacity)
        
    #change specific point's color based on the pid
    def changeSpecificPointColors(self, _pid, _opacity):
        rgba = self.clusterColorList[self.colorPic].copy()
        rgba.append(_opacity)
        # print(rgba)
        self.pcolors.SetTuple(_pid, rgba)


def unionList(_listContainer):
    # union section
    uList = np.array(_listContainer)
    for vids in tqdm(_listContainer):
        if len(vids) == 1:
            continue
        tmpUlist = uList.copy()
        removeMark = []
        unionSet = vids
        for i in range(len(uList)):
            tmpSet = uList[i]
            # if unionSet intersecting with tmpSet, new unionSet will have both set()
            unionResult = UnionOperation(unionSet, tmpSet)
            if unionResult:
                removeMark.append(i)
                unionSet = unionResult
        # remove intersecting sets
        tmpUlist = np.delete(tmpUlist, removeMark)
        # after for loop, all set() which intersecting with vids will become a new set() -> unionSet, 
        # and the intersecting sets will be removed.
        # so we need to add the intersecting set() back, to make sure new union operation will not miss any value.
        # then the new list is the unioned list
        uList = np.append(tmpUlist, unionSet)
    return list(uList)

def UnionOperation(_set1, _set2):
    Result = _set1.intersection(_set2)
    if len(Result) == 0:
        return False
    newSet = _set1.union(_set2)
    return set(newSet)




'''
renderWindow = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()
import time

def disPlayTest(baseActor, sphereSource1, sphereSource2):
    # Visualize
    mapper1 = vtk.vtkPolyDataMapper()
    mapper1.SetInputConnection(sphereSource1) # .GetOutputPort()
    mapper1.ScalarVisibilityOff()
    actor1 = vtk.vtkActor()
    actor1.SetMapper(mapper1)
    actor1.GetProperty().BackfaceCullingOn()
    actor1.GetProperty().SetRepresentationToWireframe()

    # Visualize
    mapper2 = vtk.vtkPolyDataMapper()
    mapper2.SetInputConnection(sphereSource2) # .GetOutputPort()
    mapper2.ScalarVisibilityOff()
    actor2 = vtk.vtkActor()
    actor2.SetMapper(mapper2)
    actor2.GetProperty().BackfaceCullingOn()
    actor2.GetProperty().SetRepresentationToWireframe()

    renderer = vtk.vtkRenderer()
    renderer.UseHiddenLineRemovalOn()
    renderer.AddActor(actor1)
    renderer.AddActor(actor2)
    renderer.AddActor(baseActor)
    renderer.UseHiddenLineRemovalOn()

    renderWindow.SetSize(640, 480)
    renderWindow.AddRenderer(renderer)

    interactor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    time.sleep(0.05)
    renderer.RemoveActor(actor1)
    renderer.RemoveActor(actor2)
    renderer.RemoveActor(baseActor)
    # renderWindow.Finalize()
    # interactor.Start()
    # interactor.GetRenderWindow().Finalize()
    # Stop the interactor
    # interactor.TerminateApp()
'''