import numpy as np
from numpy.lib.function_base import delete
import pygame as pg
import pygame.gfxdraw as gfx

from constants import *
from GUI import *
from utils import draw_cross

delta_t = 1

class Submarine:
    
    # static variables
    force_K_zero = True
    
    def __init__(self,width,length,pos_x = HEIGHT /2,pos_y = WIDTH/2,\
        fill_color = LINE_COLOR_GREEN,line_color = LINE_COLOR_GREEN,\
        draw_cross=True,draw_sub = True, line_color_est = LINE_COLOR_RED):
        


        # graphics
        self.width = width # size of submarine
        self.length = length # size of submarine
        self.fill_color = fill_color 
        self.line_color = line_color
        self.line_color_est = line_color_est
        self.measurements = [] # used to store GPS location
        self.draw_cross = draw_cross
        self.draw_sub = draw_sub

        # extracted from state vector for vizualization
        self.velocity_real = np.zeros((2,)) # current real velocity
        self.velocity_est = np.zeros((2,)) # current estimated velocity
        self.pos_real = np.array([pos_y,pos_x]) # current real position in world
        self.pos_real_history = [] # position history for displaying trail
        self.pos_est = np.array([pos_y,pos_x]) # current real position in world
        self.pos_est_history = [] # position history for displaying trail

        # state vector
        self.x_real = np.array([[pos_y,pos_x],[0,0]], dtype = np.float32) # real state vector
        self.x_est = np.array([[pos_y,pos_x],[0,0]], dtype = np.float32) # estimated state vector

        # noise
        self.sigma_q = 0.1 # process
        self.sigma_r = 40 # measurement

        # definitions for kalman filter
        self.A = np.array   ([[1, delta_t],[0,1-SUB_ACCELERATION*SUB_ACCELERATION_DECAY]],dtype=np.float32) # dynamic model with acceleration decay
        self.x_previous_posterior = np.array([[pos_y, pos_x], [0,0]], dtype = np.float32) # previous estimate for state vector "x"-> initialize in center of screen and 0 velocity
        self.x_current_prior = np.array([[pos_y, pos_x], [0,0]], dtype = np.float32) # current estimate for state vector "x"-> initialize in center of screen and 0 velocity
        self.B = np.array([[(delta_t**2)/2,(delta_t**2)/2],[delta_t,delta_t]]) # matrix to transform control vector "u" to a [position, velocity]-matrix
        self.P_current_prior = np.array([[0,0],[0,0]], dtype = np.float32) # covariance matrix of current state vector prior
        self.K = np.array([[0,0],[0,0]], dtype = np.float32) # Kalman gain
        self.z = np.array([[0,0],[0,0]], dtype = np.float32) # GPS measurement
        self.P_previous_posterior = np.array([[0,0],[0,0]], dtype = np.float32) # covariance matrix of previous state vector posterior
        self.Q = np.array([[self.sigma_q**2,0],[0,self.sigma_q**2]], dtype = np.float32) # Covariance matrix of process noise
        self.H = np.array([[1,0],[0,0]], dtype = np.float32) # Measurment matrix
        self.R = np.array([[self.sigma_r**2,0],[0,self.sigma_r**2]], dtype = np.float32) 
        self.x_current_posterior =  np.array([[0,0], [0,0]], dtype = np.float32)
        self.P_current_posterior = np.array([[0,0],[0,0]], dtype = np.float32) # covariance matrix of current state vector posterior


        
                
    def gps_draw_measure(self,draw_color = LINE_COLOR_DARKGREEN,draw_color_main = LINE_COLOR_DARKBLUE,
                         draw_radius = 1, draw_radius_main = 3,surface = WIN):
        for i,measure in enumerate(self.measurements):
            pg.draw.circle(surface,color = draw_color,radius=(FPS*10-(len(self.measurements)-i))*0.007,center=measure)
            # pg.draw.circle(surface,color = draw_color,radius=FPS*0.07-i*0.001,center=measure)
        if len(self.measurements) > 0:
            pg.draw.circle(surface,color = draw_color_main,radius=draw_radius_main,center=self.measurements[-1])

    def draw(self):
        if self.draw_sub:

            #draw trails
            if len(self.pos_real_history)>2:
                pg.draw.aalines(WIN,self.line_color,closed=False,points=self.pos_real_history)
            if len(self.pos_est_history)>2:
                pg.draw.aalines(WIN,self.line_color_est,closed=False,points=self.pos_est_history)
            #draw body
            pg.draw.aalines(WIN,self.line_color,closed=True,points=self.corners)
            gfx.filled_polygon(WIN,self.corners,(*self.fill_color,50))
            #draw head
            pg.draw.aalines(WIN,self.line_color,closed=False,points=(np.average(self.corners[1:3,:],axis=0),self.pos_real))
            #draw velocity vector
            direction = np.average(self.corners[1:3,:],axis=0) - self.pos_real
            pg.draw.aalines(WIN,self.line_color,closed=False,
                    points=[np.average(self.corners[1:3,:],axis=0),
                    np.average(self.corners[1:3,:],axis=0)+direction*(np.linalg.norm(self.velocity_real)/7)**2
                    ])
            

        if self.draw_cross : 
            draw_cross(self.pos_est)
            # pg.draw.circle(WIN,self.line_color_est,self.pos_est,np.cbrt(np.linalg.det(self.P_current_posterior))*10,width=2)
            pg.draw.circle(WIN,self.line_color_est,self.pos_est,np.sqrt(self.P_current_posterior[0,0])*2,width=2)

        

#return submarine to center and reset acceleration and history        
    def reset(self):
        # self.pos_real = (WIDTH/2, HEIGHT/2)
        # self.pos_real_history =[]
        # self.velocity_real = (0,0)
        self.__init__(self.width,self.length,self.fill_color,self.line_color)

    def update(self, acceleration, submerged):
    #update history         
        if len(self.pos_real_history) > FPS*10:
            self.pos_real_history.pop(0)
        if len(self.pos_est_history) > FPS*10:
            self.pos_est_history.pop(0)
        
    #gps measurement
        # multiply sigma_r by infinity if sumberged
        if submerged: 
            r_factor = 5000
        else:
            r_factor = 1
        rng = np.random.default_rng()
        # measure =  rng.normal(loc = self.pos_real, scale = self.sigma_r*r_factor, size = (2))
        measure = np.random.multivariate_normal(self.pos_real,self.R * r_factor)
        if len(self.measurements) > FPS*10: self.measurements.pop(0)
        self.measurements.append(measure)

    #update position
        # simulate natural state evolution with sampled noise
        self.x_real = np.matmul(self.A, self.x_real) + np.matmul(self.B,  np.diag(acceleration * SUB_ACCELERATION))  \
            + np.matmul(self.B , np.diag(np.random.multivariate_normal([0,0],self.Q)))

        # Kalman filter 

        ### prediction stage
        self.x_current_prior = np.matmul(self.A, self.x_previous_posterior) + np.matmul(self.B , np.diag(acceleration * SUB_ACCELERATION))
        self.P_current_prior = np.matmul(self.A, np.matmul(self.P_previous_posterior,self.A.transpose())) + self.Q
        ### correction stage
        self.K = np.matmul(self.P_current_prior, np.matmul(self.H.transpose(), np.linalg.inv(self.P_current_prior + self.R*r_factor))) # calculate Kalman gain
        if submerged and Submarine.force_K_zero : self.K = np.array([[0,0],[0,0]],dtype = np.float32)
        self.z = np.array([np.mean(self.measurements[-1:],axis=0),[0,0]],dtype = np.float32) # get latest measurement
        self.x_current_posterior = self.x_current_prior + np.matmul(self.K, (self.z - np.matmul(self.H, self.x_current_prior))) # update state estimate with measurement
        self.P_current_posterior = np.matmul((np.eye(2, dtype = np.float32) - np.matmul(self.K, self.H)), self.P_current_prior)
        ### increment state
        self.x_previous_posterior = self.x_current_posterior
        self.P_previous_posterior = self.P_current_posterior
        ### get values for vizualisation
        self.pos_real = self.x_real[0]
        self.velocity_real = self.x_real[1]
        self.pos_est = self.x_current_posterior[0]

        

    #update corners        
        self.corners = np.squeeze(np.array(
            [


                [self.pos_real-np.array([-self.length/2,-self.width/2])],
                [self.pos_real-np.array([self.length/2,-self.width/2])],
                [self.pos_real-np.array([self.length/2,self.width/2])],
                [self.pos_real-np.array([-self.length/2,self.width/2])],
            ])
        )

        direction = self.velocity_real / np.linalg.norm(self.velocity_real)

    #update rotation

        rot_matrix = [
            [-direction[0],direction[1]],
            [-direction[1],-direction[0]]
            ]
        self.corners -= self.pos_real
        for i, corner in enumerate(self.corners):
            self.corners[i,:] = np.matmul( rot_matrix, self.corners[i,:])

        self.corners += self.pos_real
        self.pos_real_history.append(self.pos_real)
        self.pos_est_history.append(self.pos_est)


