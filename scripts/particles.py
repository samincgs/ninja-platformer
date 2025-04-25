from .utils import palette_swap

class Particle:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0, decay_rate=20, custom_color=None):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.frame = frame
        self.decay_rate = decay_rate
        self.custom_color = custom_color
        
        self.images = self.game.assets['particles/' + p_type]
        
    def update(self, dt):
        kill = False
        
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt
        
        self.frame += self.decay_rate * dt
        self.frame = min(self.frame, len(self.images) - 1)
        if self.frame >= len(self.images) - 1:
            kill = True
            
            
        return kill
    
    
    def render(self, surf, offset=(0, 0)):
        img = self.images[int(self.frame)]
        if self.custom_color:
            if self.type == 'particle':
                old_color = (255, 255, 255)
            else:
                old_color = (0, 0, 0)
            img = palette_swap(img, old_color, self.custom_color)
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() / 2, self.pos[1] - offset[1] - img.get_width() / 2))
        