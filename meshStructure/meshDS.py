'''
Date: 2021-08-07 00:44:27
LastEditors: Lei Si
LastEditTime: 2021-09-18 15:57:55
'''
 
from typing_extensions import TypeAlias
from meshStructure.meshElement import Vertex, Edge, Face, Cell
from meshStructure.meshConfig import meshConfig
from tqdm import tqdm
import numpy as np

class meshDS(meshConfig):
    
    def __init__(self, _points, _cells, _meshType) -> None:
        self.meshType = _meshType
        self.Vertices = {}
        self.Edges = {}
        self.Faces = {}
        self.Cells = {}

        # following array will be used to build element connectivites.
        self.cellList = _cells
        self.pointList = _points # np array
        self.faceSet = set()
        self.edgeSet = set()
        self.faceList = [] # the vids is soted, so do not use this to generate polygon
        self.edgeList = []

        # self.build()
    def addFilePath(self, _fPath):
        self.filePath = _fPath
        
    def addVTKData(self, _vPoints, _vCells):
        self.vtkCells = _vCells
        self.vtkPoints = _vPoints
    
    def updateMeshType(self, _meshType):
        self.meshType = _meshType

    def updateVertices(self, _vid, _vclass):
        self.Vertices.update({_vid : _vclass})
    
    def updateEdges(self, _eid, _eclass):
        self.Edges.update({_eid : _eclass})
    
    def updateFaces(self, _fid, _fclass):
        self.Faces.update({_fid : _fclass})
    
    def updateCells(self, _cid, _cclass):
        self.Cells.update({_cid : _cclass})
    
    def addCellElement(self, _cid, _vids, _eids, _fids):
        if _cid not in self.Cells.keys():
            cc = Cell(_cid, _vids, _eids, _fids)
            self.updateCells(_cid, cc)

    def addFacesToFSet(self, _faces):
        for face in _faces:
            f = sorted(face)
            self.faceSet.add(tuple(f))

    def facesToFids(self, _faces):
        # given a face list, convert all face array to face id           
        fids = []
        for face in _faces:
            # f = tuple(face) # tuple is immutable - hashable, list is mutable - unhashable.
            f = sorted(face)
            fid = self.faceDir[tuple(f)]
            fids.append(fid)
        return fids
    
    def addEdgesToESet(self, _edges):
        for edge in _edges:
            e = sorted(edge)
            '''
            if tuple(e) in self.edgeSet:
                print("-1-")
                print(list(self.edgeSet).index(tuple(e)))
            '''
            self.edgeSet.add(tuple(e))
            '''
            if tuple(e) in self.edgeSet:
                print("-2-")
                print(list(self.edgeSet).index(tuple(e)))
            '''

    def edgeToEids(self, _edges):
        # given a edge list, convert all edge array to edge id
        eids = []
        for edge in _edges:
            # e = tuple(edge)
            # self.edgeSet.add(e)
            # self.edgeList = list(self.edgeSet)
            e = sorted(edge)
            eid = self.edgeDir[tuple(e)]
            eids.append(eid)
        return eids

    def addFaceElement(self, _fid, _vids, _eids):
        if _fid not in self.Faces.keys():
            fc = Face(_fid, list(_vids), _eids)
            self.updateFaces(_fid, fc)

    def addEdgeElement(self, _eid, _vids):
        if _eid not in self.Edges.keys():
            ec = Edge(_eid, list(_vids))
            self.updateEdges(_eid, ec)

    def addVertexElement(self, _vid, _coord):
        if _vid not in self.Vertices.keys():
            vc = Vertex(_vid, _coord)
            self.updateVertices(_vid, vc)    

    def faceSetTofaceDir(self):
        self.faceDir = {k: i for i, k in enumerate(self.faceSet)}

    def edgeSetToedgeDir(self):
        self.edgeDir = {k: i for i, k in enumerate(self.edgeSet)}

    def buildFaceListAndCellList(self):
        print("building face list and edge list ...")
        for cell in tqdm(self.cellList):
            faces = self.cellToFaces(cell)
            self.addFacesToFSet(faces)
            for face in faces:
                edges = self.faceToEdges(face)
                self.addEdgesToESet(edges)
        self.faceList = list(self.faceSet)
        self.edgeList = list(self.edgeSet)
        self.faceSetTofaceDir()
        self.edgeSetToedgeDir()
    
    def buildElementDir(self):
        print("building element dir ...")
        for cid, cell in enumerate(tqdm(self.cellList)):
            faces = self.cellToFaces(cell)
            fids = self.facesToFids(faces)
            c_eids = []
            for fid, face in zip(fids, faces):
                edges = self.faceToEdges(face)
                eids = self.edgeToEids(edges)

                # add face element
                self.addFaceElement(fid, face, eids)
                for eid, edge in zip(eids, edges):
                    if eid not in c_eids:
                        c_eids.append(eid)
                    # add edge element
                    self.addEdgeElement(eid, edge)

                    for vid in edge:
                        coord = self.pointList[vid]
                        #
                        # add vertex element
                        # vertex element connectivies will be complete when this function finish.
                        #
                        self.addVertexElement(vid, coord)
                        self.Vertices[vid].addNeighboring_Vids([edge])
                        self.Vertices[vid].addNeighboring_Eids([eid])
                        self.Vertices[vid].addNeighboring_Fids([fid])
                        self.Vertices[vid].addNeighboring_Cids([cid])

            # add cell elememt
            self.addCellElement(cid, cell, sorted(c_eids), sorted(fids))

    def buildElementConnectivities(self):
        print("building connectivities ...")
        for vid in tqdm(self.Vertices.keys()):
            self.buildEdgeConnectivities(vid)
            self.buildFaceConnectivities(vid)
            self.buildCellConnectivities(vid)
            
    def buildEdgeConnectivities(self, _vid):
        vc = self.Vertices[_vid]
        v_nvids = vc.neighboring_Vids
        v_neids = vc.neighboring_Eids
        v_nfids = vc.neighboring_Fids
        v_ncids = vc.neighboring_Cids

        # all neighboring edges for a vertex are neighboring with each other
        for eid in v_neids:
            self.Edges[eid].addNeighboring_Vids(v_nvids)
            self.Edges[eid].addNeighboring_Eids(v_neids)
            
            for fid in v_nfids:
                # if edge in the face, the face is a neighboring face.
                if eid in self.Faces[fid].Eids:
                    self.Edges[eid].addNeighboring_Fids([fid])

            for cid in v_ncids:
                # if edge in the cell, the cell is a neighboring face.
                if eid in self.Cells[cid].Eids:
                    self.Edges[eid].addNeighboring_Cids([cid])

    def buildFaceConnectivities(self, _vid):
        vc = self.Vertices[_vid]
        v_nvids = vc.neighboring_Vids
        v_neids = vc.neighboring_Eids
        v_nfids = vc.neighboring_Fids
        v_ncids = vc.neighboring_Cids

        for fid in v_nfids:
            self.Faces[fid].addNeighboring_Vids(v_nvids)
            self.Faces[fid].addNeighboring_Eids(v_neids)

            f_nfids = []
            for fid_2 in v_nfids:
                if fid == fid_2:
                    continue
                eids_1 = self.Faces[fid].Eids
                eids_2 = self.Faces[fid_2].Eids
                common_edge = set.intersection(set(eids_1), set(eids_2))
                if len(common_edge) > 1 :
                    print("warning --- more than 1 common edge " + "faces : " + str(fid) + "," + str(fid_2))
                if len(common_edge) == 1:
                    f_nfids.append(fid_2)
            self.Faces[fid].addNeighboring_Fids(f_nfids)

            for cid in v_ncids:
                if len(self.Cells[cid].Fids) > 1:
                    if fid in self.Cells[cid].Fids:
                        self.Faces[fid].addNeighboring_Cids([cid])

    def buildCellConnectivities(self, _vid):
        vc = self.Vertices[_vid]
        v_nvids = vc.neighboring_Vids
        v_neids = vc.neighboring_Eids
        v_nfids = vc.neighboring_Fids
        v_ncids = vc.neighboring_Cids

        for cid in v_ncids:
            self.Cells[cid].addNeighboring_Vids(v_nvids)
            self.Cells[cid].addNeighboring_Eids(v_neids)

            c_eids = self.Cells[cid].Eids
            c_nfids = []
            for fid in v_nfids:
                if fid in self.Cells[cid].Fids:
                    continue
                f_eids = self.Faces[fid].Eids
                common_edge = set.intersection(set(f_eids), set(c_eids))
                if len(common_edge) == 1:
                    c_nfids.append(fid)
                if len(common_edge) > 1:
                    print("warning --- more than 1 common edge " + "face : " + str(fid) + " - cell : " + str(cid))
            self.Cells[cid].addNeighboring_Fids(c_nfids)

            c_ncids = []
            for cid_2 in v_ncids:
                if cid == cid_2:
                    continue
                fids_1 = self.Cells[cid].Fids
                fids_2 = self.Cells[cid_2].Fids
                common_face = set.intersection(set(fids_1), set(fids_2))
                if len(common_face) > 1 :
                    print("warning --- more than 1 common face " + "cell : " + str(cid) + "," + str(cid_2))
                if len(common_face) == 1:
                    c_ncids.append(cid_2)
            self.Cells[cid].addNeighboring_Cids(c_ncids)
                    
    def build(self):
        self.buildFaceListAndCellList()
        self.buildElementDir()
        self.buildElementConnectivities()
        print("mesh data structure --- done ...")

    def getBoundaryEdgeIds(self):
        boundaryEdge = []
        if self.meshType == "Quad":
            for e in self.Edges.keys():
                if len(self.Edges[e].neighboring_Fids) == 1:
                    boundaryEdge.append(e)
        return boundaryEdge

    def getSurfaceFaceIds(self):
        surface = []
        if self.meshType == "Hex":
            for f in self.Faces.keys():
                if len(self.Faces[f].neighboring_Cids) == 1:
                    surface.append(f)
        return surface
    
    def getVertexData(self, pid):
        return self.Vertices[pid]

    def get_edge_len(self, eid):
        edge = self.Edges[eid]
        vids = edge.Vids
        v0 = self.Vertices[vids[0]].get_xyz()
        v1 = self.Vertices[vids[1]].get_xyz()
        return np.linalg.norm(v0 - v1)

    def get_vert_neighbor_edge_average_len(self, pid):
        neids = self.Vertices[pid].neighboring_Eids
        total_len = 0
        for i in neids:
            total_len += self.get_edge_len(i)
        return total_len / len(neids)


def test_case1():
    cells = [[0,1,2,3]]
    test_coords = np.array([[-0.5,   -0.5,  0.],  # 0
                            [1.,   0.,  0.],  # 1
                            [1.,   1.,  0.],  # 2
                            [0.,   1.,  0.]]) # 3
    mesh = meshDS(test_coords, cells, "quad")
    mesh.build()
    print(mesh.faceList)
    print(mesh.edgeList)
    mesh.Vertices[1].print_all()
    mesh.Edges[0].print_all()
    mesh.Faces[0].print_all()
    mesh.Cells[0].print_all()

def test_case2():
    cells = [[0,1,2,3,4,5,6,7]]
    test_coords = np.array([[2.,   2.,  2.],  # 0
                            [1.,   0.,  0.],  # 1
                            [1.,   1.,  0.],  # 2
                            [0.,   1.,  0.],  # 3
                            [0.,   0.,  1.],  # 4
                            [1.,   0.,  1.],  # 5
                            [1.,   1.,  1.],  # 6
                            [0.,   1.,  1.]])  # 7
    mesh = meshDS(test_coords, cells, "hex")
    mesh.build()
    print(mesh.faceList)
    print(mesh.edgeList)
    mesh.Vertices[1].print_all()
    mesh.Edges[0].print_all()
    mesh.Faces[1].print_all()
    mesh.Cells[0].print_all()

# test_case1()