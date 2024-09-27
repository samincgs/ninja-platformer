import pygame
import math
import random

from scripts.particle import Particle

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -2) # since the animation is bigger than our usual player img, we add a padding
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
        
    
    def rect(self):
        return pygame.Rect(*self.pos, *self.size)
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            
        
    def update(self, tilemap, movement=(0, 0)):
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        # physics
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect() # get the current rect position
        for rect in tilemap.physics_rects_around(self.pos): # check if the position collides with any of the collideable rects
            if entity_rect.colliderect(rect): # see if player collides
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
                
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement
         
        self.velocity[1] = min(self.velocity[1] + 0.1, 5) # adds velocity so player moves faster and faster down, terminal velocity when it reaches 5
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
    
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img, self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])) 
        # surf.blit(self.game.assets['player'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 2 
        self.wall_slide = False
        self.dashing = 0
    
    def jump(self):
        # prioritize certain animations
        # wall slide functionality
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0: # if the player is facing left and the last moveemnt was also heading left
                self.velocity[0] = 2
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -2
                self.velocity[1] = -2.5
                self.air_time = 5
                return True
        
        # jump functionality
        elif self.jumps: # if the player jumps
            self.velocity[1] = -2.5 # an an upward velocity
            self.jumps -= 1 # reduce their jump number
            self.air_time = 5 # immediately puts it into the jump animation
            return True
    
    
    def dash(self):
        if not self.dashing: # wyhen the player is not dashing
            # set the vector for direction and magnitude
            if self.flip: # facing the left
                self.dashing = -60
            else: # facing the right
                self.dashing = 60
    
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50: # when dash is on cooldown
            super().render(surf, offset=offset)
        else:
            pass
        
    def update(self, tilemap, movement=(0,0)):
        
        super().update(tilemap, movement=movement)
        
        self.air_time += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2
        
        self.wall_slide = False # make it so its a single frame which
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4: # if we hit the wall on either side and are in the air
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5) # capping the downward velocity at 0.5
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
            

        if not self.wall_slide:        
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
                
        # normalize the x axis if the user wall jumps to the left/right (pull number linearly back to 0)
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0) # negative values
                
        # dashing movement
        # a dash that only does a circular burst of particles at the beginning (60) and end(50) of the dash
        if abs(self.dashing) in {60, 50}: # if we are at the start or the end of the dash (use set since its more performant)
            for i in range(20):
                angle = random.random() * math.pi * 2 # random angle from a circle (full circle of angles in radians)
                speed = random.random() * 0.5 + 0.5 # random speed between 0.5 and 1
                # cosine for the x axis and sine for the y axis (generating a velocity based on the  angle) 
                # this is how you move something in a direction in 2D 
                # for the x axis you take the cosine of the angle you want to move and multiply by the amount you want to move
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed] 
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(self.dashing - 1, 0)   
        if self.dashing < 0:
            self.dashing = min(self.dashing + 1, 0)        
        
        # A dash that does a stream of particles as it moves towards a direction 
        if abs(self.dashing) > 50: # if the dash is in its first ten frames 
            # (0 - 50) acts as a cooldown so the player cannot spam the dash
            self.velocity[0] = abs(self.dashing) / self.dashing * 8 # will give us 1 or -1 depending on if we are dashing to the left or right
            if abs(self.dashing) == 51: # 1 frame 
                self.velocity[0] *= 0.1 # cause a sudden stop to the dash by severely cutting down on the velocity which is further normalized to 0 by if statements
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0] # use self.dashing so it moves along with the magnitude of the velocity 
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))