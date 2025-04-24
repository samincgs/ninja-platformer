import pygame

class Entity:
    def __init__(self, game, pos, size, e_type):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.type = e_type
        
        self.animation = None
        self.action = ''
        
        self.flip = [False, False]
        
    @property
    def img(self):
        if self.animation:
            img = self.animation.img
        if any(self.flip):
            img = pygame.transform.flip(img, self.flip[0], self.flip[1])
        return img
    
    @property 
    def center(self):
        return self.rect.center
    
    @property
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.animations[self.type + '/' + self.action].copy()
    
    def update(self, dt):
        if self.animation:
            self.animation.update(dt)
    
    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class PhysicsEntity(Entity):
    def __init__(self, game, pos, size, e_type):
        super().__init__(game, pos, size, e_type)
        self.frame_movement = [0, 0]
        self.velocity = [0, 0]
        self.acceleration = [0, 0]
        self.terminal_velocity = [250, 700]
        self.velocity_reset = [False, True]
        
        
        self.collision_directions = { 'up': False, 'down': False, 'right': False, 'left': False}
        
    def update(self, dt):
        super().update(dt)
        
        self.frame_movement[0] += self.velocity[0] * dt
        self.frame_movement[1] += self.velocity[1] * dt
                
        self.physics_movement(self.game.tilemap, movement=self.frame_movement)
        
        self.velocity[0] = min(self.velocity[0] + self.acceleration[0] * dt, self.terminal_velocity[0])
        self.velocity[1] = min(self.velocity[1] + self.acceleration[1] * dt, self.terminal_velocity[1])
        
        self.frame_movement = [0, 0]
          
    def move(self, movement, dt):
        self.frame_movement[0] += movement[0] * dt
        self.frame_movement[1] += movement[1] * dt
    
    def physics_movement(self, tilemap, movement=(0, 0)):
        self.collision_directions = { 'up': False, 'down': False, 'right': False, 'left': False}
        
        self.pos[0] += movement[0]
        tile_rects = tilemap.get_nearby_rects(self.pos)
        collision_rects = tilemap.collision_test(self.rect, tile_rects)
        entity_rect = self.rect
        for rect in collision_rects:
            if entity_rect.colliderect(rect):
                if movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collision_directions['right'] = True
                if movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collision_directions['left'] = True
                if self.velocity_reset[0]:
                    self.velocity[0] = 0
                self.pos[0] = entity_rect.x
        
        self.pos[1] += movement[1]
        tile_rects = tilemap.get_nearby_rects(self.pos)
        collision_rects = tilemap.collision_test(self.rect, tile_rects)
        entity_rect = self.rect
        for rect in collision_rects:
            if entity_rect.colliderect(rect):
                if movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collision_directions['down'] = True
                if movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collision_directions['up'] = True
                if self.velocity_reset[1]:
                    self.velocity[1] = 0
                self.pos[1] = entity_rect.y
        
            