import os

from .utils import read_json, load_imgs

ANIMATION_PATH = 'data/images/entities/'
CONFIG_FILE = 'config.json'

class Animation:
    def __init__(self, images, anim_config):
        self.images = images
        self.config = anim_config
        self.img_duration = self.config['img_duration']
        self.loop = self.config['loop']
        
        self.done = False
        self.frame = 0
    
    @property  
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
    def copy(self):
        return Animation(self.images, self.config)
    
    def update(self, dt):
        if self.loop:
            self.frame = (self.frame + dt) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + dt, (len(self.images) - 1) * self.img_duration)
            if self.frame >= ((len(self.images) - 1) * self.img_duration):
                self.done = True


class Animations:
    def __init__(self):
        self.animations = {}
                
        for entity_id in os.listdir(ANIMATION_PATH):
            config = read_json(ANIMATION_PATH + entity_id + '/' + CONFIG_FILE)
            for anim in os.listdir(ANIMATION_PATH + entity_id):
                full_path = ANIMATION_PATH + entity_id + '/' + anim
                if os.path.isdir(full_path):
                    self.animations[entity_id + '/' + anim] = Animation(load_imgs(f'entities/{entity_id}/{anim}'), anim_config=config[anim])    
                            
    def new(self, anim_id):
        return self.animations[anim_id].copy()                