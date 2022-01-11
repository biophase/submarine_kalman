import numpy as np
from numpy.lib.function_base import interp
from numpy.random.mtrand import sample
from perlin_numpy import (
    generate_perlin_noise_2d, generate_fractal_noise_2d,
    generate_fractal_noise_3d
)

import pygame as pg

from submarine import Submarine
from constants import *

# commented these out since they are already defined in "contants.py"
# WIDTH, HEIGHT = 1900, 900
# BG_COLOR = (30,0,15)
# LINE_COLOR_GREEN = (0,100,100)
# LINE_COLOR_RED = (150,0,0)
# LINE_COLOR_DARKRED = (50,0,0)
# FPS = 60
# WIN = pg.display.set_mode((WIDTH,HEIGHT))
# pg.display.set_caption ('sub simulation')

class VectorGrid:
    def __init__(self,octave = 4, persistance = 0.3, sampleScale = 0.1):
        self.dimension = 256
        self.resolution = (2,2)
        self.octave = octave
        self.persistance = persistance
        self.lancunarity = 2
        self.tileable = (True,True)
        
        self.sampleScale = sampleScale
        
        self.interValue = 0

        self.GenerateNoise()
        pass

    def GenerateNoise(self):
        np.random.seed(0)
        self.layerTick = 0;
        self.lastLayer = 0;
        #self.noise = generate_fractal_noise_2d((self.dimension,self.dimension), self.resolution, self.octave, self.persistance,self.lancunarity,self.tileable)
        self.noise_3D = generate_fractal_noise_3d((8,self.dimension,self.dimension), (1, 1, 1), 4, tileable=(True, True, True))
        self.noise = self.noise_3D[0]
        self.noise_next = self.noise_3D[1]
        pass

    def UpdateLayer(self):
        self.layerTick+=1
        tick = int(self.layerTick/10)
        self.interValue = self.layerTick%10 / 10

        if(tick>self.lastLayer):
            self.lastLayer+=1
            index = self.lastLayer%8
            index_next = (self.lastLayer+1)%8
            self.noise = self.noise_3D[index]
            self.noise_next = self.noise_3D[index_next]
        pass

    def Sample(self,worldPos):
        v_y_ceil = np.ceil(worldPos[0]*self.sampleScale)
        v_y_floor = v_y_ceil-1
        v_x_ceil = np.ceil(worldPos[1]*self.sampleScale)
        v_x_floor = v_x_ceil-1

        _y_ceil = v_y_ceil % (self.dimension-1)
        _y_floor = v_y_floor % (self.dimension-1)
        _x_ceil = v_x_ceil % (self.dimension-1)
        _x_floor = v_x_floor % (self.dimension-1)

        value_1 = self.noise[int(_y_floor)][int(_x_floor)]       
        value_2 = self.noise[int(_y_floor)][int(_x_ceil)]
        value_3 = self.noise[int(_y_ceil)][int(_x_floor)]
        value_4 = self.noise[int(_y_ceil)][int(_x_ceil)]

        value_avg = (value_1+value_2+value_3+value_4)/4

        value_1_next = self.noise_next[int(_y_floor)][int(_x_floor)]       
        value_2_next = self.noise_next[int(_y_floor)][int(_x_ceil)]
        value_3_next = self.noise_next[int(_y_ceil)][int(_x_floor)]
        value_4_next = self.noise_next[int(_y_ceil)][int(_x_ceil)]

        value_avg_next = (value_1_next+value_2_next+value_3_next+value_4_next)/4

        value = value_avg * (1-self.interValue) + value_avg_next * self.interValue

        result = self.Vectorize(value)

        return result
        
    def SampeOnGrid(self,GridPos):
        index_y = int(GridPos[0]*self.sampleScale) % self.dimension
        index_x = int(GridPos[1]*self.sampleScale) % self.dimension
        value_1 = self.noise[index_y][index_x]
        value_2 = self.noise_next[index_y][index_x]
        value = value_1 * (1-self.interValue) + value_2 * self.interValue

        result = self.Vectorize(value)

        return result

    def SampeOnGridGradian(self,GridPos):
        index_y = int(GridPos[0]*self.sampleScale) % self.dimension
        index_x = int(GridPos[1]*self.sampleScale) % self.dimension
        value_1 = self.noise[index_y][index_x]
        value_2 = self.noise_next[index_y][index_x]
        value = value_1 * (1-self.interValue) + value_2 * self.interValue
        
        result = self.VectorizeOrtho(value)

        return result

    def Vectorize(self,value):
        value = (value - 0.5)*np.pi*2
        x = np.cos(value)
        y = np.sin(value)

        return (x,y)

    def VectorizeOrtho(self,value):
        value = (value - 0.5)*np.pi*2+0.5*np.pi
        x = np.cos(value)
        y = np.sin(value)

        return (x,y)
    
    def PrintNoise(self):
        print(self.noise)
        pass

class Grid:
    def __init__(self,cell_size,dimension):
        self.cell_size = cell_size
        self.dimension = dimension-1
        self.x_start = -int(dimension/2)
        self.y_start = -int(dimension/2)
        self.grid = [[0 for x in range(self.dimension)] for y in range(self.dimension)] 
        pass
    
    def GridInView(self,CamPos,sample:VectorGrid):
        for y in range(0,self.dimension):
            for x in range(0,self.dimension):
                self.grid[y][x] = ((self.y_start+y)*self.cell_size + CamPos[0],(self.x_start+x*self.cell_size)+CamPos[1])
        self.SampleGrid(sample)
        pass

    def GridGradianInView(self,CamPos,sample:VectorGrid):
        for y in range(0,self.dimension):
            for x in range(0,self.dimension):
                self.grid[y][x] = ((self.y_start+y)*self.cell_size + CamPos[0],(self.x_start+x*self.cell_size)+CamPos[1])
        self.SampleGridGradian(sample)
        pass

    def SampleGrid(self,sample:VectorGrid):
        for y in range(0,self.dimension):
            for x in range(0,self.dimension):    
                turple = self.grid[y][x] 
                vector = sample.SampeOnGrid(turple)
                start = [turple[0],turple[1]]
                end = [turple[0]+vector[0]*30,turple[1]+vector[1]*30] # Made the vector longer for a sparse grid #Hristo
                #pg.draw.aalines(WIN,LINE_COLOR_GREEN,closed=False,points=[[1000,0],[0,6000]])
                pg.draw.aalines(WIN,LINE_COLOR_DARKBLUE,closed=False,points=[start,end])
        pass     

    def SampleGridGradian(self,sample:VectorGrid):
        for y in range(0,self.dimension):
            for x in range(0,self.dimension):    
                turple = self.grid[y][x] 
                vector = sample.SampeOnGridGradian(turple)
                start = [turple[0]-vector[0]*8,turple[1]-vector[1]*8]
                end = [turple[0]+vector[0]*8,turple[1]+vector[1]*8]
                #pg.draw.aalines(WIN,LINE_COLOR_GREEN,closed=False,points=[[1000,0],[0,6000]])
                pg.draw.aalines(WIN,LINE_COLOR_GREEN,closed=False,points=[start,end])
        pass 

def draw_window(): 
    WIN.fill((BG_COLOR))
    #grid.GridGradianInView((1000,0),sample)
    
    
    #particle.draw() #draw test particle

    sample.UpdateLayer()
    grid.GridInView((1000,0),sample)
    pg.display.update()    
    pass


def main():
    clock = pg.time.Clock()
    run = True 
    while run:
        #particle.update(np.array(sample.Sample(particle.pos))*5)
        #print(type(sample.Sample(particle.pos)))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        clock.tick(FPS)
        draw_window()
    pg.quit()
    pass

if __name__ == '__main__':
    grid = Grid(32,64)
    sample = VectorGrid(4,0.3,0.25)
    #particle = Submarine(10,10)
    main()
