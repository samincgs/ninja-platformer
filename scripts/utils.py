import pygame
from os import listdir

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0,0,0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(listdir(BASE_IMG_PATH + path)):
        img = load_image(path + '/' + img_name)
        images.append(img)
    return images