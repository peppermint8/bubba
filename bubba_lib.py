#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""
common functions
"""

import random
import pygame
import functools
import math

#from rom import dungeon

CZ = - math.pi / 4


@functools.cache
def rotate(r, size, cxy):
    r0 = r - CZ
    
    x = math.cos(r0) * size + math.sin(r0) * size + cxy[0]
    y = math.sin(r0) * size - math.cos(r0) * size + cxy[1]

    x = int(x)
    y = int(y)
    return (x,y)


def convert_color(color_str):
    clr = (0, 0, 0)
    if not color_str:
        return get_rgb()

    if not color_str.startswith("#"):
        color_str = "#" + color_str
    
    clr = pygame.Color(color_str)

    return clr

@functools.cache
def distance(ax, ay, bx, by):
    d = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
    return d

def get_direction(v, d=[]):
    vx = vy = 0
    d_lst = ["u", "d", "l", "r"] #, "z"]
    for d0 in d:
        d_lst.remove(d0)

    r = random.choice(d_lst)
    if r == "u":
        vy = -v
    elif r == "d":
        vy = v
    elif r == "l":
        vx = -v
    elif r == "r":
        vx = v

    return vx, vy



def random_name():

    c = ["w", "r", "t", "y", "p", "l", "k", "j", "h", "g", "f", "d", "s", "z", "x", "c", "v", "b", "n", "m", 
    "tr", "th", "sl", "ch", "fl", "br", "dr", "pr", "gh", "gr", "st", "sc", "sp", "wr", "fr", "qu"]
    v = ["a", "e", "i", "o", "u", "oo", "ou", "oa", "ie"] #, "y"] # utf-8?
    nombre = "" #unknown"
    n = random.choice([3, 4, 4, 4, 5, 5, 5, 6, 7, 8, 3])
    for i in range(0, n):
        if i % 2 == 0:
            nombre += random.choice(c)
        else:
            nombre += random.choice(v)

    return nombre.title()