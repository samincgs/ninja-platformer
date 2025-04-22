import pygame
import sys


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja Platformer')
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        
        self.fps = 60
        self.dt = 0.01
        
        self.movement = [False, False]
        
        
        self.img = pygame.image.load('data/images/clouds/cloud_1.png').convert()
        self.img.set_colorkey((0, 0, 0))
        
        self.img_pos = [160, 260]
        
        self.collideable_area = pygame.Rect(50, 50, 300, 50)
        

    def run(self):
        while True:
            
            self.screen.fill((14, 219, 248))
            
            self.img_pos[1] += (self.movement[1] - self.movement[0]) * 5
            img_rect = pygame.Rect(self.img_pos[0], self.img_pos[1], self.img.get_width(), self.img.get_height())
            
            if img_rect.colliderect(self.collideable_area):
                pygame.draw.rect(self.screen, (0, 100, 255), self.collideable_area)
            else:
                pygame.draw.rect(self.screen, (0, 50, 155), self.collideable_area)
            
            self.screen.blit(self.img, self.img_pos)
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                    if event.key == pygame.K_f:
                        self.fps = 30 if self.fps == 60 else 60
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False
                    
                    
            # print(self.clock.get_fps())
            pygame.display.flip()
            self.dt = self.clock.tick(self.fps) / 1000
            
if __name__ == '__main__':
    Game().run()