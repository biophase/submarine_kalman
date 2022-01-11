import pygame as pg
import numpy as np
from constants import *

def draw_cross(pos, size=5.0,width=3, color = LINE_COLOR_RED):
    top_left = pos + [-size, -size]
    bot_right = pos + [+size, +size] 
    top_right = pos + [-size, +size]
    bot_left = pos + [+size, -size]

    pg.draw.line(WIN,color,top_left,bot_right, width)
    pg.draw.line(WIN,color,top_right,bot_left, width)