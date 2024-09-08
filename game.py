import pygame
import sys
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.animations import Animation

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
            'player/run': Animation(load_images('entities/player/run'), img_dur=6,),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),  
        }
        
        self.movement = [False, False]
        
        self.clouds = Clouds(self.assets['clouds'], count=20)
        
        self.player = Player(self, (75, 75), self.assets['player'].get_size())
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.scroll = [0, 0]
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
        
    def run(self):
        while True:
            
            self.display.blit(self.assets['background'], (0, 0))
                        
            #camera
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))  
            self.player.render(self.display, offset=render_scroll)
                
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
                        self.player.velocity[1] = -3
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

