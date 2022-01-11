#external libraries
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame as pg
import numpy as np
from numpy.random import default_rng

#own imports
from constants import *
from submarine import Submarine
from GUI import *
import VectorGrid as vg



def draw_window(submerged = False, draw_estimated = False,draw_real = True, gps_on = False, draw_ff=True): 
    


    #fill window with background color
    if submerged:
        target_color = np.array(BG_COLOR_SUBMERGED,dtype = float)
    else:
        target_color = np.array(BG_COLOR, dtype = float)
    CurrentBackground.current -= (CurrentBackground.current-target_color)*0.3
    WIN.fill(CurrentBackground.current)

    #draw vector field
    if draw_ff:
        vector_field.UpdateLayer()
        grid.GridInView((1000,0),vector_field)

    #draw GUI
    GUI.draw(WIN,(10,10))
    
    #draw submarines
    if draw_real:
        real_sub.draw()
    if draw_estimated:
        estimated_sub.draw()
    if gps_on:
        real_sub.gps_draw_measure()

    #refresh screen
    pg.display.update()    


def main():
    #########################
    # global loop variables #
    #########################

    clock = pg.time.Clock()
    ticks = 0 

    ############################
    # user-controlled variabes #
    ############################

    arrows = []  #direction of submarine, set with the arrow keys    

    imu_drift = 0.5 # ussually submarine IMUs are pretty accurate but for the sake of the experiment
                  # the accracy of the IMUs can be varied. Higher value means more drift in sensor

    submerged = False # wether the submarine is submerged. while submerged the submarine doesn't recieve gps corrections

    gps_on = False # wether gps measurements get drawn

    draw_estimated = False # wether to draw estimated (by GPS and/or IMU) position of submarine

    draw_real = True # wether to draw real position of submarine

    draw_ff = False # wether flow field will be drawn

    draw_menu = True # wether to draw GUI menu


    run = True 

    #############
    # MAIN LOOP #
    #############
    # hello hello v2
    while run:
        clock.tick(FPS)
        ticks += 1

#GPS measurement every couple of frames
        if ticks % 1 == 0:
            real_sub.gps_measure()
            if submerged == False:
                correction_vector = estimated_sub.pos - np.mean(real_sub.measurements, axis = 0)
                estimated_sub.pos = estimated_sub.pos - correction_vector
                estimated_sub.velocity -= correction_vector*0.01 

        for event in pg.event.get():
            
            if event.type == pg.QUIT:
                run = False

# Key down
            if event.type == pg.KEYDOWN:
                #check whether its an arrow key
                try:
                    arrow = ARROW_KEYS [event.key] # get arrow(an acceleration vector) from the {key:vector} dictionary
                    if arrow[1] not in arrows:
                        arrows.append(arrow[1]) # append the acceleration vector to a list, which we later sum
                except KeyError:
                    pass
                
                if event.key == 103: # check if user presses 'g' and switch gps on/off
                    gps_on = not gps_on
                if event.key == 115: # check if user presses 's' and submerge/raise submarine
                    submerged = not submerged 
                if event.key == 101: # check if user presses 'e' and show/hide estimated position
                    draw_estimated = not draw_estimated
                if event.key == 114: # check if user presses 'r' and show/hide real position
                    draw_real = not draw_real                    
                if event.key == 102: # check if user presses 'f' and show/hide vector/flow field
                    draw_ff = not draw_ff
                if event.key == 120 and (event.mod == 4096 or event.mod == 0): # check if user presses 'x' and exit
                    run = False           
                if event.key == 120 and (event.mod == 4097 or event.mod == 1): # check if user presses 'Shift+x' and reset simulation
                    real_sub.reset()
                    estimated_sub.reset()
                if event.key == 27: # check if user presses 'ESC and toggle menu
                    draw_menu = not draw_menu
                

                #print(event.key) # --> use this to find out keyboard key IDs

# Key up
            #remove the released component from the list with acceleration vectors
            if event.type == pg.KEYUP:
                try:
                    arrow = ARROW_KEYS [event.key]
                    if arrow[1]  in arrows:
                        arrows.remove(arrow[1])
                except KeyError:
                    pass # pass if another (non-arrow) key is released
        
        try:
            acceleration = np.sum(arrows,axis =0)

            real_sub.update(acceleration)

            #calculate drift
            if draw_ff:
                drift = np.array(vector_field.Sample(estimated_sub.pos))*0.3 # vector_field drift from flow field and scale it
            else:
                rng = default_rng()
                drift = rng.normal(0,1,size =2)*imu_drift # vector_field drift from random normal distribution

            estimated_sub.update(acceleration + drift) # add drift to acceleration vector
             
                
        except:
            pass
        try:
            if draw_menu: #adds a simple GUI list to display values on the screen
                GUI.add_text_object('CONTROLS :', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('____________________________________', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('  ', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [ARROWS KEYS] to move submarine', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [S] to submerge submarine', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [E] to show measured submarine position', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [R] to show real submarine position', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [G] to show GPS readings', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [F] to toggle flow field', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [SHIFT+X] to reset simulaiton', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [X] quit', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('press [ESC] to toggle this menu', ' ',color = LINE_COLOR_WHITE)
                            
                GUI.add_text_object('____________________________________ ', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object(' ', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('acceleration[x,y] = ', np.sum(arrows,axis = 0),color = LINE_COLOR_GREEN)
                GUI.add_text_object('IMU drift coeficcient = ', imu_drift,color = LINE_COLOR_GREEN)
                GUI.add_text_object('View GPS readings = ', gps_on, color = LINE_COLOR_GREEN)
                GUI.add_text_object('Submerged = ', submerged, color = LINE_COLOR_GREEN)
                GUI.add_text_object('Show estimated position= ', draw_estimated, color = LINE_COLOR_GREEN)
                GUI.add_text_object('Show real position = ', draw_real, color = LINE_COLOR_GREEN)
                GUI.add_text_object('Flow field active = ', draw_ff, color = LINE_COLOR_GREEN)

                GUI.add_text_object('____________________________________  ', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('   ', ' ',color = LINE_COLOR_WHITE)            
                GUI.add_text_object('Ground truth', ' ',color = LINE_COLOR_WHITE)
                GUI.add_text_object('Estimated position', ' ',color = LINE_COLOR_WHITE)                

        except:
            pass
        

        draw_window(submerged,draw_estimated, draw_real, gps_on,draw_ff) # call main draw function and pass relevant variables


    pg.quit()
    

if __name__=='__main__':

    CurrentBackground.set(BG_COLOR) #initialize background color
    real_sub = Submarine(5,35) # create ground truth submarine
    estimated_sub =Submarine(5,35,fill_color =[180,0,50],line_color=LINE_COLOR_RED) # create submarine for displaying calculated values
    grid = vg.Grid(64,32) # initialize grid for vector field
    vector_field = vg.VectorGrid(4,0.3,0.25) # initialize vector field
    
    main()