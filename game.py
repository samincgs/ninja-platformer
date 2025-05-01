import pygame
import os
import math
import sys
import time
import random

from scripts.enemy import Enemy
from scripts.player import Player
from scripts.sparks import Spark
from scripts.tilemap import Tilemap
from scripts.animation import Animations
from scripts.utils import load_img, load_imgs, load_dir
from scripts.clouds import Clouds
from scripts.particles import Particle

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja Platformer')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        
        
        self.clock = pygame.time.Clock()
                
        self.dt = 0.01
        self.last_time = time.time()
                
        self.assets = {}
        self.assets.update(load_dir('tiles'))
        self.assets.update({'clouds': load_imgs('clouds'), 'background': load_img('background.png'), 'gun': load_img('gun.png'), 'projectile': load_img('projectile.png')})
        
        self.particle_assets = load_dir('particles')
        
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
        }
        
        self.sfx['ambience'].set_volume(0.1)
        self.sfx['dash'].set_volume(0.1)
        self.sfx['jump'].set_volume(0.2)
        self.sfx['hit'].set_volume(0.4)
        self.sfx['shoot'].set_volume(0.3)
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.animations = Animations()
        
        self.player = Player(self, (70, 20), (8, 15))
        self.clouds = Clouds(self.assets['clouds'], count=16)
                
        self.input = {'left': False, 'right': False, 'jump': False, 'dash': False}
        
        self.level = 0
        self.load_level(self.level)
        
        self.screenshake = 0
        
    def load_level(self, map_id):
        
        self.dead = 0
        self.scroll = [0, 0]
        self.transition = -0.5
        
        self.particles = []
        self.projectiles = []
        self.leaf_spawners = []
        self.enemies = []
        self.sparks = []
        
        self.tilemap.load_map('data/maps/' + str(map_id) + '.json')
        
        tree_filter = lambda x: x['type'] == 'large_decor' and x['variant'] == 2
        for tree in self.tilemap.tile_filter(tree_filter, keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        spawner_filter = lambda x: x['type'] == 'spawners' and x['variant'] in {0, 1}
        for spawner in self.tilemap.tile_filter(spawner_filter):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            
    def run(self):
        
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(loops=-1)
        
        self.sfx['ambience'].play(-1)
        
        while True:
                
            mask_display = pygame.Surface(self.display.get_size()) 
            mask_display.set_colorkey((0, 0, 0))
                
            self.display.blit(self.assets['background'], (0, 0))
            
            self.dt = time.time() - self.last_time
            self.dt = min(max(0.00001, self.dt), 0.1)
            self.last_time = time.time()
            
            self.screenshake = max(0, self.screenshake - self.dt)
            
            if not len(self.enemies):
                self.transition = min(self.transition + self.dt, 0.5)
                if self.transition >= 0.5:
                    self.level = min(self.level + 1, len(os.listdir('data/maps/')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition = min(self.transition + self.dt, 0)

            if self.dead:
                self.dead += self.dt
                if self.dead >= 0.1:
                    self.transition += self.dt
                if self.dead > 0.6:
                    self.load_level(self.level)              

            camera_speed = 0.4
            self.scroll[0] += (self.player.rect.center[0] - self.display.get_width() // 2 - self.scroll[0]) / (camera_speed / self.dt)
            self.scroll[1] += (self.player.rect.center[1] - self.display.get_height() // 2 - self.scroll[1]) / (camera_speed / self.dt)
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for tree_rect in self.leaf_spawners:
                if random.random() * 500  < (tree_rect.width * tree_rect.height) * self.dt:
                    leaf_pos = (tree_rect.x + random.random() * tree_rect.width, tree_rect.y + random.random() * tree_rect.height)
                    self.particles.append(Particle(self, 'leaf', leaf_pos, [-15, 35], random.randint(0, 6), decay_rate=2, custom_color=None))
            
            self.clouds.update(self.dt)
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render_visible(mask_display, offset=render_scroll)
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.dt)
                enemy.render(mask_display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                self.player.update(self.dt)
                self.player.render(mask_display, offset=render_scroll)
            
            # pos, direction, timer
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1] * self.dt
                projectile[2] += self.dt
                proj_img = self.assets['projectile']
                mask_display.blit(proj_img, (projectile[0][0] - render_scroll[0] - proj_img.get_width() / 2, projectile[0][1] - render_scroll[1] - proj_img.get_height() / 2))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + math.pi, 120 + random.random() * 60, 4 + random.random()))
                if projectile[2] > 6:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect.collidepoint(projectile[0]): 
                        self.sfx['hit'].play()
                        self.screenshake = max(0.4, self.screenshake)
                        self.dead += self.dt
                        self.projectiles.remove(projectile)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect.center, angle, 120 + random.random() * 60, 4 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect.center, velocity=[math.cos(angle + math.pi) * speed * 30, math.sin(angle + math.pi) * speed * 30], custom_color=(20, 16, 42), decay_rate=10.5))
              
            
            for spark in self.sparks.copy():
                kill = spark.update(self.dt)
                spark.render(mask_display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
            
            mask_surf = pygame.mask.from_surface(mask_display)
            mask_surf_silhouette = mask_surf.to_surface(setcolor=(2, 3, 12, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                self.display.blit(mask_surf_silhouette, offset)
            
            
            for particle in self.particles.copy():
                kill = particle.update(self.dt)
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.frame) * 48 * self.dt 
                if kill:
                    self.particles.remove(particle)
            
            self.input['jump'] = False
            self.input['dash'] = False
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
                    if event.key == pygame.K_x:
                        self.input['dash'] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.input['left'] = False
                    if event.key == pygame.K_RIGHT: 
                        self.input['right'] = False
                    
                    
            self.display.blit(mask_display, (0, 0))
            # print(self.clock.get_fps())
            
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (0.5 - abs(self.transition)) * 480)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
            
            
            
            screenshake_offset = (random.random() * self.screenshake * 30 - self.screenshake * 30 / 2, random.random() * self.screenshake * 30 - self.screenshake * 30 / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)
            pygame.display.flip()
            self.clock.tick(60)
            
            
if __name__ == '__main__':
    Game().run()