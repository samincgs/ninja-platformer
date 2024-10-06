import pygame
import math
import random

from scripts.particle import Particle
from scripts.projectile import Projectile
from scripts.spark import Spark

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
        self.jumps = 1
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
        
        # when player dies
        if self.air_time > 120:
            self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            
        self.wall_slide = False # make it so its a single frame which
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4: # if we hit the wall on either side and are in the air
            self.air_time = 30 # set air time to 30 so player is not considered dead when in the air for too long
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
                # cosine for the x axis and sine for the y axis (generating a velocity based on the angle) 
                # this is how you move something in a direction in 2D 
                # for the x axis you take the cosine of the angle you want to move and multiply by the amount you want to move
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed] # polar coordinates to cartesian coordinates
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
                       
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 0
        
    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-4 if self.flip else 4), self.pos[1] + 23)): # check seven tiles in front of the enemy to see if theres a tile
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking: # gives us 1 frame right before it goes to else statement
                # calculate the distance between the enemy and the player (vector pointing from the enemy to the player)
                # destination - current_location (or) target - origin
                # since we want a projectile to the player from the enemy we do player.pos - enemy.pos
                # we do destination - current_loc when we want a vector with magnitude and direction
                # we do a pythagorean theorem of dis_x + dis_y to get the scalar distance between two points
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16): # checks the vertical distance to make sure that the player is in the same vertical space as the enemy
                    if (self.flip and dis[0] < 0): # enemy is facing left and player is to the left 
                        self.game.projectiles.append(Projectile(self.game, pos=[self.rect().centerx - 7, self.rect().centery], speed=-1.5, timer=0)) #[[self.rect().centerx - 7, self.rect().centery], -1.5, 0]
                        for i in range(6):
                            self.game.sparks.append(Spark(self.game.projectiles[-1].pos, random.random() - 0.5 + math.pi, 2 + random.random()))
                    elif (not self.flip and dis[0] > 0): # enemy is facing right and player is to the right
                        self.game.projectiles.append(Projectile(self.game, [self.rect().centerx + 7, self.rect().centery], speed=1.5, timer=0)) # [[self.rect().centerx + 7, self.rect().centery], 1.5, 0]
                        for i in range(6):
                            self.game.sparks.append(Spark(self.game.projectiles[-1].pos, random.random() - 0.5, 2 + random.random()))
                
        elif random.random() < 0.01: # happens ever 1.67 seconds for 60fps 
            self.walking = random.randint(30, 120) # number of frames the enem will walk (between half a second and 2 seconds)
            
        super().update(tilemap, movement=movement)
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        
        # check if the dash animation of the player collides with the enemy    
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(32, self.game.screenshake)
                for i in range(40):
                    angle = random.random() * math.pi * 2 # random angle in a full circle
                    speed = random.random() * 5
                    velocity = [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5] # add math.pi so particles spawn in the opposite direction of the sparks
                    self.game.sparks.append(Spark(self.rect().center, angle=angle, speed= 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=velocity,frame=random.randint(0, 7) ))
                # add extra bigger sparks that go left and right
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
                   
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        # add the gun
        if self.flip:
            # subtracting the width renders it from the persepective of the top right of the gun img when its pointing left
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False),(self.rect().centerx - 3 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 3 - offset[0], self.rect().centery - offset[1]))