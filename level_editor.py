import pygame
import sys
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0

class LevelEditor:
    def __init__(self):
        pygame.init()

        #displays
        pygame.display.set_caption('level editor')
        self.screen = pygame.display.set_mode(((640, 480))) # main screen
        self.display = pygame.Surface((320, 240)) #display screen
 
        self.clock = pygame.time.Clock()
        
        self.assets = { # all assets loaded in using utils
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'decor': load_images('tiles/decor'),
            'large_decor': load_images('tiles/large_decor'),
            'spawners': load_images('tiles/spawners')
        }
        
        self.movement = [False, False, False, False]
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.scroll = [0, 0]
        
        self.tile_list = list(self.assets) # all keys from the self.assets dict
        self.tile_group = 0 # this is gonna be the group we are going to be using (grass, stone, decor etc.)
        self.tile_variant = 0 # which tile number we are gonna be using (0.png, 1.png)
        
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        
        self.ongrid = True
        
        try:
            self.tilemap.load('data/maps/0.json')
        except FileNotFoundError:
            pass

    def run(self):
        while True:
            
            self.display.fill((0, 0, 0))
            
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 3
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 3
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(150)
            
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size)) # dividng by tilesize makes it snap to the grid 
            
            if self.ongrid:
                # see where the next tile would be placed
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)
            
            # place a block on the grid
            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            # remove an existing block on the grid
            if self.right_clicking:
                if self.ongrid: # remove tiles when they are placed on the grid
                    tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                    if tile_loc in self.tilemap.tilemap:
                        del self.tilemap.tilemap[tile_loc]
                else: # remove tiles when they are placed offgrid
                    for tile in self.tilemap.offgrid_tiles.copy():
                        tile_img = self.assets[tile['type']][tile['variant']]
                        tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                        if tile_r.collidepoint(mpos):
                            self.tilemap.offgrid_tiles.remove(tile)
        
            self.display.blit(current_tile_img, (5, 5))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid: # to make sure the object is only placed once per click instead of 60 times per second
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                        if event.button == 5:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o: # use o for output
                        self.tilemap.save('data/maps/0.json')
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))         
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    LevelEditor().run()

