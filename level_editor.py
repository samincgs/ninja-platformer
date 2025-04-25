import pygame
import sys
import time

from scripts.tilemap import Tilemap
from scripts.utils import load_img, load_imgs

RENDER_SCALE = 2

class LevelEditor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Level Editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        
        self.clock = pygame.time.Clock()
        
        
        self.last_time = time.time()
        
        self.assets = {
            'grass': load_imgs('tiles/grass'),
            'stone': load_imgs('tiles/stone'),
            'decor': load_imgs('tiles/decor'),
            'large_decor': load_imgs('tiles/large_decor'),
        }
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        
        self.movement = [False, False, False, False]
        self.scroll = [0, 0]
        self.clicking  = False
        self.right_clicking  = False

    def run(self):
        while True:
                    
            self.display.fill((0, 0, 0))
            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(130)
            
            self.display.blit(current_tile_img, (5, 5))
                                    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    if event.button == 3:
                        self.right_clicking = True
                    if event.type == 4:
                        self.tile_group = (self.tile_group - 1) % len(self.assets)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False
                    
                    
            # print(self.clock.get_fps())
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
            
            
if __name__ == '__main__':
    LevelEditor().run()