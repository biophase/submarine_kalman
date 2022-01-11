import numpy as np
from numpy.lib.function_base import delete
import pygame as pg
import pygame.gfxdraw as gfx

from constants import *
from GUI import *

delta_t = 1

class Submarine:
    def __init__(self,width,length,pos_x = HEIGHT /2,pos_y = WIDTH/2, fill_color = LINE_COLOR_GREEN,line_color = LINE_COLOR_GREEN):
        # graphics
        self.width = width # size of submarine
        self.length = length # size of submarine
        self.velocity = 0 # current velocity
        self.pos = np.array([pos_y,pos_x]) # current position in world
        self.pos_history = [] # position history for displaying trail
        self.fill_color = fill_color 
        self.line_color = line_color
        self.measurements = [] # used to store GPS location

        # noise
        self.sigma_q = 1.0
        self.sigma_r = 40

        # definitions for kalman filter
        self.A = np.array   ([[1, delta_t],[0,SUB_ACCELERATION*SUB_ACCELERATION_DECAY]],dtype=np.float32) # dynamic model with acceleration decay
        self.x_previous_posterior = np.array([[pos_y, pos_x], [0,0]], dtype = np.float32) # previous estimate for state vector "x"-> initialize in center of screen and 0 velocity
        self.x_current_prior = np.array([[pos_y, pos_x], [0,0]], dtype = np.float32) # current estimate for state vector "x"-> initialize in center of screen and 0 velocity
        self.B = np.array([[(delta_t**2)/2],[delta_t]]) # matrix to transform control vector "u" to a [position, velocity]-matrix
        self.P_current_prior = np.array([[0,0],[0,0]], dtype = np.float32) # covariance matrix of current state vector prior
        self.P_previous_posterior = np.array([[0,0],[0,0]], dtype = np.float32) # covariance matrix of previous state vector posterior
        self.Q = np.array([[self.sigma_q**2,0],[0,self.sigma_q**2]], dtype = np.float32) # Covariance matrix of process noise
        self.H = np.array([[1,0],[0,0]], dtype = np.float32) # Measurment matrix
        self.R = np.array([[self.sigma_r**2,0],[0,self.sigma_r**2]], dtype = np.float32) 
        self.x_current_posterior =  np.array([[0,0], [0,0]], dtype = np.float32)
        self.P_current_posterior = np.array([[0,0],[0,0]], dtype = np.float32) # covariance matrix of current state vector posterior





    def gps_measure(self):
        #Draw some measures around a given submarine and store the result in the instance 
        num_samples = 1
        rng = np.random.default_rng()
        measure =  rng.normal(loc = self.pos, scale = self.sigma_r, size = (2))
        if len(self.measurements) > FPS*10: self.measurements.pop(0)
        self.measurements.append(measure)

        
                
    def gps_draw_measure(self,draw_color = LINE_COLOR_DARKGREEN,draw_color_main = LINE_COLOR_DARKBLUE,
                         draw_radius = 1, draw_radius_main = 3,surface = WIN):
        for i,measure in enumerate(self.measurements):
            pg.draw.circle(surface,color = draw_color,radius=(FPS*10-(len(self.measurements)-i))*0.007,center=measure)
            # pg.draw.circle(surface,color = draw_color,radius=FPS*0.07-i*0.001,center=measure)
        if len(self.measurements) > 0:
            pg.draw.circle(surface,color = draw_color_main,radius=draw_radius_main,center=self.measurements[-1])

    def draw(self):
        try:
            #draw trail
            if len(self.pos_history)>2:
                pg.draw.aalines(WIN,self.line_color,closed=False,points=self.pos_history)
            #draw contours
            pg.draw.aalines(WIN,self.line_color,closed=True,points=self.corners)
            gfx.filled_polygon(WIN,self.corners,(*self.fill_color,50))
            #draw head
            pg.draw.aalines(WIN,self.line_color,closed=False,points=(np.average(self.corners[1:3,:],axis=0),self.pos))
            #draw direction
            direction = np.average(self.corners[1:3,:],axis=0) - self.pos
            pg.draw.aalines(WIN,self.line_color,closed=False,
                    points=[np.average(self.corners[1:3,:],axis=0),
                    np.average(self.corners[1:3,:],axis=0)+direction*(np.linalg.norm(self.velocity)/7)**2
                    ])
        except:
            pass

        

#return submarine to center and reset acceleration and history        
    def reset(self):
        self.pos = (WIDTH/2, HEIGHT/2)
        self.pos_history =[]
        self.velocity = (0,0)

    def update(self,acceleration):
        #update history         
        if len(self.pos_history) > FPS*10:
            self.pos_history.pop(0)
        #update position
        self.velocity = self.velocity + acceleration * SUB_ACCELERATION 
        if np.linalg.norm(self.velocity) > 0:
            self.velocity = self.velocity + np.negative(self.velocity)*SUB_ACCELERATION*SUB_ACCELERATION_DECAY
        self.pos = self.pos + self.velocity
        
        #update corners        
        self.corners = np.squeeze(np.array(
            [


                [self.pos-np.array([-self.length/2,-self.width/2])],
                [self.pos-np.array([self.length/2,-self.width/2])],
                [self.pos-np.array([self.length/2,self.width/2])],
                [self.pos-np.array([-self.length/2,self.width/2])],
            ])
        )

        direction = self.velocity / np.linalg.norm(self.velocity)

        #update rotation

        rot_matrix = [
            [-direction[0],direction[1]],
            [-direction[1],-direction[0]]
            ]
        self.corners -= self.pos
        for i, corner in enumerate(self.corners):
            self.corners[i,:] = np.matmul( rot_matrix, self.corners[i,:])

        self.corners += self.pos
        self.pos_history.append(self.pos)


