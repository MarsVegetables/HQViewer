'''
Date: 2021-08-25 00:29:00
LastEditors: Lei Si
LastEditTime: 2021-10-20 20:04:30
'''

import vtk
import numpy as np 
from boundaryErrorVis.bndErrorVisUtility import normalizeV
from boundaryErrorVis.bndErrorVisUtility import QTChartView
from vtk.util.numpy_support import vtk_to_numpy

# 2d hausdorff distance
class boundaryErrorVis2D:
    def __init__(self, _samepleModel, _samepleVtkReader, _targetModel, _targetVtkReader) -> None:
        # sample model and target model are meshDS object.
        self.m1 = _samepleModel
        self.m2 = _targetModel
        self.samepleVtkReader = _samepleVtkReader
        self.targetVtkReader = _targetVtkReader
        self.getBoundingBoxDiagonal()

    def boundaryToPointIndexList(self, _boundaryEids, _modelDS):
        boundaryList = set()
        for e in _boundaryEids:
            for v in _modelDS.Edges[e].Vids:
                boundaryList.add(v)
        return list(boundaryList)

    def boundarySeqSet(self):
        remainBndEids = self.m1.getBoundaryEdgeIds()
        bndSeqSet = []
        while len(remainBndEids) > 0:
            currentEid = remainBndEids.pop()
            remainBndEids, bndSeq = self.boundarySeqIter(currentEid, remainBndEids, [currentEid])
            bndSeqSet.append(bndSeq)
        return bndSeqSet  

    def boundarySeqIter(self, _eid, _bndEids, _bndSeq):
        remainderBndEids = _bndEids
        bndSeq = _bndSeq
        nEids = self.m1.Edges[_eid].neighboring_Eids
        for e in nEids:
            if e in remainderBndEids:
                if e not in bndSeq:
                    bndSeq.append(e)
                    remainderBndEids.remove(e)
                    remainderBndEids, bndSeq = self.boundarySeqIter(e, remainderBndEids, bndSeq)
        return remainderBndEids, bndSeq

    def getBoundingBoxDiagonal(self):
        x = self.m1.pointList[:, 0]
        y = self.m1.pointList[:, 1]
        minx = min(x)
        maxx = max(x)
        miny = min(y)
        maxy = max(y)
        self.diagonal = np.sqrt((maxx - minx)**2 + (maxy - miny) ** 2)
        return self.diagonal

    def pointDistanceFilter(self):
        # if sample vertex is inside target model, the distance is positive
        # if vertex is outside model, the distance is negetive.
        samplePoly = self.UnstructureGridToPolyData(self.samepleVtkReader)
        targetPoly = self.UnstructureGridToPolyData(self.targetVtkReader)

        distanceFilter = vtk.vtkDistancePolyDataFilter()
        distanceFilter.SetInputData(0, samplePoly.GetOutput())
        distanceFilter.SetInputData(1, targetPoly.GetOutput()) # surface that want to compare.
        distanceFilter.Update()
        return distanceFilter

    def UnstructureGridToPolyData(self, _ugridReader):
        polydata = vtk.vtkGeometryFilter()
        polydata.SetInputData(_ugridReader.GetOutput())
        polydata.Update()
        return polydata

    def getDistanceForPoints(self):
        distanceDict = {}
        sample_boundary_Eids = self.m1.getBoundaryEdgeIds()
        vids = self.boundaryToPointIndexList(sample_boundary_Eids, self.m1)
        
        target_boundary_Eids = self.m2.getBoundaryEdgeIds()
        tvids = self.boundaryToPointIndexList(target_boundary_Eids, self.m2)

        for v in vids:
            minDis = np.Infinity
            for tv in tvids:
                dis = self.findClosestPointAndDistance(v, tv)
                if dis < minDis:
                    minDis = dis
            distanceDict[v] = minDis
        return distanceDict

    def findClosestPointAndDistance(self, vid, tvid):
        sampleCoord = self.m1.pointList[vid]
        targetCoord = self.m2.pointList[tvid]
        vector = sampleCoord - targetCoord
        return np.linalg.norm(vector)

    def pointDisToPercentage(self):
        distanceDict = self.getDistanceForPoints()

        distaceFilter = self.pointDistanceFilter()
        disFilterScalars = vtk_to_numpy(distaceFilter.GetOutput().GetPointData().GetScalars())
        
        dia = self.getBoundingBoxDiagonal()
        dia_10p = dia * 1
        max_i = dia_10p
        min_i = 0

        disPercentage = {}
        for vid, dis in distanceDict.items():
            s = disFilterScalars[vid]
            s = 1 if s < 0 else -1
            disPercentage[vid] = s * normalizeV(dis, max_i, min_i)
        return disPercentage
    
    def createLine(self, _p1, _p2, color, _w = 0.1):
        """
        Creates a line to connect vertices
        :param point1: first vertex
        :param point2: second vertex
        :param color: color of line
        :return actor: line actor
        """

        '''
        vtkLineSource is a source object that creates a polyline defined by two endpoints or a collection of 
        connected line segments. To define the line by end points, use SetPoint1 and SetPoint2 methods. To define a 
        broken line comprising of multiple line segments, use SetPoints to provide the corner points that for the line.
        '''
        line_src = vtk.vtkLineSource()
        line_src.SetPoint1(_p1)
        line_src.SetPoint2(_p2)

        ''' Create a mapper for line '''
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(line_src.GetOutputPort())
        mapper.ScalarVisibilityOff()

        ''' Create an actor and set the appearance for the mapper '''
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0] / 255, color[1] / 255, color[2] / 255)
        actor.GetProperty().SetLineWidth(_w)

        return actor

    def targetBndToVTkActor(self):
        bndEid = self.m2.getBoundaryEdgeIds()
        vtkcolor = vtk.vtkNamedColors()
        htmlColor = "#454545"
        rgb = vtkcolor.HTMLColorToRGB(htmlColor)
        lines = self.bndSeqToVTKlines(self.m2, bndEid, rgb, -2, 0.3)
        return lines

    def bndSeqToVTKlines(self, _model, _bndSeq, _color, pid, opacity = 1):
        lineActors = []
        for eid in _bndSeq:
            vids = _model.Edges[eid].Vids
            
            line_w = 5

            actor = self.createLine(_model.pointList[vids[0]], _model.pointList[vids[1]], _color, _w = line_w)
            if pid != -1:
                if pid not in vids:
                    actor.GetProperty().SetOpacity(0.5)
                else:
                    actor.GetProperty().SetLineWidth(line_w * 1.5)
            if opacity != 1:
                actor.GetProperty().SetOpacity(opacity)
            lineActors.append(actor)
        return lineActors

    def bndSetToVTKlines(self, pid = -1):
        allLines = []
        bndSeqSet = self.boundarySeqSet()
        for i, bndSeq in enumerate(bndSeqSet):
            htmlColor = getColorValue(i)
            vtkcolor = vtk.vtkNamedColors()
            rgb = vtkcolor.HTMLColorToRGB(htmlColor)
            lines = self.bndSeqToVTKlines(self.m1, bndSeq, rgb, pid)
            allLines.extend(lines)
        return allLines
    
    def bndEidSetToVidsSet(self):
        bndSeqEidSet = self.boundarySeqSet()
        vidSet = []
        for bndSeq in bndSeqEidSet:
            bndVids = []
            for e in bndSeq:
                vids = self.m1.Edges[e].Vids
                for v in vids:
                    self.addVidToList(bndVids, v)
            vidSet.append(bndVids)
        return vidSet
    
    def addVidToList(self, _vl, _v):
        if len(_vl) == 0 or _vl[-1] != _v:
            _vl.append(_v)
        return _vl

    def boundaryDistanceQTLineViews(self):
        bndVidSet = self.bndEidSetToVidsSet()
        hs = self.pointDisToPercentage() # read distance percentage value
        self.allChartView = []
        for i, bndLineV in enumerate(bndVidSet):
            chartView = QTChartView(_title = "boundary_" + str(i))
            htmlColor = getColorValue(i)
            vtkcolor = vtk.vtkNamedColors()
            rgb = vtkcolor.HTMLColorToRGB(htmlColor)
            # print(len(bndLineV))
            chartView.create_seq_line(hs, bndLineV, rgb)
            self.allChartView.append(chartView)
        return self.allChartView

def getColorValue(i):
    htmlColor = [
        "#c23531",
        "#2f4554",
        "#61a0a8",
        "#d48265",
        "#749f83",
        "#ca8622",
        "#bda29a",
        "#6e7074",
        "#546570",
        "#c4ccd3",
        "#f05b72",
        "#ef5b9c",
        "#f47920",
        "#905a3d",
        "#fab27b",
        "#2a5caa",
        "#444693",
        "#726930",
        "#b2d235",
        "#6d8346",
        "#ac6767",
        "#1d953f",
        "#6950a1",
        "#918597"
    ]
    id = i % len(htmlColor)
    return htmlColor[id]