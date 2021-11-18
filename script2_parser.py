import re 
import math
import numpy as np
import sys

P1 = [-170, -99, 150]
P2 = [0, 196.3, 150]
P3 = [170, -99, 150]
height = 10 # frame coordinates for home is [0,0,50]
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

def parseGCode(args):
    a0, b0, c0 = getHomeInFrameCoordinates()
    with open(args[1]) as gcode:
        f = open(args[2], 'w')

        prev_line = None
        for line in gcode:
            if prev_line is not None:
                split = prev_line.split()

                prev_numbers = re.findall(r"[-+]?\d*\.\d+|\d+", prev_line)
                curr_numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)

                if (len(prev_numbers) == 2): # for F command
                    f.write(split[0] + " " + split[1] + '\n')
                else:
                    if (len(curr_numbers) > 3 and len(prev_numbers) > 3):
                        prev_G = int(prev_numbers[0])
                        curr_G = int(curr_numbers[0])
                        segments = []
                        # only want to segment lines, not travel moves
                        if ((prev_G == 0 and curr_G == 1) or (prev_G == 1 and curr_G == 1)):
                            segments = getSegments(prev_numbers[1:], curr_numbers[1:]) # exclude the first number because that's G

                        for i in range(len(segments)):
                            point = segments[i]
                            A = getEuclideanDistance(P1, point) - a0
                            B = getEuclideanDistance(P2, point) - b0
                            C = getEuclideanDistance(P3, point) - c0
                            if i == 0:
                                f.write("G" + str(prev_G) +  " X" + str(A) + " Y" + str(B) + " Z" + str(C) + "\n")
                            else:
                                f.write("G" + str(curr_G) +  " X" + str(A) + " Y" + str(B) + " Z" + str(C) + "\n")
            prev_line = line

def main():
    if len(sys.argv) != 3:
        print("USAGE: python3 script.py <input filename> <output filename>")
        exit()
    parseGCode(sys.argv)


if __name__ == '__main__':
	main()