'''
Date: 2021-09-10 10:42:21
LastEditors: Lei Si
LastEditTime: 2021-10-19 20:50:58
'''
import numpy as np
import os

class HexToTriSurface:
    def __init__(self, _meshDS, _fileDirPath):
        self.meshDS = _meshDS
        self.fileDirPath = _fileDirPath
        self.surfaceFids = self.meshDS.getSurfaceFaceIds()
        self.verticesCo = _meshDS.pointList
        # new surface vid list
        VidSet = set()
        for fid in self.surfaceFids:
            face = self.meshDS.Faces[fid].Vids
            for v in face:
                VidSet.add(v)
        self.listv = list(VidSet) 

    def writeVandF(self, vertices, face, filePath):
            with open(filePath, 'w') as f:
                f.write("# OBJ file\n")
                f.write("# vertex count = %d\n"% len(vertices))
                f.write("# face count = %d\n" % len(face))
                for v in vertices:
                    f.write("v {:6f} {:6f} {:6f}\n".format(v[0], v[1], v[2]))
                for p in face:
                    f.write("f")
                    for i in p:
                        f.write(" %d" % (i + 1))
                    f.write("\n")

    def saveDataToTriObj(self):
        vertices = self.verticesCo[self.listv]
        
        triFaces = []
        for fid in self.surfaceFids:
            face = self.meshDS.Faces[fid].Vids
            cid = self.meshDS.Faces[fid].neighboring_Cids[0]
            cvids = self.meshDS.Cells[cid].Vids
            quadToTri = QuadToTriFaces(face, self.verticesCo, cvids, self.listv)
            triFaces.extend(quadToTri.QuadToTri())
        
        # build tri file path
        hexPath = self.meshDS.filePath
        self.fileName = hexPath.split("/")[-2] + "_" + hexPath.split("/")[-1].split(".vtk")[0]
        triPath = os.path.join(self.fileDirPath, "data", self.fileName + ".obj")
        self.writeVandF(vertices, triFaces, triPath)
        self.triPath = triPath
        return triPath

class QuadToTriFaces:
    def __init__(self, _fVids, _vco, _cVids, _newVidsMap) -> None:
        self.fVids = _fVids
        self.verticesCo = _vco
        self.cVids = _cVids
        self.newVidsMap = _newVidsMap
        self.cellCeneter()
    
    def cellCeneter(self):
        cvco = self.verticesCo[self.cVids] # cell vertices coordinates.
        center = np.average(cvco, axis=0)
        self.ccenter = center
    
    def checkFaceSeq(self, _fvids):
        fvidCos = self.verticesCo[_fvids]
        fcenter = np.average(fvidCos, axis=0)
        outVector = fcenter - self.ccenter
        outdirection = outVector / np.linalg.norm(outVector)
        u = fvidCos[1] - fvidCos[0] # 0 -> 1
        v = fvidCos[2] - fvidCos[0] # 0 -> 2
        # u -> v have a direction by using right hand principle.
        uvcorss = np.cross(u, v)
        fnormal = uvcorss / np.linalg.norm(uvcorss)
        directionFlag = np.dot(fnormal, outdirection)
        
        tVids = self.orderVidsBasedOnDirection(_fvids, directionFlag)
        return tVids
    
    def orderVidsBasedOnDirection(self, _fvids, _directionFlag):
        p0 = self.oldVidToNewVid(_fvids[0])
        p1 = self.oldVidToNewVid(_fvids[1])
        p2 = self.oldVidToNewVid(_fvids[2])
        tVids = [p0, p1, p2]
        if _directionFlag < 0:
            tVids = [p0, p2, p1]
        return tVids

    def oldVidToNewVid(self, _vid):
        return self.newVidsMap.index(_vid)

    def QuadToTri(self):
        t1 = self.checkFaceSeq([self.fVids[0], self.fVids[1], self.fVids[2]])
        t2 = self.checkFaceSeq([self.fVids[0], self.fVids[2], self.fVids[3]])
        return [t1, t2]

        


