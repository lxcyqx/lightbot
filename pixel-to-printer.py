import re 
import math
import numpy as np
import sys
import re

conversion_factor = 50 # mm/pixel
top_left_x = -6000 # top left coordinate
top_left_y = -4000

# x, y pixel coordinates to x, y, z cartesian coordinates
def pixelToXYZ(pixel_point):
    x = pixel_point[0]
    y = pixel_point[1]

    x = x * conversion_factor + top_left_x
    y = y * conversion_factor + top_left_y

    return [x, y, 1000] # fixed z height

P1 = [-170, -99, 150]
P2 = [0, 196.3, 150]
P3 = [170, -99, 150]
home = [0, 0, 150] # in cartesian coordinates

def getHomeInFrameCoordinates():
    a0 = getEuclideanDistance(home, P1)
    b0 = getEuclideanDistance(home, P2)
    c0 = getEuclideanDistance(home, P3)
    return a0, b0, c0
    
def getEuclideanDistance(P1, P2):
    # convert strings to float
    for i in range(len(P1)):
        P1[i] = float(P1[i])
    for i in range(len(P2)):
        P2[i] = float(P2[i])
    return math.sqrt((P2[0]-P1[0])**2 + (P2[1]-P1[1])**2 + (P2[2]-P1[2])**2)

# Cartesian coordinates to lightbot coordinates
def XYZtoABC(point):
    a0, b0, c0 = getHomeInFrameCoordinates()
    A = getEuclideanDistance(P1, point) - a0
    B = getEuclideanDistance(P2, point) - b0
    C = getEuclideanDistance(P3, point) - c0
    return [A, B, C]


while True:
    pixel_input = input() # get input from command line
    pixel_input = re.findall(r'\d+\.\d+', pixel_input) # get numbers from string input
    for num in range(len(pixel_input)):
        pixel_input[num] = float(pixel_input[num])
    xyz = pixelToXYZ(pixel_input)
    abc = XYZtoABC(xyz)

    f = open("/tmp/printer", "wb")
    gcode_command = "G1 X{0} Y{1} Z{2}".format(abc[0], abc[1], abc[2])
    print(gcode_command)
    byteString = gcode_command.encode("UTF-8")
    f.write(byteString)
