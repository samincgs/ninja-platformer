from .entities import PhysicsEntity


class Player(PhysicsEntity):
    def __init__(self, game, pos, size, e_type):
        super().__init__(game, pos, size, e_type)
        self.speed = 80
        self.acceleration[1] = 450
        self.anim_offset = (-3, -3)
        
        
        self.set_action('idle')
        
    def update(self, dt):
        super().update(dt)
        
        self.move(((self.game.movement[1] - self.game.movement[0]) * self.speed, 0), dt)
        
        if self.frame_movement[0] > 0:
            self.flip[0] = False
        if self.frame_movement[0] < 0:
            self.flip[0] = True
            

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))