import pygame
import math
import random

from .entities import PhysicsEntity
from .particles import Particle


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'player')
        self.speed = 80
        self.acceleration[1] = 450
        self.velocity_normalization[0] = 600
        self.velocity_reset[1] = True
        
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        
        self.anim_offset = (-3, -3)
        
        self.set_action('idle')
    
    def jump(self):
        if self.wall_slide:
            if self.flip[0] and self.last_movement[0] < 0:
                self.velocity[0] = 180
            elif not self.flip[0] and self.last_movement[0] > 0:
                self.velocity[0] = -180
            self.velocity[1] = -150
            self.air_time = 0.1
            self.jumps = max(self.jumps - 1, 0)
            self.game.sfx['jump'].play()
            
        elif self.jumps and self.air_time <= 0.1:
            self.velocity[1] = -200
            self.jumps -= 1
            self.air_time = 0.1
            self.game.sfx['jump'].play()
    
    def dash(self):
        if not self.dashing:
            if self.flip[0]:
                self.dashing = -60
            else:
                self.dashing = 60
            self.game.sfx['dash'].play()
            
        
    def update(self, dt):
        super().update(dt)
        
        self.air_time += dt 
        
        if self.air_time > 2:
            self.game.dead += dt
            self.game.screenshake = max(0.4, self.game.screenshake)
            self.air_time = 0

        self.move(((self.game.input['right'] - self.game.input['left']) * self.speed, 0), dt)
                
        if int(abs(self.dashing)) in {50, 60}:
            for i in range(12):
                angle = random.random() * math.pi * 2
                speed = random.random() * 40 + 20
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect.center, pvelocity, random.randint(0, 2), decay_rate=5, custom_color=(20, 16, 42)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - dt * 60)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + dt * 60)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 480
            if int(abs(self.dashing)) == 50: #FIX
                self.velocity[0] *= 0.1 
            for i in range(6):
                pvelocity = [abs(self.dashing) / self.dashing * random.random() * 30, 0]
                self.game.particles.append(Particle(self.game, 'particle', self.rect.center, pvelocity, decay_rate=5, custom_color=(20, 16, 32), frame=random.randint(1, 3)))
        
        if self.game.input['jump']:
            self.jump()
        if self.game.input['dash']:
            self.dash()
        
        if self.frame_movement[0] > 0:
            self.flip[0] = False
        if self.frame_movement[0] < 0:
            self.flip[0] = True
        
        
        if not self.wall_slide:
            if self.air_time >= 0.1:
                self.set_action('jump')
            elif self.frame_movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        self.wall_slide = False  
        wall_left = (self.rect.left - 1, self.rect.centery)
        wall_right = (self.rect.right + 1, self.rect.centery)
        if self.game.tilemap.solid_check(wall_left if self.flip[0] else wall_right) and self.air_time >= 0.1:
            self.wall_slide = True
            self.air_time = 0.1
            self.velocity[1] = min(self.velocity[1], 30)
            self.set_action('wall_slide')
        

        if self.collision_directions['down']:
            self.air_time = 0
            self.jumps = 1

        self.physics_update(dt)

    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            surf.blit(self.img, (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        
            
            
        # debug
        # pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(self.pos[0] - offset[0], self.pos[1] - offset[1], *self.size))