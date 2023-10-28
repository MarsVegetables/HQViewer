'''
Date: 2021-09-05 02:02:16
LastEditors: Lei Si
LastEditTime: 2021-10-07 21:25:00
'''
 
from boundaryErrorVis.boundaryErrorVis3D import boundaryErrorVis3D
from boundaryErrorVis.boundaryErrorVis2D import boundaryErrorVis2D
from boundaryErrorVis.bndErrorVisUtility import normalizeV
from vtkMeshOpt.MeshLoader import MeshLoader
from vtkMeshOpt.utility import valueToRGB
from meshStructure.meshDS import meshDS
import vtk

def test_main():
    renderWindow = vtk.vtkRenderWindow()
    interactor = vtk.vtkRenderWindowInteractor()
    colors = vtk.vtkNamedColors()
    # Set the background color.
    colors.SetColor('BkgColor', [26, 51, 77, 255])

    '''
    edges = vtk.vtkExtractEdges()
    edges.SetInputConnection(newGraphic.vtkReader.GetOutputPort())
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(edges.GetOutputPort())
    mapper.ScalarVisibilityOff()
    bgActor = vtk.vtkActor()
    bgActor.SetMapper(mapper)
    bgActor.GetProperty().SetOpacity(0.6)
    '''
    
    # Visualize
    renderer = vtk.vtkRenderer()

    a = []
    renderer.AddActor(a)
    '''
    ToDo:
    working on the hausdorff distance for quad and chart.
    change the hight for 3D distance.
    '''

    renderer.SetBackground(colors.GetColor3d('BkgColor'))

    renderWindow.SetSize(640, 480)
    renderWindow.AddRenderer(renderer)

    interactor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    interactor.Start()

from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarCategoryAxis, QBarSet, QLineSeries
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt


def boundaryChart2DLineViews():
    platform = 0
    if platform == 0:
        # linux
        root_folder = "/home/mars/Projects/FPCVis/VTKdata/"
    if platform == 1:
        # mac
        root_folder = "/Users/Lei_Si/Repositories/FPCVis/VTKdata/"

    model1, bgVTKReader1 = loadMesh(root_folder,"glp_bnd_10_mazewheel3.vtk")
    model2, bgVTKReader2 = loadMesh(root_folder,"mazewheel3.vtk")
    bnd2d = boundaryErrorVis2D(model1, model2)
    # hs = bnd2d.hausdorffDistances()
    lineViews = bnd2d.boundaryDistanceQTLineViews()
    return lineViews

def QTChartTest():
    # mouse move event
    # https://stackoverflow.com/questions/41922642/pyqt-grab-mousemoveevent-inside-a-chart
    # https://stackoverflow.com/questions/46805186/qt-chart-move-view-with-pressed-middle-mouse-button
    # https://geekscoders.com/courses/pyqt5-tutorials/lessons/pyqt5-tutorial-working-with-pyqtchart/
    boundaryChart2DLineViews()

# test_main()
# QTChartTest()