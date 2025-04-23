import pygame

SURROUND_POS = [(-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        
        self.tilemap = {}
        self.offgrid_tiles = []
        
        for i in range(8):
            self.tilemap[str(3 + i) + ';9'] = {'type': 'grass', 'variant': 1, 'pos': (3 + i, 9)}
        
        for i in range(5):
            self.tilemap['7;' + str(5 + i)] = {'type': 'stone', 'variant': 1, 'pos': (7 , 5 + i)}
            
    def collision_test(self, entity_rect, rect_list):
        collision_rects = []
        for tile_rect in rect_list:
            if entity_rect.colliderect(tile_rect):
                collision_rects.append(tile_rect)
        return collision_rects
    
    # pos in pixels
    def get_nearby_rects(self, pos):
        rects = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in SURROUND_POS:
            str_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if str_loc in self.tilemap:
                tile = self.tilemap[str_loc]
                if tile['type'] in PHYSICS_TILES:
                    rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
                
    def render(self, surf):
        # offgrid
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'])
        # grid
        for tile_loc in self.tilemap:
            tile = self.tilemap[tile_loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))