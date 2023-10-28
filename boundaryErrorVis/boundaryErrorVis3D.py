'''
Date: 2021-08-21 21:09:19
LastEditors: Lei Si
LastEditTime: 2021-10-19 21:21:54
'''

import pymeshlab
import os
import numpy as np
from tqdm import tqdm
import subprocess
from boundaryErrorVis.bndErrorVisUtility import pointColors, vfToVTKActor, pointColorsFromHSDir, createSphere
from boundaryErrorVis.HexToTriSurfaceObj import HexToTriSurface
import vtk
from boundaryErrorVis.boundaryDistance import bndDistance

# mp.offline()

# boundary error is described by using hausdorff Distance
class boundaryErrorVis3D:
    def __init__(self, _hex_sample, _hex_sample_vtkReader, _hex_target, _hex_target_vtkReader):
        self.hexSample = _hex_sample
        self.hexTarget = _hex_target
        self.fileDirPath = os.path.abspath(os.path.dirname(__file__))
        self.saveSurfaceData()
        self.loadData()
        self.buildMeshlabObject()
        self.bndDistanceObj = bndDistance(_hex_sample_vtkReader, _hex_target_vtkReader)

    def saveSurfaceData(self):
        # target is base model
        # sample is algorithm output
        # path 1 is sample 
        # path 2 is target
        self.samepleTriObj = HexToTriSurface(self.hexSample, self.fileDirPath)
        # self.targetTriObj = HexToTriSurface(self.hexTarget, self.fileDirPath)
        self.samepleTriObj.saveDataToTriObj()
        # self.targetTriObj.saveDataToTriObj()
        # self.path_1 = self.samepleTriObj.saveDataToTriObj()
        # self.path_2 = self.targetTriObj.saveDataToTriObj()

    def optCuts(self):
        '''
            optcuts command
        '''
        FracCutsPath = os.path.join(self.fileDirPath, "OptCuts/build/OptCuts_bin")
        # inputModelNameI = "lucy_o_f6032.obj"
        meshPath = self.samepleTriObj.triPath

        runCommand = FracCutsPath + ' 100 ' + meshPath + \
            ' 0.999 1 0 4.1 1 0'
        print(runCommand)
        subprocess.call([runCommand], shell=True)

    def buildMeshlabObject(self):
        '''
        https://github.com/cnr-isti-vclab/PyMeshLab/tree/master/pymeshlab/tests
        '''
        ms = pymeshlab.MeshSet()
        # ms.load_new_mesh(os.path.join(resultFile, "finalResult_mesh.obj"))
        # ms.load_new_mesh(self.targetTriObj.triPath)

        # ms.load_new_mesh(os.path.join(resultFile, "finalResult_mesh.obj"))
        ms.load_new_mesh(self.optCutsResultPath)
        # ms.load_new_mesh(os.path.join(root_folder, "data", "lucy_o_f6032.obj"))

        self.ms = ms
        self.m = self.ms.current_mesh()
        bb = self.m.bounding_box()
        self.mesh_diagonal = bb.diagonal()
    
    def getOptCutsHighGenusResultPath(self):
        # hexPath = self.hexSample.filePath
        fileName = self.samepleTriObj.fileName.split(".obj")[0]
        folderName = fileName + "_HighGenus_0.999_1_OptCuts"
        optCutsResultPath = os.path.join(os.getcwd(), "output", \
            folderName,"finalResult_mesh_normalizedUV.obj")
        return optCutsResultPath

    def getOptCutsTutteResultPath(self):
        # hexPath = self.hexSample.filePath
        fileName = self.samepleTriObj.fileName.split(".obj")[0]
        folderName = fileName + "_Tutte_0.999_1_OptCuts"
        optCutsResultPath = os.path.join(os.getcwd(), "output", \
            folderName,"finalResult_mesh_normalizedUV.obj")
        return optCutsResultPath

    def loadData(self):
        tuttePath = self.getOptCutsTutteResultPath()
        highGenusPath = self.getOptCutsHighGenusResultPath()

        self.optCutsResultPath = tuttePath
        if not os.path.exists(self.optCutsResultPath):
            self.optCutsResultPath = highGenusPath
            if not os.path.exists(self.optCutsResultPath):
                self.optCuts()

        self.optCutsResultPath = tuttePath
        if not os.path.exists(self.optCutsResultPath):
            self.optCutsResultPath = highGenusPath
            if not os.path.exists(self.optCutsResultPath):
                print("No OptCuts result funded. plz check OptCuts result path.")
                return 1

    def mapHausdorffDisToUV(self):
        face_array_matrix = self.m.face_matrix()

        tx = self.m.wedge_tex_coord_matrix()
        # should pass the distance dict here
        # now the distance dict is not Hausdorff distance
        # the value are precentage of error distance
        hausdorff_vt = self.buildBoundaryErrorVertexMatrix(tx, face_array_matrix, self.bndDistanceObj.distancePercentageDict_HexIds)
        self.uvHausdorffVertexList = hausdorff_vt
        # tx = m.vertex_tex_coord_matrix()
        hausdorff_ft = np.arange(len(tx)).reshape(-1, 3)
        self.uvHausdorffFaceList = hausdorff_ft
        
        return hausdorff_vt, hausdorff_ft

    def getUVDiagonal(self, uvCoord):
        xmax = max(uvCoord[:,0])
        xmin = min(uvCoord[:,0])
        ymax = max(uvCoord[:,1])
        ymin = min(uvCoord[:,1])
        svx = (xmax - xmin) ** 2
        svy = (ymax - ymin) ** 2
        diagonal = np.sqrt(svx + svy)
        return diagonal

    def triVidToHexVid(self, _triVid):
        remapVList = self.samepleTriObj.listv # this is boundary vertex index in Hex model
        vid = remapVList[_triVid]# the hausdorff Dis is calculate by just use boundary vertex in OBJ file. 
                                 # So, we need to map tri obj file vid back to hex model vid.
        return vid

    def UVBaseLength(self):
        # diagonal_10p = self.mesh_diagonal * 0.1
        diagonal_10p = self.uvDiagonal
        max_input = diagonal_10p
        return max_input

    def buildBoundaryErrorVertexMatrix(self, vt, f, hd):
        print("UV vertex # : " + str(len(vt)))
        print("surface Point # : " + str(len(self.samepleTriObj.listv)))
        # uv diagonal
        uvDiagonal = self.getUVDiagonal(vt)
        self.uvDiagonal = uvDiagonal

        newVt = []

        for i in tqdm(range(len(f))):
            ft = f[i]
            for j in range(len(ft)):
                vtIndex = len(ft) * i + j
                triVid = ft[j]       
                hexVid = self.triVidToHexVid(triVid)
                final_h = hd[hexVid] * uvDiagonal
                tmpVt = np.append(vt[vtIndex], final_h)
                newVt.append(tmpVt)
        return np.array(newVt)
    
    def UVHausdorffDisActor(self):
        v, f = self.mapHausdorffDisToUV()
        pcolors = pointColors(v)
        # actor, bndActor = vfToVTKActor(v, f, pcolors, bndFlag=True)
        actor = vfToVTKActor(v, f, pcolors, bndFlag=False)
        # actor.GetProperty().EdgeVisibilityOn()
        return [actor]
    
    def surfaceToVTKWeight(self):
        npPoints = self.bndDistanceObj.sampleSurface.npPoints
        faces = self.bndDistanceObj.sampleSurface.npCells
        
        hspDir = self.bndDistanceObj.distancePercentageDict_surfaceIds
        pcolors = pointColorsFromHSDir(len(npPoints), hspDir)
        actor = vfToVTKActor(npPoints, faces, pcolors)
        return actor
    
    def getTargetSurfaceToVTKActor(self, acolor = "", opacity = 0.1):
        # show target surface as wireframe.
        vertex_array_martix = self.bndDistanceObj.targetSurface.npPoints
        faces = self.bndDistanceObj.targetSurface.npCells
        # pcolors = pointColors(vertex_array_martix)
        actor = vfToVTKActor(vertex_array_martix, faces)
        vtkcolor = vtk.vtkNamedColors()
        rgb = vtkcolor.HTMLColorToRGB(acolor)
        actor.GetProperty().SetColor(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetLineWidth(0.01 * self.mesh_diagonal)
        # actor.GetProperty().SetLineWidth(self.mesh_diagonal)
        return actor
    

    def pidToSurfaceActor(self, pid, acolor = ""):
        vertex_array_martix = self.hexSample.pointList
        selectedVertex = self.hexSample.getVertexData(pid)
        neighboringFids = selectedVertex.neighboring_Fids
        surfaceVids = []
        surfaceFids = self.hexSample.getSurfaceFaceIds()
        for fid in neighboringFids:
            if fid in surfaceFids:
                face = self.hexSample.Faces[fid].Vids
                surfaceVids.append(face)
        if len(surfaceVids) == 0:
            print("No surface vertex is selected.")
        actor = vfToVTKActor(vertex_array_martix, surfaceVids)
        vtkcolor = vtk.vtkNamedColors()
        rgb = vtkcolor.HTMLColorToRGB(acolor)
        actor.GetProperty().SetColor(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        return actor
    
    def pidToPointActor(self, pid, acolor = ""):
        vertex_array_martix = self.hexSample.pointList

        selectedVertex = self.hexSample.getVertexData(pid)
        neighboringFids = selectedVertex.neighboring_Fids
        surfaceFlag = False
        surfaceFids = self.hexSample.getSurfaceFaceIds()
        for fid in neighboringFids:
            if fid in surfaceFids:
                vCoord = vertex_array_martix[pid]
                surfaceFlag = True
                break
        if not surfaceFlag:
            print("No surface vertex is selected.")
        actor = createSphere(vCoord, 0.01 * self.mesh_diagonal)
        vtkcolor = vtk.vtkNamedColors()
        rgb = vtkcolor.HTMLColorToRGB(acolor)
        actor.GetProperty().SetColor(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        return actor, self.UVSphereActor(pid, acolor=acolor)
    
    def pidToUVCoords(self, _pid):
        npFace = np.array(self.m.face_matrix())
        # input pid is the vertex id in 3D model, So, we need to map it to UV vertex index
        uvIndex = self.samepleTriObj.listv.index(_pid)
        uvPids = np.where(npFace == uvIndex) 

        npUVFace = np.array(self.uvHausdorffFaceList)
        selectedVertexIds = npUVFace[uvPids]
        npUVVertexcoord = np.array(self.uvHausdorffVertexList)
        selectedVertexCoord = npUVVertexcoord[selectedVertexIds]
        # many same vertices are selected
        # print(selectedVertexCoord)
        # so we need to remove duplicate.
        return np.unique(selectedVertexCoord, axis = 0)
    
    def UVSphereActor(self, _pid, acolor = ""):
        vCoords = self.pidToUVCoords(_pid)
        uvPActor = []
        for vc in vCoords:
            actor = createSphere(vc, 0.01 * self.uvDiagonal)
            vtkcolor = vtk.vtkNamedColors()
            rgb = vtkcolor.HTMLColorToRGB(acolor)
            actor.GetProperty().SetColor(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
            uvPActor.append(actor)
        return uvPActor
        