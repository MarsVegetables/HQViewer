'''
Date: 2021-09-09 00:18:00
LastEditors: Lei Si
LastEditTime: 2021-09-19 18:46:06
'''
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot

class pyQtJsOpt(QObject):
    def __init__(self, parent = None, obj = None) -> None:
        super().__init__(parent=parent)
        self.obj = obj
    '''
    @pyqtSlot(int)
    def printRef(self, ref):
        print("inside print Vid", ref)
        if hasattr(self.obj, "meshType"):
            if self.obj.meshType == "Quad":
                self.obj.removeAllActors()
                self.obj.bnd2D_specificPoint_vtkWidget(ref)
            if self.obj.meshType == "Hex":
                self.obj.removeAllActors()
                self.obj.bnd3D_specificPoint_vtkWidget(ref)
        if hasattr(self.obj, "allQualityChartView"):
            self.obj.displayViewActor(ref)
    '''
    def changeViewActor(self, vid):
        if hasattr(self.obj, "meshType"):
            if self.obj.meshType == "Quad":
                self.obj.removeAllActors()
                self.obj.bnd2D_specificPoint_vtkWidget(vid)
            if self.obj.meshType == "Hex":
                self.obj.removeAllActors()
                self.obj.bnd3D_specificPoint_vtkWidget(vid)
        if hasattr(self.obj, "allQualityChartView"):
            self.obj.displayViewActor(vid)
    
    @pyqtSlot(str)
    def printRef(self, ref):
        print("inside print Vids", ref)
        if "M" not in ref:
            if "[" in ref:
                if hasattr(self.obj, "chartView"):
                    self.obj.displayCorner(ref)
            else:
                self.changeViewActor(int(ref))

class webEngineView(QWebEngineView):
    def __init__(self, obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        webChannel = QWebChannel(self)
        self.backend = pyQtJsOpt(self, obj)
        webChannel.registerObject('pyQtOpt', self.backend)
        self.page().setWebChannel(webChannel)
        self.show()
