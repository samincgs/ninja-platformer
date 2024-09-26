class Animation:
    def __init__(self, images, img_dur=5,loop=True):
        self.images = images
        self.loop= loop
        self.img_duration = img_dur
        
        self.frame = 0
        self.done = False
        
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    @property
    def img(self):
        return self.images[int(self.frame / self.img_duration)] 
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, (self.img_duration * len(self.images) - 1))
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
            
    
        
    
        
    