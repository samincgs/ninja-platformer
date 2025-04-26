import os

from .utils import load_json, save_json, load_imgs

COLORKEY = (0, 0, 0)
ANIMATION_PATH = 'data/images/entities/'
CONFIG_FILE = 'config.json'

class Animation:
    def __init__(self, anim_state, images, anim_config):
        self.anim_state = anim_state
        self.images = images
        self.config = anim_config
        self.img_duration = self.config[anim_state]['img_duration']
        self.loop = self.config[anim_state]['loop']
        
        self.done = False
        self.frame = 0
    
    @property  
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
    def copy(self):
        return Animation(self.anim_state, self.images, self.config)
    
    def update(self, dt):
        if self.loop:
            self.frame = (self.frame + dt) % (self.img_duration * len(self.images))
        else:
            self.frame += dt
            self.frame = min(self.frame, (len(self.images) - 1) * self.img_duration)
            if self.frame >= ((len(self.images) - 1) * self.img_duration):
                self.done = True


class Animations:
    def __init__(self):
        self.animations = {}
        self.generate_anims(ANIMATION_PATH)
     
    def generate_anims(self, path):
        for entity_id in os.listdir(path):
            change_config = False
            try:
                config = load_json(path + entity_id + '/' + CONFIG_FILE)
            except FileNotFoundError:
                change_config = True
                config = {}
                
            for anim in os.listdir(path + entity_id):
                full_path = path + entity_id + '/' + anim
                if os.path.isdir(full_path):
                    if not config or anim not in config:
                        config[anim] = {'img_duration': 0.1, 'loop': False}
                    self.animations[entity_id + '/' + anim] = Animation(anim_state=anim, images=load_imgs(f'entities/{entity_id}/{anim}', colorkey=COLORKEY), anim_config=config)
            
            if change_config:
                save_json(path=path + entity_id + '/' + CONFIG_FILE, data=config)
        
    def new(self, anim_id):
        return self.animations[anim_id].copy()                