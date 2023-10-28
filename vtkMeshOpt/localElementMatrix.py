'''
Date: 2021-08-03 22:04:25
LastEditors: Lei Si
LastEditTime: 2021-09-19 01:12:55
'''
 
import vtk
import numpy
from vtkMeshOpt.MeshLoader import MeshLoader
from vtkMeshOpt.quadMetric import Quad_ScaledJacobian
from vtkMeshOpt.hexaMetric import Hexa_ScaledJacobian
from meshStructure.meshDS import meshDS
from boundaryErrorVis.echartsComponent import echartsBar

def getOtherPoints(center, cellArray):
    node_index = cellArray.index(center)
    tmp1 = (node_index - 1)
    point1_index = tmp1 if tmp1 >= 0 else (len(cellArray) - 1)
    point1 = cellArray[point1_index]

    tmp2 = node_index + 1
    point2_index = tmp2 if tmp2 < len(cellArray) else 0
    point2 = cellArray[point2_index]

    return point1, point2

def loadQuadData():
    # this function does not use mesh data structure.
    file_path = "/home/mars/Desktop/Projects/FPCVis/VTKdata/"
    file_name = 'holes1.vtk'
    mesh = MeshLoader(file_path=file_path, file_name=file_name)

    # generate cell list
    mesh.cellList_vtk2np()
    cells = mesh.cellList

    # points
    points = mesh.generateNpPoints()
    return points, cells

def quadMatrixData(_vi, _mesh):
    quad_scaledJacobian = Quad_ScaledJacobian("local element matrix", [], _mesh.pointList)
    angleIndex = []
    angleQuality = []
    vi = _vi
    cids = _mesh.Vertices[_vi].neighboring_Cids
    for cid in cids:
        cell = cell = _mesh.Cells[cid].Vids
        if vi in cell:
            connectVertex = [vi]
            p1, p2 = getOtherPoints(vi, cell)
            if p1 not in connectVertex:
                connectVertex.insert(0,p1)
            if p2 not in connectVertex:
                connectVertex.append(p2)
                
            quad_v = quad_scaledJacobian.scaledJacobian_cell(cell)
            value = quad_v[cell.index(vi)]
            angleIndex.append(str(connectVertex))
            angleQuality.append(value)

    tableData = {vi:[angleIndex, angleQuality]}
    return tableData

def loadHexData():
    filePath = "/mnt/mdisk/UHResearches/VTK_2D/Smoothing_Examples/"
    fileName = "fandisk.vtk"
    basicGraphic = MeshLoader(filePath, fileName)

    points = basicGraphic.generateNpPoints()
    cells = basicGraphic.cellList_vtk2np()

    print("DS start build.....")
    mesh = meshDS(points, cells, "hex")
    mesh.build()

    return mesh

def hexMatrixData(_vi, _mesh):
    cornerIndex = []
    cornerQuality = []
    ncid = _mesh.Vertices[_vi].neighboring_Cids
    for cid in ncid:
        cell = _mesh.Cells[cid].Vids
        hex_jc = Hexa_ScaledJacobian("local element matrix", [], _mesh.pointList)
        scaled_Jacob_list = hex_jc.scaledJacobian_cell(cell)
        for sj in scaled_Jacob_list:
            node_ids = sj[0]
            jv = sj[1]
            if _vi == node_ids[0]:
                cornerIndex.append(str(list(node_ids)))
                cornerQuality.append(jv)
    tableData = {_vi:[cornerIndex, cornerQuality]}
    return tableData

def getVertexQualityMatrix(_vi, _mesh):
    if _mesh.meshType == "Quad":
        return quadMatrixData(_vi, _mesh)
    if _mesh.meshType == "Hex":
        return hexMatrixData(_vi, _mesh)
        
#
# python QT5 Table
# https://pythonbasics.org/pyqt-table/
#
# tableData = {vertex index:[angleIndex, angleQuality]}
# {1: [[[9, 1, 30], [30, 1, 0]], [0.9065378550952359, 0.9896308047266582]]}
#

# data = {1: [[[9, 1, 30], [30, 1, 0]], [0.9065378550952359, 0.9896308047266582]]}

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QWidget, QAction, QTableWidget
from PyQt5.QtGui import QIcon, QTabletEvent
from PyQt5.QtCore import pyqtSlot
import sys

class TableView(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
    
    def setData(self):
        verHeaders = []
        for n, key in enumerate(sorted(self.data.keys())):
            verHeaders.append(str(key))
            for m, item in enumerate(self.data[key][1]):
                newitem = QTableWidgetItem(str(item))
                self.setItem(n,m,newitem)
        self.setHorizontalHeaderLabels(self.data[key][0])
        self.setVerticalHeaderLabels(verHeaders)

def main(args):
    app = QApplication(args)
    # Table = TableView(tableData, len(tableData.keys()), len(angleIndex)) # (data, num of row, num of col)
    # Table.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)