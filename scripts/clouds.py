import random

class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth
        
    def update(self, dt):
        self.pos[0] += self.speed * dt
        
    def render(self, surf, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % surf.get_width(), render_pos[1] % surf.get_height())) # add fluffys way if not work
        
        
class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []
         
        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images), random.random() + 5, random.random() * 0.6 + 0.2))
            
        self.clouds.sort(key=lambda x: x.depth)
        
    def update(self, dt):
        for cloud in self.clouds:
            cloud.update(dt)
            
    def render(self, surf, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)
             
        