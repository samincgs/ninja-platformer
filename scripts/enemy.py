import random

from .entities import PhysicsEntity

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size, 'enemy')
        self.speed = 40
        self.acceleration[1] = 450
        self.velocity_normalization[0] = 600
        self.walking = 0
        
        self.set_action('idle')
        
    def update(self, dt):
        super().update(dt)
        
        if self.walking:
            if self.game.tilemap.solid_check((self.rect.centerx + (-7 if self.flip[0] else 7), self.pos[1] + 23)):
                self.move(((-1 if self.flip[0] else 1) * self.speed, 0), dt)
            else:
                self.flip[0] = not self.flip[0]
                
            self.walking = max(0, self.walking - dt)
        elif random.random() < 0.01:
            self.walking = random.random() * 1.5 + 0.5
            
        
        self.physics_update(dt)