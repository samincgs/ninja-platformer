import pygame

from .entities import PhysicsEntity


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'player')
        self.speed = 80
        self.acceleration[1] = 450
        self.air_time = 0
        
        self.anim_offset = (-3, -3)
        
        self.set_action('idle')
        
    def update(self, dt):
        super().update(dt)
        
        self.air_time += dt
        
        self.move(((self.game.input[1] - self.game.input[0]) * self.speed, 0), dt)
        
        if self.frame_movement[0] > 0:
            self.flip[0] = False
        if self.frame_movement[0] < 0:
            self.flip[0] = True
        
        if self.air_time >= 0.1:
            self.set_action('jump')
        elif self.frame_movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        
        if self.collision_directions['down']:
            self.air_time = 0
        
        self.physics_update(dt)
            

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        # debug
        # pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(self.pos[0] - offset[0], self.pos[1] - offset[1], *self.size))