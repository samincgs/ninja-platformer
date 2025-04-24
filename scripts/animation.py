class Animation:
    def __init__(self, images, img_dur=0.1, loop=True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0
    
    @property  
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self, dt):
        if self.loop:
            self.frame = (self.frame + dt) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + dt, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
        
    