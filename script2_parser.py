import re 
import math
import numpy as np

P1 = [10, 0, 200]
P2 = [0, -10, 200]
P3 = [0, 10*math.sqrt(10), 200]
height = 50 # frame coordinates for home is [0,0,50]
home = [0, 0, 0] # in cartesian coordinates
# we also want home in cartesian so we can find the lengths of the line
a0 = 0
b0 = 0
b0 = 0

def setHome():
    a0 = getEuclideanDistance(home, P1)
    b0 = getEuclideanDistance(home, P2)
    c0 = getEuclideanDistance(home, P3)

def getEuclideanDistance(P1, P2):
    return math.sqrt((P2[0]-P1[0])**2 + (P2[1]-P1[1])**2 + (P2[2]-P1[2])**2)

def getSegments(P1, P2):
    """ 
    Gets the segments between two points

    param X1: x coordinate of points 1
    param Y1: y coordinate of points 1
    param Z1: z coordinate of points 1
    param X2: x coordinate of points 2
    param Y2: y coordinate of points 2
    param Z2: z coordinate of points 2
    return: an array of points
    """
    epsilon = 0.005
    segments = []
    if (getEuclideanDistance(P1, P2) < epsilon):
        return [[P1[0], P1[1], P1[2]], [P2[0], P2[1], P2[2]]]
    else:
        distance = getEuclideanDistance(P1, P2)
        spacing_between_points = 3
        number_of_segments = int(math.ceil(distance / spacing_between_points))
        xs = np.linspace(P1[0], P2[0], number_of_segments + 2) # add 2 for the start and end points
        ys = np.linspace(P1[1], P2[1], number_of_segments + 2)
        zs = np.linspace(P1[2], P2[2], number_of_segments + 2)

        for i in range(len(xs)):
            segments.append([xs[i], ys[i], zs[i]])

    return segments


def getFrameCoordinates(X, Y, Z):
    line1 = math.sqrt((P1[0]-X)**2 + (P1[1]-Y)**2 + (P1[2]-Z)**2) - home[0]
    line2 = math.sqrt((P2[0]-X)**2 + (P2[1]-Y)**2 + (P3[2]-Z)**2) - home[1]
    line3 = math.sqrt((P3[0]-X)**2 + (P2[1]-Y)**2 + (P3[2]-Z)**2) - home[2]
    print(line1, line2, line3)
    return line1, line2, line3

def parseGCode():
    with open('cube72.gcode') as gcode:
        f = open(str("gcode_data.gcode"), 'w')

        for line in gcode:
            split = line.split()
            if (len(split) == 1): # G1 or G0 command
                f.write(split[0] + '\n')
            else:
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if (len(numbers) > 0):
                    G = numbers[0]
                    X = numbers[1]
                    Y = numbers[2]
                    Z = numbers[3]
                    getFrameCoordinates(X, Y, Z)
                    f.write("G" + str(G) +  " A" + str(X) + " B" + str(Y) + " C" + str(Z) + "\n")

# parseGCode()
getSegments([0,0,0], [5,5,5])