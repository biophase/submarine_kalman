#external libraries
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # hide pygame startup message

import pygame as pg
import numpy as np


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

    #draw submarines
    if draw_real:
        real_sub.draw()
    if draw_estimated:
        pass
    if gps_on:
        real_sub.gps_draw_measure()

    #draw GUI
    GUI.draw(WIN,(10,10))

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

    arrows = [[0,0]]  #direction of submarine, set with the arrow keys    

    submerged = False # wether the submarine is submerged. while submerged the submarine doesn't recieve gps corrections

    gps_on = True # wether gps measurements get drawn

    draw_estimated = False # wether to draw estimated position history of submarine

    draw_real = True # wether to draw real position of submarine

    draw_ff = False # wether flow field will be drawn

    draw_menu = True # wether to draw GUI menu

    run = True 
    
    acceleration = np.zeros((2,2),dtype=np.float32) # placeholder acceleration, controlled with arrow keys

    force_K_zero = True # If True Kalman gain is set to 0 when submerged

    #############
    # MAIN LOOP #
    #############
    while run:
        clock.tick(FPS)
        ticks += 1
        for event in pg.event.get():
            
            if event.type == pg.QUIT:
                run = False
# Arrow Keys
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
                # if event.key == 101: # check if user presses 'e' and show/hide estimated position
                #     draw_estimated = not draw_estimated
                if event.key == 114: # check if user presses 'r' and show/hide real position
                    draw_real = not draw_real                    
                if event.key == 102: # check if user presses 'f' and show/hide vector/flow field
                    draw_ff = not draw_ff
                if event.key == 120 and (event.mod == 4096 or event.mod == 0): # check if user presses 'x' and exit
                    run = False           
                if event.key == 120 and (event.mod == 4097 or event.mod == 1): # check if user presses 'Shift+x' and reset simulation
                    real_sub.reset()
                if event.key == 27: # check if user presses 'ESC and toggle menu
                    draw_menu = not draw_menu
                if event.key == 107: # check if user presses 'K' and toggle force_K_zero
                    Submarine.force_K_zero = not Submarine.force_K_zero                
                

                # print(event.key) # --> use this in debug to find out keyboard key IDs

    # Key up
            #remove the released component from the list with acceleration vectors
            if event.type == pg.KEYUP:
                try:
                    arrow = ARROW_KEYS [event.key]
                    if arrow[1]  in arrows:
                        arrows.remove(arrow[1])
                except KeyError:
                    pass # pass if another (non-arrow) key is released
            
        
# Update submarine position
        acceleration = np.sum(arrows,axis =0)
        real_sub.update(acceleration, submerged)
           
                
# GUI

        if draw_menu: #adds a simple GUI list to display values on the screen
            GUI.add_text_object('CONTROLS :', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('____________________________________', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('  ', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('press [ARROWS KEYS] to move submarine', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('press [S] to submerge submarine', ' ',color = LINE_COLOR_WHITE)
            # GUI.add_text_object('press [E] to show measured submarine position', ' ',color = LINE_COLOR_WHITE)
            # GUI.add_text_object('press [R] to show real submarine position', ' ',color = LINE_COLOR_WHITE)
            # GUI.add_text_object('press [G] to show GPS readings', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('press [F] to toggle flow field', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('press [K] to force K=0', ' ',color = LINE_COLOR_WHITE)
            # GUI.add_text_object('press [SHIFT+X] to reset simulaiton', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('press [X] quit', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('press [ESC] to toggle this menu', ' ',color = LINE_COLOR_WHITE)
                        
            GUI.add_text_object('____________________________________ ', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object(' ', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('acceleration[x,y] = ', np.sum(arrows,axis = 0),color = LINE_COLOR_GREEN)
            # GUI.add_text_object('View GPS readings = ', gps_on, color = LINE_COLOR_GREEN if gps_on==True else LINE_COLOR_RED)
            GUI.add_text_object('Submerged = ', submerged, color = LINE_COLOR_GREEN if submerged==True else LINE_COLOR_RED)
            # GUI.add_text_object('Show estimated position= ', draw_estimated, color = LINE_COLOR_GREEN if draw_estimated==True else LINE_COLOR_RED)
            # GUI.add_text_object('Show real position = ', draw_real, color = LINE_COLOR_GREEN if draw_real==True else LINE_COLOR_RED)
            # GUI.add_text_object('Flow field active = ', draw_ff, color = LINE_COLOR_GREEN if draw_ff==True else LINE_COLOR_RED)
            GUI.add_text_object('Force K=0:  ', Submarine.force_K_zero, color = LINE_COLOR_GREEN if Submarine.force_K_zero==True else LINE_COLOR_RED)

            GUI.add_text_object('____________________________________  ', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('   ', ' ',color = LINE_COLOR_WHITE)            
            GUI.add_text_object('Ground truth', ' ',color = LINE_COLOR_WHITE)
            GUI.add_text_object('Estimated position', ' ',color = LINE_COLOR_WHITE)       
            # 
            GUI.add_text_object('____________________________________   ', ' ',color = LINE_COLOR_WHITE)         
            GUI.add_text_object('Standard deviation Location estimate = ',np.sqrt(real_sub.P_current_posterior[0,0]),color = LINE_COLOR_WHITE)
            GUI.add_text_object('Estimate error covariance matrix = ',real_sub.P_current_posterior,color = LINE_COLOR_WHITE)
            GUI.add_text_object('Kalman Gain = ', real_sub.K,color = LINE_COLOR_WHITE)
            



        
# draw screen
        draw_window(submerged,draw_estimated, draw_real, gps_on,draw_ff) # call main draw function and pass relevant variables

# quit
    pg.quit()
    

if __name__=='__main__':
    print('hi')
    CurrentBackground.set(BG_COLOR) #initialize background color
    real_sub = Submarine(5,35) # create ground truth submarine
    # estimated_sub =Submarine(5,35,fill_color =[180,0,50],line_color=LINE_COLOR_RED) # create submarine for displaying calculated values
    grid = vg.Grid(64,32) # initialize grid for vector field
    vector_field = vg.VectorGrid(4,0.3,0.25) # initialize vector field
    
    main()