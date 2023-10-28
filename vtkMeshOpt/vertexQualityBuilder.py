'''
Date: 2021-09-18 17:50:33
LastEditors: Lei Si
LastEditTime: 2021-09-19 01:10:02
'''
 
from vtkMeshOpt.quadMetric import Quad_ScaledJacobian
from vtkMeshOpt.hexaMetric import Hexa_ScaledJacobian
from tqdm import tqdm
#
#
# 
# 
class vertexQuality:
    def __init__(self, _vid) -> None:
        self.vid = _vid
        self.cornerIndex = []
        self.minQuality = 1000 # range [-1, 1], 1 is ideal ratio
        self.qualities = []
        
    def addCornerAndQuality(self, _index_value):
        self.cornerIndex.append(_index_value[0])
        quality = _index_value[1]
        if self.minQuality > quality:
            self.minQuality = quality
        self.qualities.append(quality)
        self.qualityToRadiiRatio()
    
    def qualityToRadiiRatio(self):
        if self.minQuality < 0:
            # nagivate quality -1 has 2 * maxRadii
            self.radiiRatio = abs(self.minQuality) + 1
        else:
            # radii is 0 when quality is ideal == 1
            self.radiiRatio = 1 - self.minQuality

#
#
# 
# 
class vertexQualityBuilder:
    def __init__(self, _meshDS, _qualityType = "scaled Jacobian") -> None:
        self.meshDS = _meshDS
        self.meshType = _meshDS.meshType
        self.points = self.meshDS.pointList
        self.createVertexQualityDict()

    def createVertexQualityDict(self):
        self.vertexQualityDict = {vid : vertexQuality(vid) for vid in range(len(self.points))}
        
    def vidsToCornerIndexAndQuality(self, vids):
        index_values = self.quality_metric.scaledJacobian_cell(vids)
        for i, vid in enumerate(vids):
            self.vertexQualityDict[vid].addCornerAndQuality(index_values[i])
    
    def cleanQualityDict(self):
        tmpDict = self.vertexQualityDict.copy()
        for vid, qobj in tmpDict.items():
            if qobj.minQuality == 1000:
                print("The point : " + str(vid) + " is not in any cell.")
                del self.vertexQualityDict[vid]
            

#
#
# 
#       
class Quad_VertexQualityBuilder(vertexQualityBuilder):
    def __init__(self, _meshDS, _qualityType = "scaled Jacobian") -> None:
        super().__init__(_meshDS, _qualityType)
        self.set_quality_metric(_qualityType)
        self.buildQualityDict()
        self.cleanQualityDict()
        
    def set_quality_metric(self, _qualityType):
        if _qualityType == "scaled Jacobian":
            self.metric_min = -1
            self.metric_max = 1
            self.quality_metric = Quad_ScaledJacobian("FPC", [], self.points)

    def buildQualityDict(self):
        fids = self.meshDS.Faces.keys()
        for fid in tqdm(fids):
            vids = self.meshDS.Faces[fid].Vids
            self.vidsToCornerIndexAndQuality(vids)

#
#
#
# 
class Hexa_VertexQualityBuilder(vertexQualityBuilder):
    def __init__(self, _meshDS, _qualityType = "scaled Jacobian") -> None:
        super().__init__(_meshDS, _qualityType)
        self.set_quality_metric(_qualityType)
        self.buildQualityDict()
        self.cleanQualityDict()
        
    def set_quality_metric(self, _qualityType):
        if _qualityType == "scaled Jacobian":
            self.metric_min = -1
            self.metric_max = 1
            self.quality_metric = Hexa_ScaledJacobian("FPC", [], self.points)

    def buildQualityDict(self):
        cids = self.meshDS.Cells.keys()
        for cid in tqdm(cids):
            vids = self.meshDS.Cells[cid].Vids
            self.vidsToCornerIndexAndQuality(vids)
