'''
Date: 2021-09-18 15:05:28
LastEditors: Lei Si
LastEditTime: 2021-09-19 01:10:20
'''

from vtkMeshOpt.vertexQualityBuilder import Hexa_VertexQualityBuilder, Quad_VertexQualityBuilder
#
#
# this class will be used outside this file
# 
class meshVertexQualityMarker:
    def __init__(self, _meshDS) -> None:
        print("building mesh vertex quality dict ...")
        self.meshDS = _meshDS # mesh data structure
        self.meshType = _meshDS.meshType
        # self.maxRadii = _maxRadii # this variable control the sphere size.

        # generate quality value.
        if self.meshType == "Hex":
            # sectorActorsObj
            self.qualityBuilder = Hexa_VertexQualityBuilder(self.meshDS)
        else:
            self.qualityBuilder = Quad_VertexQualityBuilder(self.meshDS)
        
        self.qualityDict = self.qualityBuilder.vertexQualityDict
        print("mesh vertex quality dict --- done ...")
        # vertex marker radii dictionary for each vertex
        # {vid : {"radiiRatio" : 0, "actor" : []} for vid in self.qualityDict.keys()}
        # self.vertexQualityMarkRadiiRatio = {}
        # based on quality value generate sphere for each vertex

        # cluster marker dictionary
        # self.clusterQualityMarkerDict = {}
        # merge two sphere if they are overlapping
    
    '''
    def addVertexMarkDataToVertexMarkDict(self, _vid, _radiiRatio):
        self.vertexQualityMarkRadiiRatio[_vid]={"radiiRatio" : _radiiRatio}
        
    
        def addClusterDataToClusterDict(self, _clusterId, _radiiRatio, _actor, _members):
            self.clusterQualityMarkerDict[_clusterId]={"radiiRatio" : _radiiRatio, "actor" : _actor, "members" : _members}
    

    def updateMaxRadii(self, _newRadii):
        self.maxRadii = _newRadii # this variable control the sphere size.
        # regenerate all actor and detect cluster
    '''
        
