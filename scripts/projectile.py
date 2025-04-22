import random
import math

from scripts.spark import Spark
from scripts.particle import Particle


class Projectile:
    def __init__(self, game, pos, speed, timer=0):
        self.game = game
        self.pos = list(pos)
        self.speed = speed
        self.timer = timer

    def update(self):
        # [[x, y], direction, timer]
        # projectile[0][0] += projectile[1]
        # projectile[2] += 1
        # img = self.assets['projectile']
        # self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1])) # center it to make sure its drawn on its origin point while it moves in a specfic direction (for visual accuray and collision)
        # if self.tilemap.solid_check(projectile[0]):
        #     self.projectiles.remove(projectile)
        # elif projectile[2] > 360: # if timer is greater than 6 seconds
        #     self.projectiles.remove(projectile)
        # elif abs(self.player.dashing) < 50: # if you are not in the actual dashing animation
        #     if self.player.rect().collidepoint(projectile[0]):
        #         self.projectiles.remove(projectile)
        #         print('player hit')

        kill = False

        self.pos[0] += self.speed
        self.timer += 1
        if self.game.tilemap.solid_check(self.pos):
            kill = True
            for i in range(6):
                self.game.sparks.append(Spark(self.pos, random.random() - 0.5 + (math.pi if self.speed > 0 else 0),1 + random.random() * 2,))

        elif self.timer > 360:  # if timer is greater than 6 seconds
            kill = True

        elif (
            abs(self.game.player.dashing) < 50
        ):  # if you are not in the actual dashing animation and the projectile hits the player
            if self.game.player.rect().collidepoint(self.pos):
                kill = True
                self.game.dead += 1  # only is incremented once because the projectile is removed right as it collides
                self.game.screenshake = max(32, self.game.screenshake)
                for i in range(30):
                    angle = random.random() * (
                        math.pi * 2
                    )  # random angle in a full circle
                    speed = random.random() * 5
                    velocity = [math.cos(angle + math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5]  # add math.pi so particles spawn in the opposite direction of the sparks
                    self.game.sparks.append(Spark(self.game.player.rect().center,angle=angle,speed=2 + random.random()))
                    self.game.particles.append(
                        Particle(
                            self.game,
                            "particle",
                            self.game.player.rect().center,
                            velocity=velocity,
                            frame=random.randint(0, 7),
                        )
                    )

        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.game.assets["projectile"]
        surf.blit(img,(self.pos[0] - img.get_width() / 2 - offset[0],self.pos[1] - img.get_height() / 2 - offset[1]))  # center it to make sure its drawn on its origin point while it moves in a specfic direction (for visual accuray and collision)
