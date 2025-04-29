import pygame
import math


class Spark:
    def __init__(self, pos, angle, speed, decay_rate):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.decay_rate = decay_rate * speed
        
    def update(self, dt):
        self.speed -= self.decay_rate * dt
        if self.speed <= 0:
            return True
        
        
        self.pos[0] += math.cos(self.angle) * self.speed * dt
        self.pos[1] += math.sin(self.angle) * self.speed * dt
        
    def render(self, surf, offset=(0, 0)):
        points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 0.05 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 0.05 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.01 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.01 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 0.05 - offset[0], self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 0.05 - offset[1]),
            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.01 - offset[0], self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.01 - offset[1]),
        ]
        
        pygame.draw.polygon(surf, (255, 255 , 255), points=points)