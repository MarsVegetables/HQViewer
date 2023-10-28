'''
Date: 2021-09-19 23:59:10
LastEditors: Lei Si
LastEditTime: 2021-10-21 14:42:48
'''

import vtk

class qualityEdges:
    def __init__(self, _meshDS, _qualityDict, _vtkPoints, _pcolors, _Threshold = 0.95) -> None:
        self.meshDS = _meshDS
        self.qualityDict = _qualityDict
        self.vtkPoints = _vtkPoints
        self.pointColors = _pcolors
        self.pointColors_fedges = vtk.vtkDoubleArray()
        self.threshold = _Threshold
        if self.threshold != 1:
            self.pointColors_fedges.DeepCopy(_pcolors)
        self.qualityEdgesFilter()
        self.cellListToPolygon()

    def createVTKCellArray(self):
        lines = vtk.vtkCellArray()
        for l in self.lineVids:
            line = vtk.vtkLine()
            for i, x in enumerate(l):
                # highlight feature edges. a 0.1 -> 0.5
                if self.threshold != 1:
                    rgba = self.pointColors_fedges.GetTuple(x)
                    rgba = [rgba[0], rgba[1], rgba[2], 0.5] # [r, g, b, a]
                    self.pointColors_fedges.SetTuple(x, rgba)
                # add line to polygon.
                line.GetPointIds().SetId(i,x)
            lines.InsertNextCell(line)
        return lines
    
    def cellListToPolygon(self):
        vtk_lines = self.createVTKCellArray()

        self.qualityEdgeData = vtk.vtkPolyData()
        self.qualityEdgeData.SetPoints(self.vtkPoints)
        self.qualityEdgeData.SetLines(vtk_lines)
        if type(self.pointColors) != type([]):
            if self.threshold != 1:
                # print(self.pointColors.GetTuple(104))
                self.qualityEdgeData.GetPointData().SetScalars(self.pointColors_fedges)
            else:
                # print(self.pointColors_bak.GetTuple(104))
                self.qualityEdgeData.GetPointData().SetScalars(self.pointColors)


    def qualityEdgesFilter(self):
        self.lineVids = []
        for fid in self.meshDS.Edges.keys():
            vids = self.meshDS.Edges[fid].Vids
            qCount = 0
            for vid in vids:
                q = self.qualityDict[vid].minQuality
                # only show edge that both two ends min quality are less than threshold.
                # 0.5 means show all edges that both ends quality less than 0.5
                # threshold is the maximum quality value.
                if q > self.threshold:
                    continue
                qCount += 1
            if qCount == 2:      
                self.lineVids.append(vids)
