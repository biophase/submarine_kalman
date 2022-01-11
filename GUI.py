import pygame as pg
import numpy as np
import submarine
from constants import *

pg.font.init()

class GUI:
    text_objects = {}
    myfont = pg.font.SysFont(DEFAULT_FONT, DEFAULT_TEXT_SIZE)

    def add_text_object(key = ("Text_object_" + str(len(text_objects))), value = "",color = DEFAULT_TEXT_COLOR):
        try:
            GUI.text_objects[key] = GUI.myfont.render(key + str(value), True, color)
        except:
            pass
    def remove_text_object(key):
        del GUI.text_objects[key]
    
    def draw(window,pos):
        for i, key in enumerate(GUI.text_objects):
            if str(key).startswith('Ground truth'):
                window.blit(GUI.text_objects[key], np.array(pos) + np.array([90,(DEFAULT_TEXT_SIZE+5)*i]))
                temp_sub = submarine.Submarine(7,50,(DEFAULT_TEXT_SIZE+5)*(i+1),45)
                temp_sub.sigma_q=0
                temp_sub.sigma_r=0
                temp_sub.update(np.array([-1,0]),submerged = False)                
                temp_sub.draw()
            elif str(key).startswith('Estimated position'):
                window.blit(GUI.text_objects[key], np.array(pos) + np.array([90,(DEFAULT_TEXT_SIZE+5)*i]))
                temp_sub = submarine.Submarine(7,50,(DEFAULT_TEXT_SIZE+5)*(i+1),45,fill_color=LINE_COLOR_RED,line_color=LINE_COLOR_RED)
                temp_sub.sigma_q=0
                temp_sub.sigma_r=0
                temp_sub.update(np.array([-1,0]),submerged = False)                
                temp_sub.draw()
            else:
                window.blit(GUI.text_objects[key], np.array(pos) + np.array([0,DEFAULT_TEXT_SIZE+5])*i)
        GUI.text_objects = {}
        #window.blit(GUI.textsurface,pos)


class CurrentBackground:
    current = np.zeros(3)

    def set(color):
        CurrentBackground.current = np.array(color,dtype = float)
        