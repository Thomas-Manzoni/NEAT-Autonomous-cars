
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 12:31:15 2021

@author: manzo
"""

import pygame
import os
import random
import math
import sys
import neat
import numpy as np
import sympy as sy
import sympy.geometry as gm
import Road as road
import pickle



pygame.init()

RED = (200,0,0)
FUCSIA = (255,0,255)
YELLOW = (255,255,0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

CAR = pygame.image.load(os.path.join("CarAssets", "carf.png"))

SPEED = 50

FONT = pygame.font.Font('freesansbold.ttf', 20)


TRACK = pygame.image.load(os.path.join("CarAssets", "track2.png"))

SCORES = []

air_density = 1.225
friction_coef = 1.7
drag_coef = 0.7
lift_coef = -2.0
g = 9.8

MAX_FRONT_ACC = 10
DRAG_SCALING = 0.1
MAX_VELOCITY = 10

class Car(pygame.sprite.Sprite):
    def __init__(self, img=CAR):
        super().__init__()
        self.image_ori = img
        # self.image_ori.set_colorkey(WHITE)
        # self.image_ori(WHITE).convert_apha()
        
        self.w_ori = img.get_width()
        self.h_ori = img.get_height()
        
        self.image = img
        
        
        self.front_acc_time = 0

        self.x = 100
        self.y = 350
        self.x_velocity = 0
        self.y_velocity = 0
        self.x_accelleration = 0
        self.y_accelleration = 0
        self.body_orientation = 0
        self.wheels_orientation = 0
        self.mass = 700
        
        self.pedal_time = 0
        
        self.front_area = 1.5
        
        self.rect = self.image.get_rect(center=(self.x, self.y)) #da ytube
        
       # self.rect = pygame.Rect(self.x, self.y, img.get_width(), img.get_height())
        
        self.left_sensor = [0,0]
        self.right_sensor = [0,0]
        
        self.radars = []
        
        self.crashed = False
        
        self.command = [0,0,0,0]
        self.previous_pos = [0,0]
        self.still = 0
        
        self.finish_line = False
        
        self.finish_portion = False
        
        self.infraction = False
     
    def move(self):
        
        if (self.finish_portion == False):
            self.x_velocity += self.x_accelleration/30 #diviso 30 perchè per ogni frame
            self.y_velocity += self.y_accelleration/30
            if (self.x_velocity > 30):
                self.x_velocity = 30
                if (self.y_velocity > 30):
                    self.y_velocity = 30
        
            self.rect.x += self.x_velocity 
            self.rect.y -= self.y_velocity
            
        if (self.finish_portion == True):
            self.x_velocity = 0
            self.y_velocity = 0
            
    def shift(self):
        self.rect.x -= 1000
        
   
        
     
    
    def input_analisys(self):
        self.previous_pos[0] = self.left_sensor[0]
        self.previous_pos[1] = self.left_sensor[1]
        
        if (self.command[0] == 1): #w
            self.pedal_time += 2
            if (self.pedal_time > 90):
                self.pedal_time = 90
                
            self.x_velocity = self.accelleration(self.pedal_time)*np.cos(np.radians(self.body_orientation))
            self.y_velocity = self.accelleration(self.pedal_time)*np.sin(np.radians(self.body_orientation))
           
            
        elif (self.command[3] == 1):
            self.pedal_time -= 4
            if (self.pedal_time < 0):
                self.pedal_time = 0
            
            self.x_velocity = self.accelleration(self.pedal_time)*np.cos(np.radians(self.body_orientation))
            self.y_velocity = self.accelleration(self.pedal_time)*np.sin(np.radians(self.body_orientation))

        else:
            self.pedal_time -= 1
            if (self.pedal_time < 0):
                self.pedal_time = 0
                
            self.x_velocity = self.accelleration(self.pedal_time)*np.cos(np.radians(self.body_orientation))
            self.y_velocity = self.accelleration(self.pedal_time)*np.sin(np.radians(self.body_orientation))
        
            
        if (self.command[1] == 1 and ((self.x_velocity**2 + self.y_velocity**2)**0.5) > 1.5): #a
            if (abs((self.x_velocity**2 + self.y_velocity**2)**0.5 <= 5)):
                self.body_orientation += 5
            elif ( abs(self.x_velocity**2 + self.y_velocity**2)**0.5 <= 20 and abs(self.x_velocity**2 + self.y_velocity**2)**0.5 > 5):                
                self.body_orientation += 5
                    
        if (self.command[2] == 1 and ((self.x_velocity**2 + self.y_velocity**2)**0.5) > 1.5): #a
            if (abs((self.x_velocity**2 + self.y_velocity**2)**0.5 <= 5)):
                self.body_orientation -= 5
            elif ( abs(self.x_velocity**2 + self.y_velocity**2)**0.5 <= 20 and abs(self.x_velocity**2 + self.y_velocity**2)**0.5 > 5):                
                self.body_orientation -= 5
                
        if(self.body_orientation >= 360):
            self.body_orientation = 0
        if(self.body_orientation < 0):
            self.body_orientation += 360
            
           
       
           
    
    def accelleration(self, time):
        
        velocity = MAX_VELOCITY*time/40
        if (velocity > MAX_VELOCITY):
            velocity = MAX_VELOCITY
        return velocity
    

    def rot_center(self, image, angle, x, y):
        #rotated_image = pygame.transform.rotate(self.image_ori, self.body_orientation)

        center_x = self.rect.centerx
        center_y = self.rect.centery

        self.image = pygame.transform.rotate(self.image_ori, self.body_orientation)
       # new_rect = rotated_image.get_rect(center = self.image.get_rect(center = (center_x, center_y)).center)    
       # self.image = rotated_image
       # self.rect = new_rect
        self.rect = self.image.get_rect(center=self.rect.center) 
        
    def draw_sensors(self):
        if (self.body_orientation <= 90 and self.body_orientation >= 0):
            self.left_sensor = [self.rect.x + self.w_ori*(math.cos(np.radians(self.body_orientation))), self.rect.y]
            self.right_sensor = [self.rect.x + self.image.get_width(), self.rect.y + self.h_ori*math.cos(np.radians(self.body_orientation))]
        elif(self.body_orientation < 360 and self.body_orientation >= 270):
            self.left_sensor = [self.rect.x + self.image.get_width(), self.rect.y + self.w_ori*(-1)*math.sin(np.radians(self.body_orientation))]
            self.right_sensor = [self.rect.x + self.w_ori*math.cos(np.radians(self.body_orientation)), self.rect.y + self.image.get_height()]
        elif(self.body_orientation >= 180 and self.body_orientation < 270):
            self.left_sensor = [self.rect.x + self.h_ori*(-1)*math.sin(np.radians(self.body_orientation)), self.rect.y + self.image.get_height()]
            self.right_sensor = [self.rect.x , self.rect.y + self.w_ori*(-1)*math.sin(np.radians(self.body_orientation))]
        elif(self.body_orientation > 90 and self.body_orientation < 180):
            self.left_sensor = [self.rect.x, self.rect.y + self.h_ori*(-1)*math.cos(np.radians(self.body_orientation))]
            self.right_sensor = [self.rect.x + self.h_ori*math.sin(np.radians(self.body_orientation)) ,self.rect.y]

        
        self.know = [self.rect.x, self.rect.y]
        self.know2 = [self.rect.x + self.image.get_width(), self.rect.y + self.image.get_height()]
        self.know3 = [self.rect.x + self.image.get_width(), self.rect.y]
        self.know4 = [self.rect.x, self.rect.y + self.image.get_height()]
       # pygame.draw.circle(SCREEN, FUCSIA, self.left_sensor, 5)
        #pygame.draw.circle(SCREEN, FUCSIA, self.right_sensor, 5)
        
        #pygame.draw.line(SCREEN, GREEN, self.left_sensor, (500,300))

       
    
    def radar(self, radar_angle):
        length = 10
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])
       # print(x,y)
        while not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and length < 250:
            #print(x,y)
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.body_orientation + radar_angle)) * length)
            if x < 50:
                x = 50
            y = int(self.rect.center[1] - math.sin(math.radians(self.body_orientation + radar_angle)) * length)
            if y < 5:
                y = 5
            if y > SCREEN_HEIGHT-5:
                y = SCREEN_HEIGHT-5
        # Draw Radar
        pygame.draw.line(SCREEN, (255, 255, 255, 255), self.rect.center, (x, y), 1)
        #pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 1)

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                             + math.pow(self.rect.center[1] - y, 2)))

        self.radars.append([radar_angle, dist])
        #print(dist)
        
        
    
    def detect_collision(self):
        x_l = int(self.left_sensor[0])
        y_l = int(self.left_sensor[1])
        x_r = int(self.right_sensor[0])
        y_r = int(self.right_sensor[1])
       # print(x_r,x_l)
        if (x_l < 50 or x_l < 50 or y_l < 10 or y_r < 10 or y_l > (SCREEN_HEIGHT - 15) or y_r > (SCREEN_HEIGHT - 15) or SCREEN.get_at((x_l, y_l)) == pygame.Color(2, 105, 31, 255)  or SCREEN.get_at((x_r, y_r)) == pygame.Color(2, 105, 31, 255) or ((self.rect.centerx > traf_l_pos - 55 ))) :
            #print((self.left_sensor[0], self.left_sensor[1]))  
            if (x_l < 50 or x_l < 50 or y_l < 10 or y_r < 10 or y_l > (SCREEN_HEIGHT - 15) or y_r > (SCREEN_HEIGHT - 15)):
                print("BOUNDARIES")
            elif(SCREEN.get_at((x_l, y_l)) == pygame.Color(2, 105, 31, 255)  or SCREEN.get_at((x_r, y_r)) == pygame.Color(2, 105, 31, 255)):
                print("COLLISION")
            
                
            return True
        
        if(self.x_velocity == 0 and self.y_velocity == 0 and (traf_l_pos - self.rect.centerx) > 200):  
            self.still += 1
        else:
            self.still = 0
        if self.still >= 30 and self.rect.centerx < 200:
            # print("Too slow")
            return True
        if self.still >= 100 and self.rect.centerx >= 200:
            return True
            #print("ahieie")
        return False
    
    # def detect_finishline(self):
    #     if(self.left_sensor[0] <= 485 and self.left_sensor[0] >= 470 and self.left_sensor[1] >= 600 and self.left_sensor[1] < 900):
    #         return True
    #     else:
    #         return False
    
    def update(self):
        
        self.draw_sensors()
        self.input_analisys()
        self.move()
        #self.crashed = self.detect_collision()
       # self.finish_line = self.detect_finishline()
        self.radars.clear()
        angles = [-60, -30, 0, 30, 60]
        for i in range(len(angles)):
            self.radar(angles[i])
        
       
    def draw(self, SCREEN):
        # pygame.Surface.set_colorkey(self.rect,(255,255,255))
       SCREEN.blit(self.image, (self.rect.x, self.rect.y))
     
       
       
    def data(self):
        input = [0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        if ((traf_l_pos - self.left_sensor[0]) < 200) and ((traf_l_pos - self.left_sensor[0]) > 0):
            input[5] = 1
        else:
            input[5] = 0
        if input[5] == 1:
            pass
            #pygame.draw.circle(SCREEN, (0, 0, 0, 0), (self.rect.centerx, 50), 3)
        if input[5] == 0:
            pass
            #pygame.draw.circle(SCREEN, (0, 255, 255, 0), (self.rect.centerx, 50), 3)
        return input 
       
       
        
def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)



def eval_genomes(genomes, config):
    clock = pygame.time.Clock()
   # clock = pygame.time.Clock()
    fit = 1
    global cars, ge, nets, shifts
    
    shifts = 0
    
    global traf_l_pos 
    traf_l_pos = 2000

    cars = []
    ge = []
    nets = []
    trak = road.Road()
    SCREEN.fill((170,170,170))
    
    check = 0
    next_lane = False
    for i in range(12):
        trak.addpoint()
        
    trak.points[5] = (trak.points[5][0], trak.points[5][1], 1 )    
    
    # LOADING SAVED GENOME!
    # file = open("winner.p",'rb')   
    # winner_genome = pickle.load(file)
    # file.close()
   
    
    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        
    # LOADING SAVED GENOME   
    # cars.append(pygame.sprite.GroupSingle(Car())) 
    # ge.append(winner_genome[1])
    # net = neat.nn.FeedForwardNetwork.create(winner_genome[1], config)
    # nets.append(net)
    # winner_genome[1].fitness = 0
    
    def score():
        global shifts
        text = FONT.render(f'Driven sections:  {str(shifts)}', True, (0, 0, 0))
        SCREEN.blit(text, (50, 620))
    
    def statistics():
        global cars, ge
        text_1 = FONT.render(f'Cars Alive:  {str(len(cars))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        #text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

        SCREEN.blit(text_1, (50, 640))
        SCREEN.blit(text_2, (50, 660))
        #SCREEN.blit(text_3, (50, 510))
    
    
    
    
    time = 0  
   # command = [0,0,0,0]
    run = True
   # command = [0,0,0,0]
    countdown = False
    redlight_time = 0
    while True:
        time += 1
        #print(mycar.x_velocity)
        SCREEN.fill((100,100,100))
        #print(traf_l_pos)
        if countdown:
            redlight_time += 1
        if redlight_time > 500:
            countdown = False
            redlight_time = 0
            for i in range(10):
                if trak.points[i][2] == 1:
                   #trak.points[i][2] = 2
                   trak.change_traf(i)
                   print("GREEN LIGHT BITCH!")
                   break
               
        for i in range(10): # INGLOBA IN QUELLO SOTTO
            #print(trak.points[i][2])
            if trak.points[i][2] == 1:
                traf_l_pos = trak.points[i][0]
                countdown = True
                break
            else:
                traf_l_pos = 2000
            
        
        
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            
               
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_w:
            #         mycar.command[0] = 1               
            #     if event.key == pygame.K_a:
            #         mycar.command[1] = 1
            #     if event.key == pygame.K_d:
            #         mycar.command[2] = 1
            #     if event.key == pygame.K_s:
            #         mycar.command[3] = 1
                
                
                    
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_w:
            #         mycar.command[0] = 0
            #     if event.key == pygame.K_a:
            #         mycar.command[1] = 0
            #     if event.key == pygame.K_d:
            #         mycar.command[2] = 0 
            #     if event.key == pygame.K_s:
            #         mycar.command[3] = 0
       
        if len(cars) == 1:
            #print(ge[0].fitness)
            with open("Winner.p", "wb") as f:
                pickle.dump(genomes[0], f)
                f.close()
            
        if len(cars) == 0:
            SCORES.append(shifts)
            #print("fin")
            print(SCORES)
            break
        
        for i, car in enumerate(cars):
            
            if ((traf_l_pos - car.sprite.rect.centerx) < 200 and ((traf_l_pos - car.sprite.rect.centerx) > 0)):
                # if car.sprite.x_velocity > 1:
                #     ge[i].fitness -= fit
                # else:
                #     ge[i].fitness += fit*3
                ge[i].fitness -= fit*car.sprite.x_velocity*0.1
                if car.sprite.x_velocity <= 1:
                    #pygame.draw.circle(SCREEN, (255,80,100,100), (car.sprite.rect.centerx, 690), 2)
                    ge[i].fitness += fit
            elif car.sprite.x_velocity > 1:
                ge[i].fitness += fit
               # pygame.draw.circle(SCREEN, (255,0,255,255), (car.sprite.rect.centerx, 650), 2)
           
            if car.sprite.crashed:
                #ge[i].fitness -= 0.5
               
                remove(i)
            # if car.sprite.finish_line:
            #     if(fit == 1):
            #         ge[i].fitness += 5
            #         print("LAP TIME:", time)
            #         fit = 0
            #     remove(i)
            
            
            if car.sprite.rect.x >= 1100:               
                car.sprite.finish_portion = True
                # car.sprite.shift()
                # trak.shift()
                # car.sprite.crashed = False
                
        for i, car in enumerate(cars):
           output = nets[i].activate(car.sprite.data())
           if output[0] > 0.7:
               car.sprite.command[0] = 1
               car.sprite.command[3] = 0
           if output[1] > 0.7:
               car.sprite.command[1] = 1
               car.sprite.command[2] = 0
           if output[0] <= 0.7:
               car.sprite.command[3] = 1
               car.sprite.command[0] = 0
           if output[1] <= 0.4:
               car.sprite.command[2] = 1
               car.sprite.command[1] = 0
           if output[1] > 0.4 and output[1] <= 0.7:
               car.sprite.command[2] = 0
               car.sprite.command[1] = 0
        
        check = 0
        for i, car in enumerate(cars):
            if car.sprite.finish_portion == True:
                check += 1
            else:
                break
            if check == len(cars):
                next_lane = True
                check = 0
        
        if next_lane == True:
            next_lane = False
            #print("ole")
            trak.shift()
            for i, car in enumerate(cars):
                car.sprite.shift()
                car.sprite.crashed = False
                car.sprite.finish_portion = False
            shifts += 1
            
        for i in range(len(trak.points)):
            trak.draw(i)
        
        for car in cars:
            car.sprite.rot_center(car.sprite.image_ori, car.sprite.body_orientation, car.sprite.rect.centerx, car.sprite.rect.centery)
            car.draw(SCREEN)            
            car.update()
            
        
            
        clock.tick(SPEED)
        statistics()
        score()
        pygame.display.update()
        
        for car in cars:
            car.sprite.crashed = car.sprite.detect_collision()



def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    # pop.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # pop.add_reporter(stats)
    print("test")
    pop.run(eval_genomes)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)


        