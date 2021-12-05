from flask import Flask,request
import sys
import serial
import math
import time 

app = Flask(__name__)
printer = serial.Serial('/tmp/printer')

import re

# canvas is 640x480
conversion_factor = 2.38 # mm/pixel
top_left_x = -711 # top left coordinate
top_left_y = -559

# x, y pixel coordinates to x, y, z cartesian coordinates
def pixelToXYZ(pixel_point):
    x = pixel_point[0]
    y = pixel_point[1]

    x = -1 * x * conversion_factor + top_left_x
    y = -1 * y * conversion_factor + top_left_y

    return [x, y, 1500] # fixed z height

P1 = [-851.8, -512.3, 1803.5]
P2 = [2.65, 985.3, 1803.5]
P3 = [862.7, -512.3, 1803.5]
home = [0, 0, 1575] # in cartesian coordinates

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

    # newX =float(x)/4 -50
    # newY =float(y)/4 -50
    newX = abc[0]
    newY = abc[1]
    newZ = abc[2]

    line = "G0 X"+str(newX) + " Y" + str(newY) + " Z" + str(newZ) + "\n \r"
    print(line)
    byteString = line.encode('UTF-8')
    printer.write(byteString)
    print(printer.readline())
    # Now here we get the position, put your control code below
    # 
    return ""

def main():
    app.run(host='0.0.0.0',port=5000)
    #printer.open() 
    printer.write(b"G28 X Y Z")
    print(printer.is_open)


if __name__ == "__main__":
    sys.exit(main())

