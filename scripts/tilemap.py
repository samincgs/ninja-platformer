import pygame
import json

NEIGHBOR_OFFSETS = [(0, 0), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)] # all 9 positions around the character as well as its self
PHYSICS_TILES = {'grass', 'stone'}

AUTOTILE_TYPES = {'grass', 'stone'}
AUTOTILE_MAP = { # run sorted on the list to make sure the list comes out in the same order everytime and then convert into a tuple because a list cannot be used as a key
    tuple(sorted([(1, 0), (0, 1)])): 0, # top left
    tuple(sorted([(-1, 0), (0, 1), (1, 0)])): 1, # top middle
    tuple(sorted([(-1, 0), (0, 1)])): 2, # top right
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3, # middle right
    tuple(sorted([(-1, 0), (0, -1)])): 4, # bottom right
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5, # bottom middle
    tuple(sorted([(1, 0), (0, -1)])): 6, # bottom left
    tuple(sorted([(1, 0), (0, 1), (0, -1)])): 7, # middle left
    tuple(sorted([(-1, 0), (1, 0), (0, 1), (0, -1)])): 8, # middle middle
}

class Tilemap:
    def __init__(self, game, tile_size = 16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}  # self.tilemap[3;10] = {'type': 'grass', 'variant': 1, 'pos': (3 + i, 10)}
        self.offgrid_tiles = [] # {'type': 'grass', 'variant': 1, 'pos': (3 + i, 10)}
        
        # for i in range(10):
        #     self.tilemap[str(3 + i) + ';10'] = {'type': 'grass', 'variant': 1, 'pos': (3 + i, 10)}
        #     self.tilemap['10;' + str(5 + i)] = {'type': 'stone', 'variant': 1, 'pos': (10, 5 + i)}
            
    
    def tiles_around(self, pos):
        tiles = []
        # we int the tile position again because if we have a float for a position it still keeps the 0 
        #(we also do // divide because it deals with negative numbers different from / ) (int (-3/2) = -1.5) -3 // 2 = -2
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size)) 
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, fp=f)
        f.close()
    
    def load(self, path):
        f = open(path, 'r')
        tile_map = json.load(f)
        f.close()
        
        self.tilemap = tile_map['tilemap']
        self.tile_size = tile_map['tile_size']
        self.offgrid_tiles = tile_map['offgrid']
    
    def autotile(self):
        for loc in self.tilemap: # ex. 1;2
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']: # check if the neighbouring tile is the same tile as its self
                        neighbors.add(shift) # depending on which direction the same tile is, add that shift to the set
            
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]
                
           
    def render(self, surf, offset=(0, 0)):
        
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        # using the current camera and location to render tiles only depending on the current world frame    
        for x in range(offset[0] // self.tile_size, ((offset[0] + surf.get_width()) // self.tile_size) + 1):
            for y in range(offset[1] // self.tile_size, ((offset[1] + surf.get_height()) // self.tile_size) + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size- offset[1]))
        
        
        # for loc in self.tilemap:
        #     tile = self.tilemap[loc]
        #     surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size- offset[1]))