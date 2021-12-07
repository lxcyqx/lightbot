from flask import Flask,request
import sys
import serial
import math
import numpy as np
import re
import colorsys

class Light:
    """
    LightBal Movement Class abstracts control of the light
    """
    printer = None
    numLEDS = 6     # number of leds in the light sphere    
    maxRadius = 300
    # Pulley points defined in 3D space: (mm)
    P1 = [-851.8, -512.3, 1803.5]
    P2 = [2.65, 985.3, 1803.5]
    P3 = [862.7, -512.3, 1803.5]
    home = [0, 0, 1575] # in cartesian coordinates
    # cable length offsets. Length of cables when light is at home positoin.
    a0, b0, c0 = 0, 0, 0
    isTargetSet = False    # Makes sure robot does not move until target it set.
    targetPosition = np.array([0,0,1400])  # real coordinate x,y,z position of target
    position = np.array([0,0,1400])    # real coordinte x,y,z position of the light
    velocity = np.array([0,0,0])
    acceleration = np.array([0,0,0])
    speed = 0
    time_step = 0.05
    # Force and mass used in "P Controller" motion smoothing. F=Ma 
    force = np.array([-2,0,0])
    mass = .5
    # Color and Sound defined in polar coordinates. 
    polarPosition = [0,0,0] # [ Radius, Angle(degrees), Z_height]
    RGB = [0,0,0] # [R, G, B] values defined from 0 to 1

    k_p = 0
    k_d = 0
    

    def __init__(self,newPrinter):
        self.printer = newPrinter
        self.setHomeInFrameCoordinates()

        
    def setHomeInFrameCoordinates(self):
        # Calculate lengs of cables when light is at the home position. Used to offset motion commands
        #   as part of the kinematics implementation.
        self.a0 = self.getEuclideanDistance(self.home, self.P1)
        self.b0 = self.getEuclideanDistance(self.home, self.P2)
        self.c0 = self.getEuclideanDistance(self.home, self.P3)


    def getPosition(self):
        # Allows other parts of the program to get light's current position (not target pos)
        return [this.position[0] ,this.position[1], this.position[2]]


    def setTarget(self, target):
        # Set target for light to go worards. This is how other parts of the program assign new positions 
        #   to the light. Implements "P controller" for motion smoothing.
        for i in range(len(target)):
            self.targetPosition[i] = target[i]
        self.isTargetSet = True


    def getEuclideanDistance(self, p1, p2):
        # convert strings to float
        for i in range(len(p1)):
            p1[i] = float(p1[i])
        for i in range(len(p2)):
            p2[i] = float(p2[i])
        # find euclidean distance 
        return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)


    # Cartesian coordinates to lightbot coordinates
    def XYZtoABC(self, point):
        # a0, b0, c0 = self.getHomeInFrameCoordinates()
        A = self.getEuclideanDistance(self.P1, point) - self.a0
        B = self.getEuclideanDistance(self.P2, point) - self.b0
        C = self.getEuclideanDistance(self.P3, point) - self.c0
        return [A, B, C]

    # Calculate cylindrical R,Th,Z coordinate from XYZ coordinates
    def XYZtoPolar(self, point):
        X = point[0]
        Y = point[1]
        Z = point[2]
        #print("X: "+str(X)+"Y: "+str(Y))
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


    # A force is used to move the light sphere towares the target position smoothly
    def update_position(self):
        # Force is directly proportional to distance, and lies along the vector from 
        #   light position to target position
        # F=ma ; F/m = a
        self.force = self.targetPosition - self.position
        self.acceleration = self.force * self.k_p
        self.velocity = self.velocity * self.k_d + self.acceleration * self.time_step
        self.speed = ((self.velocity ** 2).sum()) ** 0.5 * 60
        self.position = self.position + self.velocity * self.time_step
        return self.position

    def set_mode(self, mode):
        if(mode == "smooth"):
            self.k_p = .5
            self.k_d = 0.975
        elif(mode == "responsive"):
            self.k_p = 50
            self.k_d = .60


    # Update is called several times a second to trigger the new position and 
    #   color of the LED. This is how the light is anamated.
    def update(self):
        if (self.isTargetSet and self.checkIsValid(self.targetPosition) ):
            
            self.update_position() 
            
            ABC = self.XYZtoABC(self.position)
            line = "G0 X"+str(ABC[0]) + " Y" + str(ABC[1]) + " Z" + str(ABC[2]) + " F" + str(self.speed) + "\n \r"
            byteString = line.encode('UTF-8')
            self.printer.write(byteString)
            
            self.polarPosition = self.XYZtoPolar(self.targetPosition)
            RGB=self.PointToRGB(self.targetPosition)
            
            colorGCode="SET_LED LED=light RED="+str(RGB[0])+" GREEN="+str(RGB[1])+" BLUE="+str(RGB[2])+" \n \r"
            
            byteString = colorGCode.encode('UTF-8')
            self.printer.write(byteString)
