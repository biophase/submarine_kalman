import pygame as pg
import sys, getopt

args = sys.argv[1:]
try:
    opts,args = getopt.getopt(args,'r:',['resolution='])
except:
    pass

WIDTH, HEIGHT = 800, 800 # default resolution if not 'full screen' or 'custom'
custom_resolution = False # can be overwritten with arguments from console
# custom_resolution = True

for opt,arg in opts:
    if opt == '-r' or '--resolution':
        WIDTH,HEIGHT = map(int,arg.split('x'))
        custom_resolution = True
    else:
        USING_SYSTEM_RESOLUTION = True

if sys.platform == 'win32' and custom_resolution==False:
    try:
        from win32api import GetSystemMetrics
        USING_SYSTEM_RESOLUTION = True # when True the simulation runs in full screen
    except:
        USING_SYSTEM_RESOLUTION = False    
else:
    USING_SYSTEM_RESOLUTION = False

#set window size to full screen (windows only)

if USING_SYSTEM_RESOLUTION:
    WIDTH, HEIGHT = (GetSystemMetrics(0),(GetSystemMetrics(1)))


#colors and fonts
#BG_COLOR = (30,0,15) #old color
BG_COLOR = (45,35,55)
BG_COLOR_SUBMERGED = (5,10,25)
DEFAULT_TEXT_COLOR = (255,255,255,170)
DEFAULT_TEXT_SIZE = 15
DEFAULT_FONT = 'Arial'
LINE_COLOR_WHITE = (255,255,255)
LINE_COLOR_GREEN = (0,200,0)
LINE_COLOR_DARKGREEN = (0,80,0)
LINE_COLOR_RED = (150,0,0)
LINE_COLOR_DARKRED = (50,0,0)
LINE_COLOR_DARKBLUE = (0,100,100)
FPS = 30
WIN = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption ('sub simulation')

#submarine physics
SUB_ACCELERATION = 3e-1 # this can be interpreted as engine power
SUB_ACCELERATION_DECAY = 0.1 # this can be interpreted as drag

ARROW_KEYS = { # maps arro key presses to acceleration vectors
    1073741906 : ['UP',(0,-1)],
    1073741904 : ['LEFT',(-1,0)],
    1073741905 : ['DOWN',(0,1)],
    1073741903 : ['RIGHT',(1,0)] 
}


