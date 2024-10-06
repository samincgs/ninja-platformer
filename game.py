import pygame
import sys
import random
import math
import os

from scripts.entities import PhysicsEntity, Player, Enemy
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
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=6),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), loop=False)
        }
        
        self.movement = [False, False]

        self.clouds = Clouds(self.assets['clouds'], count=20)
        
        self.player = Player(self, (120, 75), self.assets['player'].get_size())
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.level = 0
        self.load_level(self.level)
        
        self.screenshake = 0
        
    def load_level(self, map_id):
        self.tilemap.load(f'data/maps/{map_id}.json')
        
        self.scroll = [0, 0]
        
        self.leaf_spawners = []
        self.particles = []
        self.enemies = []
        self.projectiles = []
        self.sparks = []
        self.dead = 0
        
        self.transition = -30
        
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True): # get the position of the tree images using the extract function
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13)) # make the tree into a pygame.Rect and store it in the list add 5 to the position to get a decent position for where the leaf should start spawning (30, 15) because it makes sense for the leaves to be there
        
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)], keep=False):
            if spawner['variant'] == 0: # player
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
    
    def run(self):
        while True:
            print(len(os.listdir('data/maps')))
            self.display.blit(self.assets['background'], (0, 0))
            
            self.screenshake = max(0, self.screenshake - 1)
            
            # when transition is 0, you can see everything on the screen and then when its 30 or -30 you cant see a thing
            if not len(self.enemies): # if you have killed all the enemies
                self.transition += 1
                if self.transition >= 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level) # loads new level and sets transition back to -30
            if self.transition < 0: # goes from -30 to 0
                self.transition += 1
            
            if self.dead:
                self.dead += 1
                print(self.transition)
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead >= 40: # add a small delay before the level is reset
                    self.load_level(self.level)
                                            
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
            
            for enemy in self.enemies.copy(): # copy because we will be removing from the list
                kill = enemy.update(self.tilemap, movement=(0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
            
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))  
                self.player.render(self.display, offset=render_scroll)
                
            # projectiles shot by the enemy
            for projectile in self.projectiles.copy():
                kill = projectile.update()
                projectile.render(self.display, offset=render_scroll)
                if kill:
                    self.projectiles.remove(projectile)
            
            # all sparks added for visual effects       
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
               
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
            
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size()) # create a black surface
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8) # multiply by 8 so it reaches 240 (height of the screen)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
                
            # we created a random value between 0 and screenshake and then subtracth half of the screenshake value effectively centering it around 0
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)         
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()

