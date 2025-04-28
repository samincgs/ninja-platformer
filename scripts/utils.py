import pygame
import os
import json

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

def load_dir(path, alpha=False, colorkey=(0, 0, 0)):
    imgs = {}
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        imgs[img_name] = load_imgs(path + '/' + img_name, alpha=alpha, colorkey=colorkey)
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

def palette_swap(surf, old_color, new_color):
    img = surf.copy()
    surf.set_colorkey(old_color)
    img.fill(new_color)
    img.blit(surf, (0, 0))
    return img.copy()

def normalize(vel, amt, target=0):
    if vel > target:
        return max(vel - amt, target)
    elif vel < target:
        return min(vel + amt, target)
    return target