import numpy as np
import pygame as pg
import pygame.gfxdraw as gfx

from constants import *
from GUI import *

class Submarine:
    def __init__(self,width,length,pos_x = HEIGHT /2,pos_y = WIDTH/2, fill_color = LINE_COLOR_GREEN,line_color = LINE_COLOR_GREEN):
        self.width = width # size of submarine
        self.length = length # size of submarine
        self.velocity = 0 # current velocity
        self.pos = np.array([pos_y,pos_x]) # current position in world
        self.pos_history = [] # position history for displaying trail
        self.fill_color = fill_color 
        self.line_color = line_color
        self.measurements = [] # used to store GPS location

    def gps_measure(self, num_samples = 10, stddev = 1, ):
        #Draw some measures around a given submarine and store the result in the instance 
        rng = np.random.default_rng()
        self.measurements = rng.normal(loc = self.pos, scale = stddev, size = (num_samples,2))
        
                
    def gps_draw_measure(self,draw_color = LINE_COLOR_DARKGREEN,draw_color_main = LINE_COLOR_DARKGREEN,
                         draw_radius = 2, draw_radius_main = 5,surface = WIN):
        for measure in self.measurements:
            pg.draw.circle(surface,color = draw_color,radius=draw_radius,center=measure)
        if len(self.measurements) > 0:
            pg.draw.circle(surface,color = draw_color,radius=draw_radius_main,center=np.mean(self.measurements, axis = 0))

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


