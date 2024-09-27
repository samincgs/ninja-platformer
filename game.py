import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds 
from scripts.animations import Animation
from scripts.particle import Particle

class Game:
    def __init__(self):
        pygame.init()

        #displays
        pygame.display.set_caption('ninja platformer')
        self.screen = pygame.display.set_mode((640, 480)) # main screen 40 / 30
        self.display = pygame.Surface((320, 240)) #display screen
    
        self.clock = pygame.time.Clock()
        
        self.assets = { # all assets loaded in using utils
            'background': load_image('background.png'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'decor': load_images('tiles/decor'),
            'large_decor': load_images('tiles/large_decor'),
            'player': load_image('entities/player.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=6),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),  
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), loop=False)
        }
        
        self.movement = [False, False]
        
        self.clouds = Clouds(self.assets['clouds'], count=20)
        
        self.player = Player(self, (120, 75), self.assets['player'].get_size())
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.scroll = [0, 0]
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
        
        self.leaf_spawners = []
        self.particles = []
        
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True): # get the position of the tree images using the extract function
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13)) # make the tree into a pygame.Rect and store it in the list add 5 to the position to get a decent position for where the leaf should start spawning (30, 15) because it makes sense for the leaves to be there
        
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)], keep=False):
            if spawner['variant'] == 0: # player
                self.player.pos = spawner['pos']
            else:
                print(spawner['pos'], 'enemy') # enemy
 
    def run(self):
        while True:
            
            self.display.blit(self.assets['background'], (0, 0))
                        
            #camera
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            # spawn the particles in the tree area
            for rect in self.leaf_spawners:
                # random.random is a random number between 0 and 1 not including 1 (0.25)
                # use the area formula wxh to spawn a leaf particle where the likelihood of triggering depends on the size of the rectangle
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height) # get a position bounded within the rect since rect.x is the topleft of the rect and random.radom()* width can never exceed the width
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
                

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))  
            self.player.render(self.display, offset=render_scroll)
            
            # collection of particles
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    # use 0.035 as frequency control to make sure it doesnt oscillate too fast and be jittery or too rapid (too slow down how fast it goes left and right, make sure it doesnt finish too quick)
                    # 0.3 to control the amplitude, here it moves to 0.3 and -0.3
                    # we use particle.animation.frame because we need something that changes over time in order to provide natural and fluid movement
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3 # the sin function produces a value that oscilates between -1 and 1
                if kill:
                    self.particles.remove(particle)
            
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))         
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()

