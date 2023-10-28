'''
Date: 2020-11-08 13:21:26
LastEditors: Lei Si
LastEditTime: 2021-09-21 19:46:56
'''
 
import vtk

class MouseInteractorPickPoint(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtkWindgetList, dataset, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.LeftButtonPressEvent)
        self.vtkWindgetList = vtkWindgetList
        self.PointLocator = vtk.vtkPointLocator()
        self.PointLocator.SetDataSet(dataset)
        self.lastSelectedPid = 1
        self.indicatorStr = ""
        
    def LeftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        # pickedActor = picker.GetActor()
        # print(pickedActor)
        position = picker.GetPickPosition()
        # print(position)
        pid = self.PointLocator.FindClosestPoint(position)
        # print(pid)
        # reset the old actor color.
        # if self.lastSelectedPid != -1:
        self.vtkWindgetList[0].fpcObj.setAllActorColorBack()
        self.lastSelectedPid = pid

        for windget in self.vtkWindgetList:
            windget.displayActor(pid)
        self.OnLeftButtonDown()
        return

class KeyPressInteractorPickPoint(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtkWindgetController, dataset, parent=None):
        self.AddObserver("KeyPressEvent", self.keyPressEvent)
        self.vtkWindgetController = vtkWindgetController
        self.PointLocator = vtk.vtkPointLocator()
        self.PointLocator.SetDataSet(dataset)
        self.lastSelectedPid = -1
        self.indicatorStr = ""
        self.bFlag = True
        
    def keyPressEvent(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == 'p':
            clickPos = self.GetInteractor().GetEventPosition()
            picker = vtk.vtkPropPicker()
            picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
            # pickedActor = picker.GetActor()
            # print(pickedActor)
            position = picker.GetPickPosition()
            # print(position)
            pid = self.PointLocator.FindClosestPoint(position)
            # set selected pid
            self.vtkWindgetController.setCurrentPid(pid)
            # reset the old actor color.
            # if self.lastSelectedPid != -1:
            self.vtkWindgetController.fpcObj.setAllActorColorBack()
            self.lastSelectedPid = pid
            i = 0
            for windget in self.vtkWindgetController.vtkWindgetList:
                if i == 0:
                    windget.displayActor(pid, _bFlag = self.bFlag)
                    i += 1
                else:
                    windget.displayActor(pid, _bFlag = self.bFlag)
        return