from flask import Flask,request
import sys
import serial
import math
import numpy as np
import re
import colorsys

class Light:
    """LightBal Movement Class abstracts control of the light"""
    printer = None
    numLEDS = 6     # number of leds in the light sphere    
    maxRadius = 200
    P1 = [-851.8, -512.3, 1803.5]
    P2 = [2.65, 985.3, 1803.5]
    P3 = [862.7, -512.3, 1803.5]
    home = [0, 0, 1575] # in cartesian coordinates

    isTargetSet = False    # Makes sure robot does not move until target it set.
    targetPosition = np.array([0,0,0])  # real coordinate x,y,z position of target
    position = np.array([0,0,0])    # real coordinte x,y,z position of the light
    velocity = np.array([0,0,0])
    acceleration = np.array([0,0,0])
    
    polarPosition = [0,0,0]
    RGB = [0,0,0]

    force = np.array([0,0,0])
    mass = 1

    def __init__(self,newPrinter):
        self.printer = newPrinter

    def getPosition(self):
        return [this.position[0] ,this.position[1], this.position[2]]
        print("DEBUG: getPosition called")

    def setTarget(self, target):
        for i in range(len(target)):
            self.targetPosition[i] = target[i]
            self.isTargetSet = True

    def getEuclideanDistance(self, p1, p2):
        # convert strings to float
        for i in range(len(p1)):
            p1[i] = float(p1[i])
        for i in range(len(p2)):
            p2[i] = float(p2[i])
        return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)

    def getHomeInFrameCoordinates(self):
        a0 = self.getEuclideanDistance(self.home, self.P1)
        b0 = self.getEuclideanDistance(self.home, self.P2)
        c0 = self.getEuclideanDistance(self.home, self.P3)
        return a0, b0, c0
    
    # Cartesian coordinates to lightbot coordinates
    def XYZtoABC(self, point):
        a0, b0, c0 = self.getHomeInFrameCoordinates()
        A = self.getEuclideanDistance(self.P1, point) - a0
        B = self.getEuclideanDistance(self.P2, point) - b0
        C = self.getEuclideanDistance(self.P3, point) - c0
        return [A, B, C]

    def XYZtoPolar(self, point):
        X = point[0]
        Y = point[1]
        Z = point[2]
        print("X: "+str(X)+"Y: "+str(Y))
        R = math.sqrt(X**2 + Y**2)
        Th = math.degrees(math.atan2(Y,X))
        print("Radius: " + str(R) + " Angle: "+ str(Th))
        return [R,Th,Z]
    
    # Error checking if the targt point is in bounds 
    def checkIsValid(self, point):
        Z = self.targetPosition[2]
        is_valid = False
        
        targetRadius = self.getEuclideanDistance(point, [0,0,Z])
        if (targetRadius <= self.maxRadius):
            is_valid = True
        return is_valid

    # Convert the point to light space
    def PointToRGB(self,polarPoint):
        polarCoord = self.XYZtoPolar(polarPoint)
        R = polarCoord[0]
        S = R/self.maxRadius
        Th = polarCoord[1]
        #print(Th)
        H = (Th + 180)/(360)
        #print("Hue: "+str(H))
        V = .5
        RGB = (0,0,0)
        if(0<=S and S<= 1):
            if(0<=H and H<=1):
                RGB = colorsys.hsv_to_rgb(H,S,V)

        return list(RGB)


    # Update is called several times a second to trigger the new position and 
    #   color of the LED. This is how the light is anamated.
    def update(self):
        if (self.isTargetSet and self.checkIsValid(self.targetPosition) ):
            newX = self.targetPosition[0]
            newY = self.targetPosition[1]
            newZ = self.targetPosition[2]
            line = "G0 X"+str(newX) + " Y" + str(newY) + " Z" + str(newZ) + "\n \r"
            #print(line)
            byteString = line.encode('UTF-8')
            self.printer.write(byteString)
            
            self.polarPosition = self.XYZtoPolar(self.targetPosition)
            RGB=self.PointToRGB(self.polarPosition)
            
            colorGCode="SET_LED LED=light RED="+str(RGB[0])+" GREEN="+str(RGB[1])+" BLUE="+str(RGB[2])+" \n \r"
            
            #print(colorGCode)
            byteString = colorGCode.encode('UTF-8')
            self.printer.write(byteString)
    

### BEGINNING OF MAIN PROGRAM ###

app = Flask(__name__)
printer = serial.Serial('/tmp/printer')
light = Light(printer)

# canvas is 640x480
canvas_width = 640
canvas_height = 480

conversion_factor = 1 # mm/pixel

# center of camera canvas is aligned with pysical Z axis
center_x = (canvas_width/2) * conversion_factor
center_y = (canvas_height/2) * conversion_factor

# x, y pixel coordinates to x, y, z cartesian coordinate
def pixelToXYZ(pixel_point):
    pixel_x = pixel_point[0]
    pixel_y = pixel_point[1]

    x = (canvas_width - ( pixel_x * conversion_factor) - center_x)
    y = (canvas_height - (pixel_y * conversion_factor) - center_y)
    #print( "pixel x = " + str(pixel_x) + "pixel y = " + str( pixel_y) )
    return [x, y, 1400] # fixed z height


"""
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
"""

# This function is called every frame of the handtrack.js script 
# Handtrack.js passes the target pixel x,y coordinate of the tracked hand (or hands)
# getPosition() calculates the X,Y,Z location from the pixel x,y location and  
# sets the new targetPosition of the light object.
@app.route('/position',methods=['GET'])
def getPosition():
    x = request.args.get('x')
    y = request.args.get('y')

    xyz = pixelToXYZ([float(x), float(y)])
    abc = light.XYZtoABC(xyz)

    newX = abc[0]
    newY = abc[1]
    newZ = abc[2]

    light.setTarget([ newX, newY, newZ])
    light.update()
    return ""
"""
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

"""
    

def main():
    app.run(host='0.0.0.0',port=5000)
    #printer.write(b"G28 X Y Z")



if __name__ == "__main__":
    sys.exit(main())



