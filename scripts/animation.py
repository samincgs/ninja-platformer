import os

from .utils import load_json, save_json, load_imgs

COLORKEY = (0, 0, 0)
ANIMATION_PATH = 'data/images/entities/'
CONFIG_FILE = 'config.json'

class Animation:
    def __init__(self, anim_id, images, anim_config):
        self.id = anim_id[0]
        self.anim_type = anim_id[1]
        self.images = images
        self.config = anim_config
        self.img_duration = self.config['animations'][self.anim_type]['img_duration']
        self.loop = self.config['animations'][self.anim_type]['loop']
        
        self.done = False
        self.frame = 0
    
    @property  
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
    def copy(self):
        return Animation((self.id, self.anim_type), self.images, self.config)
    
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
        self.generate_anims(ANIMATION_PATH)
     
    
    def generate_anims(self, path):
        for entity_id in os.listdir(path):
            change_config = False
            try:
                config = load_json(path + entity_id + '/' + CONFIG_FILE)
            except FileNotFoundError:
                change_config = True
                config = {'id': entity_id, "animations": {}}
                
            for anim in os.listdir(path + entity_id):
                full_path = path + entity_id + '/' + anim
                if os.path.isdir(full_path):
                    if not config['animations'] or not anim in config['animations']:
                        config['animations'][anim] = {'img_duration': 0.1, 'loop': False}
                    self.animations[entity_id + '/' + anim] = Animation(anim_id=(entity_id, anim), images=load_imgs(f'entities/{entity_id}/{anim}', colorkey=COLORKEY), anim_config=config)
            
            if change_config:
                save_json(path=path + entity_id + '/' + CONFIG_FILE, data=config)
        
    def new(self, anim_id):
        return self.animations[anim_id].copy()                