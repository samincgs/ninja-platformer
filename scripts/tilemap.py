import pygame
from .utils import save_json, load_json

SURROUND_POS = [(-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 0), (-1, 1), (0, 1), (1, 1)]
OFFSET_N4 = [(0, 1), (0, -1), (1, 0), (-1, 0)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])) : 0,
    tuple(sorted([(-1, 0), (0, 1), (1, 0)])) : 1,
    tuple(sorted([(-1, 0), (0, 1)])) : 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])) : 3,
    tuple(sorted([(-1, 0), (0, -1)])) : 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])) : 5,
    tuple(sorted([(1, 0), (0, -1)])) : 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])) : 7,
    tuple(sorted([(1, 0), (0, -1), (0, 1), (-1, 0)])) : 8,   
}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def save_map(self, path):
        save_json(path, {'tilemap': self.tilemap, 'offgrid': self.offgrid_tiles, 'tile_size': self.tile_size})
        
    def load_map(self, path):
        map_data = load_json(path)
        
        self.tilemap = map_data['tilemap']
        self.offgrid_tiles = map_data['offgrid']
        self.tile_size = map_data['tile_size']
    
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
                
    def render(self, surf, offset=(0, 0)):
        # offgrid
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
        # grid
        for tile_loc in self.tilemap:
            tile = self.tilemap[tile_loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in OFFSET_N4:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap: # means neighbour exists
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if tile['type'] in AUTOTILE_TYPES and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]
                
            
           
    def render_visible(self, surf, offset=(0, 0)):
        # offgrid
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
        
        # grid
        for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
            for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
                grid_loc = str(x) + ';' + str(y)
                if grid_loc in self.tilemap:
                    tile = self.tilemap[grid_loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
            
    