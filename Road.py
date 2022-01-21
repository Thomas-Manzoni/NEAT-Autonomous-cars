# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 13:10:50 2022

@author: manzo
"""

import pygame
import os
import random
import math
import sys

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 700

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
TRACK = pygame.image.load(os.path.join("CarAssets", "track2.png"))

TRACK_WIDTH = 80
TRACK_PIECE_LENGHT = 800
TRAF_WIDTH = 15
class Road:
    def __init__(self):
        self.points = [(0, SCREEN_HEIGHT/2, 0)]
        
    def addpoint(self):        
        l = len(self.points)-1
        if l == 0:
            new_point_y = SCREEN_HEIGHT/2
        else:
            last_point_y = self.points[l][1]
            new_point_y = random.randint(last_point_y-150, last_point_y+150)
        if new_point_y > SCREEN_HEIGHT - TRACK_WIDTH-50:
            new_point_y = SCREEN_HEIGHT - TRACK_WIDTH-50
        if new_point_y < TRACK_WIDTH+50:
            new_point_y = TRACK_WIDTH+50
        if random.randint(0,20) == 21:
            self.points.append((self.points[l][0]+200,new_point_y,1))
        else:
            self.points.append((self.points[l][0]+200,new_point_y,0))
        
    def draw(self,i):
        #pygame.draw.circle(SCREEN, (0, 255, 110, 0), self.points[i], 3)
        if (i > 0):
            pygame.draw.line(SCREEN, (2, 105, 31, 255), (self.points[i-1][0], self.points[i-1][1]+TRACK_WIDTH), (self.points[i][0], self.points[i][1]+TRACK_WIDTH), 22)
            pygame.draw.line(SCREEN, (2, 105, 31, 255), (self.points[i-1][0], self.points[i-1][1]-TRACK_WIDTH), (self.points[i][0], self.points[i][1]-TRACK_WIDTH), 22)
        if (self.points[i][2] == 1):
            pygame.draw.line(SCREEN, (255, 0, 0, 255), (self.points[i][0], self.points[i][1] + TRAF_WIDTH ), (self.points[i][0], self.points[i][1] - TRAF_WIDTH ), 5)
        if (self.points[i][2] == 2):
            pygame.draw.line(SCREEN, (0, 255, 0, 255), (self.points[i][0], self.points[i][1] + TRAF_WIDTH ), (self.points[i][0], self.points[i][1] - TRAF_WIDTH ), 5)
    
    def shift(self):  
        for h in range(5):
            self.points.pop(0)
        for i in range(5):
            self.addpoint()
        for i in range(len(self.points)):
            self.points[i] = (self.points[i][0] - 1000, self.points[i][1], self.points[i][2])
    
    def change_traf(self, i):
         if (self.points[i][2] == 1):
             self.points[i] = (self.points[i][0], self.points[i][1], 2)
    
    
    
# if __name__ == '__main__':
#     r = Road()
#     move_up = False
#     #SCREEN.blit(TRACK, (0, 0))
#     SCREEN.fill((0,0,0))
#     a = 0
#     h = 0
#     index = 0
#     for i in range(50):
#         r.addpoint()
    
#     while True:
#         SCREEN.fill((0,0,0))
#         a += 1
#         for i in range(len(r.points)):
#             r.draw(i)
        
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 quit()
                
            
            
             
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_w:
#                     move_up = True
#                     h = 1
                    
#             if event.type == pygame.KEYUP:
#                 if event.key == pygame.K_w:
#                     move_up = False
                    
#             # if move_up:    
#             #     for i in range(len(r.points)):
#             #         r.points[i] = (r.points[i][0] - 20, r.points[i][1])
#             if h == 1:
#                 r.shift()
#                 h = 0
                
        
#         pygame.display.update()
#         if(a >50000):
#             break
    
#     pygame.quit() 
      
    
    