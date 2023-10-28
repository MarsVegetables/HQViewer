'''
Date: 2020-11-12 23:51:28
LastEditors: Lei Si
LastEditTime: 2021-10-17 23:23:20
'''

import vtk
import numpy as np

class histGen:
    def __init__(self, in_dataDir):
        self.xLabel, self.inDataArray = self.sortDirAndSplit(in_dataDir)
        allFrequencies = vtk.vtkFloatArray()
        allFrequencies.SetNumberOfComponents(1)
        allFrequencies.SetNumberOfTuples(len(self.inDataArray))
        for i, data in enumerate(self.inDataArray):
            allFrequencies.SetTuple1(i, data)
        
        self.dataObj = vtk.vtkDataObject()
        self.dataObj.GetFieldData().AddArray(allFrequencies)
        self.histActor = self.genBarChart()
    
    def genBarChart(self):
        xmin = 0.02
        xmax = 0.25
        ymin = 0.01
        ymax = 0.2
        barChart = vtk.vtkBarChartActor()
        # BUG 1: if input is not set first, the x-axis of the bar chart will be too long
        barChart.SetInput(self.dataObj)
        barChart.SetTitle("Histogram")
        barChart.GetPositionCoordinate().SetValue(xmin,ymin,0.0) # control where the cahrt display. set start x, y, z postion.
        barChart.GetPosition2Coordinate().SetValue(xmax,ymax,0.0) # control the end position of x, y, z. 
        barChart.GetProperty().SetColor(1,1,1)
        xlen = xmax - xmin
        ylen = ymax - ymin
        self.createLabelLegend(xmax, ymin + 0.2 * ylen, 0.2 * xlen, 0.6 * ylen)
        # BUG 2: if the number of entries is not set to the number of data array tuples, the bar chart actor will crash.
        # The crash occurs whether the legend and or labels are visible or not.
        barChart.GetLegendActor().SetNumberOfEntries(self.dataObj.GetFieldData().GetArray(0).GetNumberOfTuples())
        barChart.LegendVisibilityOff()
        barChart.LabelVisibilityOn()
        
        self.barChart = barChart
        self.applyColor2BarChart()
        return [self.barChart, self.legend]
   
    # BUG 3: The Y range is not shown as expect.
    def applyColor2BarChart(self):
        colors = [[0.8, 0.1, 0.1], [0.5, 0.5, 0.8], [0.2, 0.2, 0.2]]

        # seq of legend vale, from big to small.
        legendList = [len(self.xLabel) - 1, int(0.5 * len(self.xLabel)), 0]
        if len(self.xLabel) <= 2:
            legendList = [legendList[0]]
        elif len(self.xLabel) <=3:
            legendList = [legendList[0],legendList[2]]
        for i, xl in enumerate(self.xLabel):
            self.barChart.SetBarLabel(i, str(xl))
            if i in legendList:
                lIndex = legendList.index(i)
                color = colors[lIndex]
                self.updateLabelLegend(lIndex, color, str(xl))
                self.barChart.SetBarColor(i,color)
            else:
                self.barChart.SetBarColor(i,[0.2,0.5,0.8]) # setbarcolor (bar, color)

        

    def sortDirAndSplit(self, in_dir):
        dataArray = []
        xLabel = []
        for key in sorted(in_dir):
            dataArray.append(in_dir[key])
            xLabel.append(key)
        return xLabel, dataArray
    
    '''
    description: 
    param {*} self
    param {*} p1 : x min
    param {*} p2 : y min
    param {*} p3 : x length begin at x min
    param {*} p4 : y length begin at y min
    return {*}
    '''    
    def createLabelLegend(self, p1, p2, p3, p4):
        if hasattr(self, "legend"):
            print("already have a legend.")
        else:
            self.legend = vtk.vtkLegendBoxActor()
            if len(self.xLabel) > 3:
                self.legend.SetNumberOfEntries(3)
            else:
                self.legend.SetNumberOfEntries(len(self.xLabel) - 1)
            self.legend.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
            self.legend.GetPositionCoordinate().SetValue(p1, p2, 0)
            self.legend.GetPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
            self.legend.GetPosition2Coordinate().SetValue(p3, p4, 0)
    
    def updateLabelLegend(self, i, _color, _label):
        gly = createGlyph(_color)
        self.legend.SetEntryColor(i, _color)
        self.legend.SetEntrySymbol(i, gly.GetOutput())
        self.legend.SetEntryString(i, _label)
    
def createGlyph(_color):
    glyphSource = vtk.vtkGlyphSource2D()
    glyphSource.SetGlyphTypeToNone()
    glyphSource.DashOn()
    glyphSource.FilledOff()
    glyphSource.SetColor(_color)
    glyphSource.Update()
    return glyphSource


def test():
    data = [10, 20, 30, 50]

    hg = histGen(data)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(hg.histActor)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(640, 480)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    interactor.Initialize()
    interactor.Start()

# test()