# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 16:43:31 2022

@author: filon
"""

import pygame
import neat
import os
import random

pygame.font.init()

win_h = 800
win_w = 500
draw_lines = True
gen = 0

pygame.display.set_caption("Flappy Bird")

# Set up sprites
bird_imgs = [pygame.transform.scale2x(pygame.image.load('images\\bird1.png')),
             pygame.transform.scale2x(pygame.image.load('images\\bird2.png')),
             pygame.transform.scale2x(pygame.image.load('images\\bird3.png'))]
base_img = pygame.transform.scale2x(pygame.image.load('images\\base.png'))
bg_img = pygame.transform.scale2x(pygame.image.load('images\\bg.png'))
pipe_img = pygame.transform.scale2x(pygame.image.load('images\\pipe.png'))

# declaring font
stat_font = pygame.font.SysFont('comicsans', 50)

class Bird:
    rotate_vel = 20
    max_rotate = 25
    animate_time = 5
    imgs = bird_imgs
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.h = self.y
        self.frames = 0
        self.tilt = 0
        self.vel = 0
        self.img_num = 0
        self.img = self.imgs[0]
    
    def jump(self):
        self.vel = -10.5
        self.frames = 0
        self.h = self.y
    
    def move(self):
        self.frames += 1
        d = self.vel * self.frames + 1.5 * self.frames**2
        if d >= 16:
            d = 16
        
        self.y = self.y + d
        
        if d < 0 or self.y < self.h + 50:
            if self.tilt < self.max_rotate:
                self.tilt = self.max_rotate
        else:
            if self.tilt > -90:
                self.tilt -= self.rotate_vel
                
    def draw(self, win):
        self.img_num += 1
        if self.img_num < self.animate_time:
            self.img = self.imgs[0]
        elif self.img_num < self.animate_time * 2:
            self.img = self.imgs[1]
        elif self.img_num < self.animate_time * 3:
            self.img = self.imgs[2]
        elif self.img_num < self.animate_time * 4:
            self.img = self.imgs[1]
        elif self.img_num < self.animate_time * 4 + 1:
            self.img = self.imgs[0]
            self.img_num = 0
        
        if self.tilt < -80:
            self.img = self.imgs[1]
            self.img_num = self.animate_time * 2
        
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft =  (self.x, self.y)).center)
        win.blit(rotated_img, new_rect)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
class Pipe:
    gap = 200
    vel = 5
    
    def __init__(self, x):
        self.x = x
        self.h = 0
        self.top = 0
        self.bot = 0
        self.top_pipe = pygame.transform.flip(pipe_img, False, True)
        self.bot_pipe = pipe_img
        self.passed = False
        self.set_height()
        
    def set_height(self):
        self.h = random.randrange(50, 450)
        self.bot = self.h + self.gap
        self.top = self.h - self.top_pipe.get_height()
        
    def move(self):
        self.x -= self.vel
    
    def draw(self, win):
        win.blit(self.top_pipe, (self.x, self.top))
        win.blit(self.bot_pipe, (self.x, self.bot))
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.top_pipe)
        bot_pipe_mask = pygame.mask.from_surface(self.bot_pipe)
        
        top_off = (self.x - bird.x, self.top - round(bird.y))
        bot_off = (self.x - bird.x, self.bot - round(bird.y))
        
        top_over = bird_mask.overlap(top_pipe_mask, top_off)
        bot_over = bird_mask.overlap(bot_pipe_mask, bot_off)
        
        if top_over or bot_over:
            return True
        return False
    
class Base:
    vel = 5
    img = base_img
    w = base_img.get_width()
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.w
        
    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel
        
        if self.x1 < -self.w:
            self.x1 = self.x2 + self.w
        if self.x2 < -self.w:
            self.x2 = self.x1 + self.w
        
    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))
    
def draw_win(win, birds, pipes, base, score, gen, pipe_ind):
    global draw_lines
    win.blit(bg_img, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)
        
    base.draw(win)
    
    
    for bird in birds:
        if draw_lines:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].top_pipe.get_width() / 2, pipes[pipe_ind].h),
                                 5)
                pygame.draw.line(win, (255,0,0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].bot_pipe.get_width() / 2, pipes[pipe_ind].bot),
                                 5)
            except:
                pass
        bird.draw(win)
    
    text = stat_font.render('Score : ' + str(score), 1, (255,255,255))
    win.blit(text, (win_w - 10 - text.get_width(), 10))
    
    text = stat_font.render('Gen : ' + str(gen), 1, (255,255,255))
    win.blit(text, (10,10))
    
    text = stat_font.render('Alive : ' + str(len(birds)), 1, (255,255,255))
    win.blit(text, (10, 50))
    
    pygame.display.update()
    
def main(genomes, config):
    global gen
    gen += 1
    birds = []
    ge = []
    nn = []
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nn.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)
    
    pipes = [Pipe(500)]
    base_obj = Base(630)
    win = pygame.display.set_mode((win_w, win_h))
    clock = pygame.time.Clock()
    run = True
    score = 0
    
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].top_pipe.get_width():
                pipe_ind = 1
        else:
            break
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nn[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].h), abs(bird.y - pipes[pipe_ind].bot)))
            if output[0] > 0.5:
                bird.jump()
        
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird) or (bird.y + bird.img.get_height() >= 630 or bird.y < 0):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    ge.pop(x)
                    nn.pop(x)
                    
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    for g in ge:
                        g.fitness += 5
                    score += 1
                    pipes.append(Pipe(500))
            
            if pipe.x + pipe.top_pipe.get_width() < 0:
                pipes.remove(pipe)
            
            pipe.move()
        
        base_obj.move()
        draw_win(win, birds, pipes, base_obj, score, gen, pipe_ind)
        
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    popu = neat.Population(config)
    popu.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    popu.add_reporter(stats)
    
    winner = popu.run(main, 50)
    print('\nBest Genome: \n{!s}'.format(winner))
    
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
        
            
        