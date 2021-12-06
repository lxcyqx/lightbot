from flask import Flask,request
import sys
import serial
import math
import time 

app = Flask(__name__)
printer = serial.Serial('/tmp/printer')

import re

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

def preprogrammedMove():
    # TODO: return list of points
    # generate curve in maya and then read from the txt file that is generated from other python script
    pass

@app.route('/position',methods=['GET'])
def getPosition():
    start = timer()
    end = timer()
    begin_x = request.args.get('x')
    begin_y = request.args.get('y')

    x = request.args.get('x')
    y = request.args.get('y')

    while (end - start < .1): #wait for elapsed time of 5 seconds
        end = timer()
        x = request.args.get('x')
        y = request.args.get('y')
    
    # if 10 seconds has passed and no new point, go to preprogrammed move
    if (end - start >= 10 and begin_x==x and begin_y==y):
        points = preprogrammedMove()
        #TODO: process the points


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

