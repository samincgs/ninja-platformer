import pygame

class Entity:
    def __init__(self, game, pos, size, e_type):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.type = e_type
    
    @property
    def img(self):
        return self.game.assets[self.type]
    
    @property 
    def center(self):
        return self.rect.center
    
    @property
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def update(self, dt):
        pass
    
    def render(self, surf):
        surf.blit(self.img, self.pos)


class PhysicsEntity(Entity):
    def __init__(self, game, pos, size, e_type):
        super().__init__(game, pos, size, e_type)
        self.frame_movement = [0, 0]
        self.velocity = [0, 0]
        self.acceleration = [0, 350]
        self.terminal_velocity = [0, 700]
        self.speed = 80
        
        self.collision_directions = { 'up': False, 'down': False, 'right': False, 'left': False}
        
    def update(self, dt):
        super().update(dt)
        
        self.frame_movement[0] += self.velocity[0] * dt
        self.frame_movement[1] += self.velocity[1] * dt
        
        self.apply_force(((self.game.movement[1] - self.game.movement[0]) * self.speed, 0), dt)
        self.physics_movement(self.game.tilemap, movement=self.frame_movement)
        
        # print(self.frame_movement)
        self.velocity[0] += self.acceleration[0] * dt
        self.velocity[1] = min(self.velocity[1] + self.acceleration[1] * dt, self.terminal_velocity[1])
        
        if self.collision_directions['down'] or self.collision_directions['up']:
            self.velocity[1] = 0
        
        self.frame_movement = [0, 0]
        
        
        
    def apply_force(self, vec, dt):
        self.frame_movement[0] += vec[0] * dt
        self.frame_movement[1] += vec[1] * dt
    
    def physics_movement(self, tilemap, movement=(0, 0)):
        self.collision_directions = { 'up': False, 'down': False, 'right': False, 'left': False}
        
        print(movement)
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
                self.pos[1] = entity_rect.y
        
            