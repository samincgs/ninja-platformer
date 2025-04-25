import pygame

from .entities import PhysicsEntity


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'player')
        self.speed = 80
        self.acceleration[1] = 450
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.velocity_normalization[0] = 600
        
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
            
        elif self.jumps:
            self.velocity[1] = -180
            self.jumps -= 1
            self.air_time = 0.1
        
    def update(self, dt):
        super().update(dt)
        
        self.air_time += dt
        self.wall_slide = False
        if (self.collision_directions['right'] or self.collision_directions['left']) and self.air_time >= 0.1:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 30)
            if self.collision_directions['right']:
                self.flip[0] = False
            else:
                self.flip[0] = True
            self.set_action('wall_slide')
        
        self.move(((self.game.input['right'] - self.game.input['left']) * self.speed, 0), dt)
        if self.game.input['jump']:
            self.jump()
        
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
            
        if self.collision_directions['down']:
            self.air_time = 0
            self.jumps = 1
        
        self.physics_update(dt)
            

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        # debug
        # pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(self.pos[0] - offset[0], self.pos[1] - offset[1], *self.size))