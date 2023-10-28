import numpy as np
import vtk


def line_length(point_a, point_b):
    """This is a conceptual class representation of a simple BLE device
    (GATT Server). It is essentially an extended combination of the
    :class:`bluepy.btle.Peripheral` and :class:`bluepy.btle.ScanEntry` classes

    :param client: A handle to the :class:`simpleble.SimpleBleClient` client
        object that detected the device
    :type client: class:`simpleble.SimpleBleClient`
    :param addr: Device MAC address, defaults to None
    :type addr: str, optional
    :param addrType: Device address type - one of ADDR_TYPE_PUBLIC or
        ADDR_TYPE_RANDOM, defaults to ADDR_TYPE_PUBLIC
    :type addrType: str, optional
    :param iface: Bluetooth interface number (0 = /dev/hci0) used for the
        connection, defaults to 0
    :type iface: int, optional
    :param data: A list of tuples (adtype, description, value) containing the
        AD type code, human-readable description and value for all available
        advertising data items, defaults to None
    :type data: list, optional
    :param rssi: Received Signal Strength Indication for the last received
        broadcast from the device. This is an integer value measured in dB,
        where 0 dB is the maximum (theoretical) signal strength, and more
        negative numbers indicate a weaker signal, defaults to 0
    :type rssi: int, optional
    :param connectable: `True` if the device supports connections, and `False`
        otherwise (typically used for advertising ‘beacons’).,
        defaults to `False`
    :type connectable: bool, optional
    :param updateCount: Integer count of the number of advertising packets
        received from the device so far, defaults to 0
    :type updateCount: int, optional
    """
    # vector_ab = gen_vector(point_a, point_b)
    vector_ab = np.array([1,1])
    return np.linalg.norm(vector_ab)  # L2

def writeDataSet(dataset, filename):
    datasetwriter = vtk.vtkDataSetWriter()
    datasetwriter.SetInputData(dataset)
    datasetwriter.SetFileName(filename)
    datasetwriter.Write()

import math

def valueToRGB(value):
    # 1 is the ideal value

    # input value is [-1, 1]
    
    # value should between 0 to 2
    # cValue = (float(value) - sMin) / (sMax - sMin)
    value = value + 1
    cValue = float(value)/ 2
    # cValue = float(value)
    # print(cValue)
    # The min scalar value is mapped to 0, and the max value is mapped to 1
    
    hsv = [240., 1.0, 1.0] # - hue, sat, value
    s = cValue
    if cValue < 0.5:
        hsv[0] = 240 + (120 * 2 * s)
        hsv[1] = 1
    else:
        hsv[0] = 0
        hsv[1] = 2*s - 1
    rgb = hsvRgb(hsv)
    # rgb.append(1.0)  # set alpha (or opacity) channel
    return rgb

def valueToRGB_i0(value):
    # 0 is the ideal value

    # input value is [-1, 1]
    
    # value should between 0 to 2
    # cValue = (float(value) - sMin) / (sMax - sMin)
    value = value + 1
    cValue = float(value) / 2
    # cValue = float(value)
    # print(cValue)
    # The min scalar value is mapped to 0, and the max value is mapped to 1
    
    hsv = [240., 1.0, 0.8] # - hue, sat, value
    s = cValue
    if cValue < 0.5:
        hsv[0] = 240.
        hsv[1] = 1 - 2*s
    else:
        hsv[0] = 0.
        hsv[1] = 2*s - 1
    rgb = hsvRgb(hsv)
    # rgb.append(1.0)  # set alpha (or opacity) channel
    return rgb

'''
    Convert HSV to RGB color 
'''
def hsvRgb(hsv):
    rgb = [0,0,0]
    #h, s, v      - hue, sat, value
    #r, g, b      - red, green, blue
    #i, f, p, q, t   - interim values


    # guarantee valid input:
    h = hsv[0] / 60.
    while h >= 6.:
        h -= 6.
    while h < 0.:
        h += 6.

    s = hsv[1]
    if (s < 0.):
        s = 0.
    if (s > 1.):
        s = 1.

    v = hsv[2]
    if (v < 0.):
        v = 0.
    if (v > 1.):
        v = 1.


    # if sat==0, then is a gray:
    if s == 0.0:
        rgb[0] = rgb[1] = rgb[2] = v
        return rgb
    


    # get an rgb from the hue itself:

    i = math.floor(h)
    f = h - i
    p = v * (1. - s)
    q = v * (1. - s * f)
    t = v * (1. - (s * (1. - f)))

    if math.floor(i) == 0:
      r = v
      g = t
      b = p
      

    elif math.floor(i) == 1:
      r = q
      g = v
      b = p
      

    elif math.floor(i) == 2:
      r = p
      g = v
      b = t
      

    elif math.floor(i) == 3:
      r = p
      g = q 
      b = v
      

    elif math.floor(i) == 4:
      r = t
      g = p
      b = v
      

    elif math.floor(i) == 5:
      r = v
      g = p 
      b = q
      
    rgb[0] = r
    rgb[1] = g
    rgb[2] = b

    return rgb

def createVTKCellArray(lineVids):
        lines = vtk.vtkCellArray()
        for l in lineVids:
            line = vtk.vtkLine()
            for i, x in enumerate(l):
                line.GetPointIds().SetId(i,x)
            lines.InsertNextCell(line)
        return lines
    
def vlToVTKLinePolyData(vtkpoints, lineVids):
    vtk_lines = createVTKCellArray(lineVids)

    edgeData = vtk.vtkPolyData()
    edgeData.SetPoints(vtkpoints)
    edgeData.SetLines(vtk_lines)
    return edgeData