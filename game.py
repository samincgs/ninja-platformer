import pygame, sys
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds

class Game:
    def __init__(self):
        pygame.init()

        # main screen
        self.screen = pygame.display.set_mode((640, 480))
        
        # display screen made to enlarge the pixels of the entities/tiles
        self.display = pygame.Surface((320, 240))
        
        pygame.display.set_caption('ninja platformer')

        self.clock = pygame.time.Clock()
        
        # assets for all the imports
        self.assets = {
            'player': load_image('entities/player.png'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'decor': load_images('tiles/decor'),
            'large_decor': load_images('tiles/large_decor'),
            'background': load_image('background.png'),
            'clouds' : load_images('clouds'),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump')),
            'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
        }
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self,(50, 50), (8, 15))
        self.movement = [False, False]
        
        # tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        
        # camera
        self.scroll = [0, 0]
        
    def run(self):
        while True: 
            
            self.display.blit(self.assets['background'], (0, 0))
            
            # camera
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            # clouds
            self.clouds.update()
            self.clouds.render(self.display,offset= render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.velocity[1] = -3
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))   
            pygame.display.update()
            self.clock.tick(60)
            
Game().run()