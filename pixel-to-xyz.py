import re 
import math
import numpy as np
import sys

conversion_factor = 50 # mm/pixel
top_left_x = -6000 # top left coordinate
top_left_y = -4000

# x, y pixel coordinates to x, y, z cartesian coordinates
def pixelToCoord(x, y):
    x = x * conversion_factor + top_left_x
    y = y * conversion_factor + top_left_y

    return [x, y, 1000] # fixed z height