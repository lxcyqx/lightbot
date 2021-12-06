from flask import Flask,request
import sys
import serial
import math
import numpy as np
import re
import colorsys
from tkinter import *
from time import perf_counter
from threading import Thread
import time
sys.path.append('.')
from Light import Light


"""
### LightBot class: visualization and smooth timing ###
"""
class LightBot:
    
    def __init__(self,light):
        self.root = Tk()
        self.root.geometry("660x500")
        self.root.config(bg="white")

        self.canvas_frame = Frame(root)
        self.canvas_frame.pack(side = TOP)
        self.canvas = Canvas(self.canvas_frame, width=640, height=480, bg="grey")
        self.canvas.pack()

        self.button_frame = Frame(root)
        self.button_frame.pack(side = BOTTOM)

        self.start_button = Button(self.button_frame, text="START")
        self.start_button.pack(side=LEFT)
        self.pause_button = Button(self.button_frame, text="PAUSE") 
        self.pause_button.pack( side=LEFT)
        self.stop_button = Button(self.button_frame, text="STOP")
        self.stop_button.pack( side=LEFT)

    
    def run(self):
        self.root.mainloop()
    
    def set_pixel_target(self, pixel_x, pixel_y):
        self.draw_circle(pixel_x, pixel_y, 10, "blue")

    def draw_circle(self, x, y, radius, color):
        x0=x-radius
        x1=x+radius
        y0=y-radius
        y1=y+radius
        id = self.canvas.create_oval(x0,y0,x1,y1, fill=color)
        return id



"""
### BEGINNING OF MAIN PROGRAM ###
"""
app = Flask(__name__)
printer = serial.Serial('/tmp/printer')


# Light ball object, capable of moving around and changing color
light = Light(printer)

# LightBot, top level object anamates scene and does high level calculations
#t=Thread(target=
#lightBot = LightBot(light)
#lightBot.run()

# canvas is 640x480
canvas_width = 640
canvas_height = 480
conversion_factor = 1 # mm/pixel

# center of camera canvas is aligned with pysical Z axis
center_x = canvas_width/2 
center_y = canvas_height/2 


# x, y pixel coordinates to x, y, z cartesian coordinate
def pixelToXYZ(pixel_point):
    pixel_x = math.floor(pixel_point[0])
    pixel_y = math.floor(pixel_point[1])
    #print("Pixel X: "+str(pixel_x)+" Pixel Y: "+str(pixel_y))
    pixel_x_adj = -1* ( pixel_x - center_x)
    pixel_y_adj = -1* (pixel_y - center_y)
    x = pixel_x_adj * conversion_factor
    y = pixel_y_adj * conversion_factor
    #print( "Real x = " + str(x) + "real y = " + str(y) )
    return [x, y, 1400] # fixed z height


def preprogrammedMove():
    # TODO: return list of points
    # generate curve in maya and then read from the txt file that is generated from other python script
    pass

# This function is called every frame of the handtrack.js script 
# Handtrack.js passes the target pixel x,y coordinate of the tracked hand (or hands)
# getPosition() calculates the X,Y,Z location from the pixel x,y location and  
# sets the new targetPosition of the light object.
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
    abc = light.XYZtoABC(xyz)
    #lightBot.set_pixel_target(float(x), float(y))

   # newX = abc[0]
   # newY = abc[1]
   # newZ = abc[2]

    light.setTarget([ xyz[0], xyz[1], xyz[2]])
    light.update()
    return ""


def main():
    app.run(host='0.0.0.0',port=5000)
    #printer.write(b"G28 X Y Z")


if __name__ == "__main__":
    sys.exit(main())



