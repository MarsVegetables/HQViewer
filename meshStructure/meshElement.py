'''
Date: 2021-08-08 22:06:47
LastEditors: Lei Si
LastEditTime: 2021-08-13 15:41:33
'''

import numpy as np

class Element_Base:
    def __init__(self, _id, _element_type = "Base"):
        self.element_type = _element_type
        self.id = _id

        self.neighboring_Vids = []
        self.neighboring_Eids = []
        self.neighboring_Fids = []
        self.neighboring_Cids = []

        self.boundary = False

    def print_id_type(self):
        print("type : " + self.element_type)
        print("id : " + str(self.id))

    def print_self_data(self):
        self.print_id_type()

    def print_neighboring(self, _idFlag = True):
        if _idFlag:
            self.print_id_type()

        print("neigboring_Vids --> " + str(self.neighboring_Vids))
        print("neigboring_Eids --> " + str(self.neighboring_Eids))
        print("neigboring_Fids --> " + str(self.neighboring_Fids))
        print("neigboring_Cids --> " + str(self.neighboring_Cids))

    def print_all(self):
        self.print_self_data()
        self.print_neighboring(False)
#
#   
#
class Vertex(Element_Base):
    def __init__(self, _id, _coordinate, _element_type = "Vertex"):
        super().__init__(_id, _element_type)
        self.x = _coordinate[0]
        self.y = _coordinate[1]
        self.z = _coordinate[2]

    def print_self_data(self):
        super().print_self_data()
        print("coordinate : " + str([self.x, self.y, self.z]))

    def addNeighboring_Vids(self, _edges):
        for edge in _edges:
            vids = edge[edge != self.id]
            for vid in vids:
                if vid not in self.neighboring_Vids:
                    self.neighboring_Vids.append(vid)

    def addNeighboring_Eids(self, _eids):
        for eid in _eids:
            if eid not in self.neighboring_Eids:
                self.neighboring_Eids.append(eid)
    
    def addNeighboring_Fids(self, _fids):
        for fid in _fids:
            if fid not in self.neighboring_Fids:
                self.neighboring_Fids.append(fid)

    def addNeighboring_Cids(self, _cids):
        for cid in _cids:
            if cid not in self.neighboring_Cids:
                self.neighboring_Cids.append(cid)

    def get_xyz(self):
        return np.array([self.x, self.y, self.z])

#
#
#
class Edge(Element_Base):
    def __init__(self, _id, _vids, _element_type = "Edge"):
        super().__init__(_id, _element_type)
        self.Vids = _vids

    def print_self_data(self):
        super().print_self_data()
        print("Vids : " + str(self.Vids))

    def addNeighboring_Vids(self, _vids):
        for vid in _vids:
            if vid not in self.Vids:
                if vid not in self.neighboring_Vids:
                    self.neighboring_Vids.append(vid)

    def addNeighboring_Eids(self, _eids):
        for eid in _eids:
            if eid is not self.id and eid not in self.neighboring_Eids:
                self.neighboring_Eids.append(eid)

    def addNeighboring_Fids(self, _fids):
        for fid in _fids:
            if fid not in self.neighboring_Fids:
                self.neighboring_Fids.append(fid)
    
    def addNeighboring_Cids(self, _cids):
        for cid in _cids:
            if cid not in self.neighboring_Cids:
                self.neighboring_Cids.append(cid)
#
#
#
class Face(Edge):
    def __init__(self, _id, _vids, _eids, _element_type = "Face"):
        super().__init__(_id, _vids, _element_type)
        self.Eids = _eids

    def print_self_data(self):
        super().print_self_data()
        print("Eids : " + str(self.Eids))

    def addNeighboring_Eids(self, _eids):
        for eid in _eids:
            if eid not in self.Eids:
                if eid not in self.neighboring_Eids:
                    self.neighboring_Eids.append(eid)

    def addNeighboring_Fids(self, _fids):
        for fid in _fids:
            if fid is not self.id and fid not in self.neighboring_Fids:
                self.neighboring_Fids.append(fid)
                
    def angle_Vids(self, _vid):
        pass                                                                                       

#
#
#
class Cell(Face):
    def __init__(self, _id, _vids, _eids, _fids, _element_type = "Cell"):
        super().__init__(_id, _vids, _eids, _element_type)
        self.Fids = _fids
        self.cellType = "unassigned"

    def print_self_data(self):
        super().print_self_data()
        print("Fids : " + str(self.Fids))

    def addNeighboring_Fids(self, _fids):
        for fid in _fids:
            if fid not in self.Fids:
                if fid not in self.neighboring_Fids:
                    self.neighboring_Fids.append(fid)

    def addNeighboring_Cids(self, _cids):
        for cid in _cids:
            if cid is not self.id and cid not in self.neighboring_Cids:
                self.neighboring_Cids.append(cid)
                
    def corner_Vids(self, _vid):
        pass