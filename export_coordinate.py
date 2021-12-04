from flask import Flask,request
import sys
import serial
import math
import numpy as np
import re


class Light:
    """LightBal Movement Class abstracts control of the light"""
   
    numLEDS = 6     # number of leds in the light sphere    
    targetPos = []  # real coordinate x,y,z position of the target point
    isTarget = False    # state machine looks here to track hand
                        #   or move smoothly in randomized pattern. 
    
    position = np.array([0,0,0])    # real coordinte x,y,z position of the light
    velocity = np.array([0,0,0])
    acceleration = np.array([0,0,0])

    force = np.array([0,0,0])
    mass = 1

    def __init__(self):  
        pass     
    def getPosition(self):
        pass
    def setTarget(self, target):
        pass
    def update(self):
        pass



### BEGINNING OF PROGRAM ###

app = Flask(__name__)
printer = serial.Serial('/tmp/printer')

# 
# canvas is 640x480
canvas_width = 640
canvas_height = 480
### DEBUG: conversion_factor = 2.38 # mm/pixel
conversion_factor = 1
###

#top_left_x = -711 # top left coordinate
#top_left_y = -559

center_x = (canvas_width/2) * conversion_factor
center_y = (canvas_height/2) * conversion_factor

# x, y pixel coordinates to x, y, z cartesian coordinates
def pixelToXYZ(pixel_point):
    pixel_x = pixel_point[0]
    pixel_y = pixel_point[1]

    x = (canvas_width - ( pixel_x * conversion_factor) - center_x)
    y = (canvas_height - (pixel_y * conversion_factor) - center_y)
    print( "pixel x = " + str(pixel_x) + "pixel y = " + str( pixel_y) )
    print( "real x = " + str(x) + "real y = " + str(y) )
    return [x, y, 1400] # fixed z height

P1 = [-851.8, -512.3, 1803.5]
P2 = [2.65, 985.3, 1803.5]
P3 = [862.7, -512.3, 1803.5]
home = [0, 0, 1575] # in cartesian coordinates

def getHomeInFrameCoordinates():
    a0 = getEuclideanDistance(home, P1)
    b0 = getEuclideanDistance(home, P2)
    c0 = getEuclideanDistance(home, P3)
    return a0, b0, c0
    
def getEuclideanDistance(p1, p2):
    # convert strings to float
    for i in range(len(p1)):
        p1[i] = float(p1[i])
    for i in range(len(p2)):
        p2[i] = float(p2[i])
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)

# Cartesian coordinates to lightbot coordinates
def XYZtoABC(point):
    a0, b0, c0 = getHomeInFrameCoordinates()
    A = getEuclideanDistance(P1, point) - a0
    B = getEuclideanDistance(P2, point) - b0
    C = getEuclideanDistance(P3, point) - c0
    return [A, B, C]

@app.route('/position',methods=['GET'])
def getPosition():
    x = request.args.get('x')
    y = request.args.get('y')

    xyz = pixelToXYZ([float(x), float(y)])
    abc = XYZtoABC(xyz)

    newX = abc[0]
    newY = abc[1]
    newZ = abc[2]

    line = "G0 X"+str(newX) + " Y" + str(newY) + " Z" + str(newZ) + "\n \r"
    is_valid = False
    if( -300 < newX and newX < 300):
        if( -300 < newY and newY < 300):
            if( -300 < newZ and newZ < 300):
                is_valid = True
    
    print(line)
    byteString = line.encode('UTF-8')
    if( is_valid):
        printer.write(byteString)
    
    #print(printer.readline())
    # Now here we get the position, put your control code below
    # 
    return ""

def main():
    app.run(host='0.0.0.0',port=5000)
    #printer.write(b"G28 X Y Z")



if __name__ == "__main__":
    sys.exit(main())








class Light:
    """LightBal Movement Class abstracts control of the light"""
   
    numLEDS = 6     # number of leds in the light sphere    
    targetPos = []  # real coordinate x,y,z position of the target point
    isTarget = False    # state machine looks here to track hand
                        #   or move smoothly in randomized pattern. 
    
    position = np.array([0,0,0])    # real coordinte x,y,z position of the light
    velocity = np.array([0,0,0])
    acceleration = np.array([0,0,0])

    force = np.array([0,0,0])
    mass = 1

    def __init__(self):  
        pass     
    def getPosition(self):
        pass
    def setTarget(self, target):
        pass
    def update(self):
        pass


