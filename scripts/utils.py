import os
import json
import pygame

BASE_IMG_PATH = 'data/images/'

def load_img(path, alpha=False, colorkey=(0, 0, 0)):
    img = pygame.image.load(BASE_IMG_PATH + path).convert() if not alpha else pygame.image.load(path).convert_alpha()
    if colorkey:
        img.set_colorkey(colorkey)
    return img

def load_imgs(path, alpha=False, colorkey=(0, 0, 0)):
    imgs = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        imgs.append(load_img(path + '/' + img_name, alpha, colorkey))
    return imgs

def load_json(path):
    f = open(path)
    data = json.load(fp=f)
    f.close()
    return data

def save_json(path, data):
    f = open(path, 'w')
    json.dump(data, fp=f)
    f.close()