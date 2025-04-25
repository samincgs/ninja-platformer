import pygame
import math
import sys
import time
import random

from scripts.player import Player
from scripts.tilemap import Tilemap
from scripts.animation import Animations
from scripts.utils import load_img, load_imgs
from scripts.clouds import Clouds
from scripts.particles import Particle

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja Platformer')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        
        self.clock = pygame.time.Clock()
        self.master_clock = 0
                
        self.dt = 0.01
        self.last_time = time.time()
        
        self.assets = {
            'grass': load_imgs('tiles/grass'),
            'stone': load_imgs('tiles/stone'),
            'decor': load_imgs('tiles/decor'),
            'large_decor': load_imgs('tiles/large_decor'),
            'player': load_img('entities/player/player.png'),
            'background': load_img('background.png'),
            'clouds': load_imgs('clouds'),
            'particles/leaf': load_imgs('particles/leaf'),
            'particles/particle': load_imgs('particles/particle'),
        }
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.animations = Animations()
        
        self.tilemap.load_map('map.json')
                
        self.player = Player(self, (70, 20), self.assets['player'].get_size())
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.input = {'left': False, 'right': False, 'jump': False}
        self.scroll = [0, 0]
        
        self.particles = []
        self.leaf_spawners = []
        
        tree_filter = lambda x: x['type'] == 'large_decor' and x['variant'] == 2
        for tree in self.tilemap.extract(tree_filter, keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

    def run(self):
        while True:
            self.dt = time.time() - self.last_time
            self.last_time = time.time()
            
            self.master_clock += self.dt
                        
            self.display.blit(self.assets['background'], (0, 0))
            
            camera_speed = 0.4
            self.scroll[0] += (self.player.rect.center[0] - self.display.get_width() // 2 - self.scroll[0]) / (camera_speed / self.dt)
            self.scroll[1] += (self.player.rect.center[1] - self.display.get_height() // 2 - self.scroll[1]) / (camera_speed / self.dt)
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for tree_rect in self.leaf_spawners:
                if random.random() * 49999 < tree_rect.width * tree_rect.height:
                    leaf_pos = (tree_rect.x + random.random() * tree_rect.width, tree_rect.y + random.random() * tree_rect.height)
                    self.particles.append(Particle(self, 'leaf', leaf_pos, [-15, 35], random.randint(0, 6), decay_rate=2, custom_color=None))
            
            self.clouds.update(self.dt)
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render_visible(self.display, offset=render_scroll)
            
            self.player.update(self.dt)
            self.player.render(self.display, offset=render_scroll)
            
            for particle in self.particles.copy():
                kill = particle.update(self.dt)
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.frame) * 0.8

                if kill:
                    self.particles.remove(particle)
            
            self.input['jump'] = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.input['left'] = True
                    if event.key == pygame.K_RIGHT:
                        self.input['right'] = True
                    if event.key == pygame.K_UP:
                        self.input['jump'] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.input['left'] = False
                    if event.key == pygame.K_RIGHT:
                        self.input['right'] = False
                    
                    
            # print(self.clock.get_fps())
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
            
            
if __name__ == '__main__':
    Game().run()