import pygame
import sys
import time

from scripts.player import Player
from scripts.tilemap import Tilemap
from scripts.animation import Animation
from scripts.utils import load_img, load_imgs
from scripts.clouds import Clouds

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja Platformer')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        
        self.clock = pygame.time.Clock()
        
        self.fps = 60
        
        self.dt = 0.01
        self.last_time = time.time()
        
        self.assets = {
            'grass': load_imgs('tiles/grass'),
            'stone': load_imgs('tiles/stone'),
            'decor': load_imgs('tiles/decor'),
            'large_decor': load_imgs('tiles/large_decor'),
            'player': load_img('entities/player.png'),
            'background': load_img('background.png'),
            'clouds': load_imgs('clouds')
        }
        
        self.animations = {
            'player/idle': Animation(load_imgs('entities/player/idle'), img_dur=0.12, loop=True),
            'player/run': Animation(load_imgs('entities/player/run'), img_dur=0.08, loop=True),
            'player/jump': Animation(load_imgs('entities/player/jump'), loop=False),
            'player/wall_slide': Animation(load_imgs('entities/player/wall_slide'), loop=False),
        }
        
        
        self.player = Player(self, (70, 20), self.assets['player'].get_size())
        self.tilemap = Tilemap(self, tile_size=16)
        self.clouds = Clouds(self.assets['clouds'], count=20)
        
        self.input = [False, False]
        self.scroll = [0, 0]

    def run(self):
        while True:
            self.dt = time.time() - self.last_time
            self.last_time = time.time()
                        
            self.display.blit(self.assets['background'], (0, 0))
            
            camera_speed = 0.4
            self.scroll[0] += (self.player.rect.center[0] - self.display.get_width() // 2 - self.scroll[0]) / (camera_speed / self.dt)
            self.scroll[1] += (self.player.rect.center[1] - self.display.get_height() // 2 - self.scroll[1]) / (camera_speed / self.dt)
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.clouds.update(self.dt)
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render_visible(self.display, offset=render_scroll)
            
            self.player.update(self.dt)
            self.player.render(self.display, offset=render_scroll)
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.input[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.input[1] = True
                    if event.key == pygame.K_f:
                        self.fps = 30 if self.fps == 60 else 60
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -160
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.input[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.input[1] = False
                    
                    
            # print(self.clock.get_fps())
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.flip()
            self.clock.tick(self.fps)
            
            
if __name__ == '__main__':
    Game().run()