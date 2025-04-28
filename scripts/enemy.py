import math
import pygame
import random

from .particles import Particle
from .entities import PhysicsEntity
from .sparks import Spark

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'enemy')
        self.speed = 40
        self.acceleration[1] = 450
        self.velocity_normalization[0] = 600
        self.walking = 0
        
        self.anim_offset = (-3, -3)
        
        self.set_action('idle')
        
    def update(self, dt):
        kill = False
        
        super().update(dt)
        
        if self.walking:
            self.walking = max(0, self.walking - dt)
            
            if self.game.tilemap.solid_check((self.rect.centerx + (-7 if self.flip[0] else 7), self.pos[1] + 23)):
                if (self.collision_directions['right'] or self.collision_directions['left']):
                    self.flip[0] = not self.flip[0]
                self.move(((-0.8 if self.flip[0] else 0.8) * self.speed, 0), dt)
            else:
                self.flip[0] = not self.flip[0]
                
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1] < 16):
                    if (self.flip[0] and dis[0] < 0):
                        self.game.projectiles.append([[self.rect.centerx - 7, self.rect.centery], -90, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 120 + random.random() * 60, 4 + random.random()))
                    if (not self.flip[0] and dis[0] > 0):
                        self.game.projectiles.append([[self.rect.centerx + 7, self.rect.centery], 90, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 120 + random.random() * 60, 4 + random.random()))
        elif random.random() < 0.6 * dt:
            self.walking = random.random() * 1.5 + 0.5
        
        if self.frame_movement[0] > 0:
            self.flip[0] = False
        if self.frame_movement[0] < 0:
            self.flip[0] = True
        
        if self.frame_movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
            
        if abs(self.game.player.dashing) >= 50:
            if self.rect.colliderect(self.game.player.rect):
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect.center, angle, 180 + random.random() * 40, 4 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect.center, velocity=[math.cos(angle + math.pi) * speed * 30, math.sin(angle + math.pi) * speed * 30], custom_color=(20, 16, 42), decay_rate=10.5))
                self.game.sparks.append(Spark(self.rect.center, 0, 300 + random.random() * 60, 1.4))
                self.game.sparks.append(Spark(self.rect.center, math.pi, 300 + random.random() * 60, 1.4))
                kill = True
            
        
        self.physics_update(dt)
        
        return kill
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        
        gun_img = self.game.assets['gun']
        if self.flip[0]:
            surf.blit(pygame.transform.flip(gun_img, True, False), (self.rect.centerx - 2 - gun_img.get_width() - offset[0], self.rect.centery - offset[1])) # minus by gun width on x axis when rendering on flip
        else:
            surf.blit(gun_img, (self.rect.centerx + 2 - offset[0], self.rect.centery - offset[1]))