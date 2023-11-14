#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Bubba the Beholder
- A Xarnoz production

Inspired by ...
Temple of ROM 
Rick Adams - 1982 - Temple of ROM
chalace - blue
ring
cup - red
red gem
crown
sphere
https://github.com/yggdrasilradio/templeofrom/blob/develop/map/map.gif


To do
- level up
- win the map (what is the condition? find all treasure, kill all monsters)

- image offset for monsters (dragon!)
- ring of regeneration for health

cell size changes
- need to re-size everything


https://www.flaticon.com/search?word=monsters
Freepik
Iconikar
IconMarketPx
redempticon
Lovedat
Xinh
pongsakored

https://www.img2go.com/



lamentations
"""

import sys
import os
import pygame
from pygame.locals import *
import functools
import random
import yaml
import math

from bubba_lib import *


dungeon = []
fog = [] # fog of war
dx = dy = 0

# generic class, teleport, trap, treasure - need to rename it
class Treasure():
    x = y = x0 = y0 = 0
    value = 25

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.x0 = x
        self.y0 = y


class Player():
    alive = True
    v = 0.0
    max_x = 1000
    max_y = 700
    pad = 20
    gs = 25
    lastx = 0
    lasty = 0
    xi = 0
    yi = 0
    pname = "Bubba"
    hp = 50
    key_cnt = 0
    dmg_bonus = 0
    xp = 0
    
    def __init__(self, a, x, y):
        self.a = a
        self.x = x
        self.y = y
        self.x0 = x
        self.y0 = y

    def move(self, direction):
        m_flag = False
        if not self.alive:
            xx = int(self.x / self.gs)
            yy = int(self.y / self.gs)            
            return m_flag, xx, yy
        
        a0 = 0
        v = 0
        if direction == "w":
            # forward
            v = self.v
        elif direction == "s":
            v =  -self.v
        elif direction == "d":
            v = self.v
            a0 = 90
        elif direction == "a":
            v = -self.v
            a0 = 90
           
        xx = yy = 0
        if v != 0:
            new_x = self.x + v * math.sin(math.radians(self.a + a0))
            new_y = self.y + v * math.cos(math.radians(self.a + a0))

            # how do we know if we hit an edge?
            # if new_x + new_y in gs * 
            xx = int(new_x / self.gs)
            yy = int(new_y / self.gs)
            
            
            if not dungeon_wall(xx, yy, water=self.water, lava=self.lava):
                self.x = new_x
                self.y = new_y
                
                if self.xi != xx or self.lasty != yy:
                    print("pos: {},{}  b: {:0.1f},{:0.1f}, a: {:0.1f}".format(xx, yy, self.x, self.y, self.a))

                self.lastx = xx
                self.lasty = yy
                self.xi = xx
                self.yi = yy
                m_flag = True

                self.x0 = self.x + math.sin(math.radians(self.a)) * 10
                self.y0 = self.y + math.cos(math.radians(self.a)) * 10


        return m_flag, xx, yy
    

    def turn(self, m):
        if self.alive:
            self.a += self.av * m
            if self.a > 360.0:
                self.a = self.a - 360.0
            if self.a < 0.0:
                self.a = self.a + 360.0

            #self.x0 = self.x + math.sin(math.radians(self.a)) * 15
            #self.y0 = self.y + math.cos(math.radians(self.a)) * 15
        self.x0 = self.x + math.sin(math.radians(self.a)) * 10
        self.y0 = self.y + math.cos(math.radians(self.a)) * 10



class Beast():
    bname = "the beast"
    ac = 10
    hp = 5
    dmg = 4
    state = "rest"
    mana = mana_max = 100
    water = False
    lava = False
    vx = 0.0
    vy = 0.0
    pad = 10
    attack_distance = 15

    

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.x0 = x
        self.y0 = y
        
    def set_target(self, x, y):
        # ideally do path finding to target
        # self.vx = towards x
        # self.vy = towards y
        xd = x - self.x
        yd = y - self.y
        ad = self.attack_distance * 0.25

        if xd > ad:
            self.vx = self.v
        elif xd < ad:
            self.vx = -self.v
        else:
            self.vx = 0

        if yd > ad:
            self.vy = self.v
        elif yd < ad:
            self.vy = -self.v
        else:
            self.vy = 0

        # if fear, vx, vy = vx,vy * -1

        #print(f"target: {x:.1f},{y:.1f} | {xd:.1f},{yd:.1f}")

    def action(self):

        #b.target = (bubba.x, bubba.y)
        #                b.target_flag = True

        if self.state == "rest":
            self.mana += 1
            if self.mana > self.mana_max:
                self.vx, self.vy = get_direction(self.v)
                self.state = "move"
                # heal HP also, depends on beast

        if self.state == "move":
            self.mana -= 1
            #if self.mana <= 0:
            if 1==2:
                self.state = "rest"
                self.mana = 0
                

            new_x = self.x + self.vx
            new_y = self.y + self.vy
            xd = yd = ""
            padx = pady = 0
            if self.vx > 0:
                padx = self.pad
                xd = "r"
            elif self.vx < 0:
                padx = -self.pad
                xd = "l"


            if self.vy > 0:
                pady = self.pad
                yd = "d"
            elif self.vy < 0:
                pady = -self.pad
                yd = "u"

            xx = int((new_x + padx) / self.gs)
            yy = int((new_y + pady) / self.gs)
            xx = min(xx, self.dx)
            yy = min(yy, self.dy)
            #print("b: {}, {},{}".format(self.bname, xx, yy))
            #print("{}: ({}, {}), vx: {}, vy: {}, xd: {}, yd: {}".format(self.bname, xx, yy, self.vx, self.vy, xd, yd))
            
            if not dungeon_wall(xx, yy, water=self.water, lava=self.lava):
                self.x = new_x
                self.y = new_y
                self.xi = xx
                self.yi = yy
            else:
                xx0 = xx
                yy0 = yy

                if self.vx > 0:
                    xx0 = xx + 1
                elif self.vx < 0:
                    xx0 = xx - 1

                nd_flag = False # new_direction flag
                xx0 = min(self.dx, xx0)
                yy0 = min(self.dy, yy0)

                #if dungeon[xx0][yy] == 0 or dungeon[xx0][yy] >= 20:
                if not dungeon_wall(xx0, yy, water=self.water, lava=self.lava):
                    nd_flag = True


                if self.vy > 0:
                    yy0 = yy + 1
                elif self.vy < 0:
                    yy0 = yy - 1
                # 2 < x < 20
                #if not dungeon[xx][yy0] == 0 or dungeon[xx][yy0] >= 20:
                if not dungeon_wall(xx, yy0, water=self.water, lava=self.lava):
                    nd_flag = True

                if nd_flag:
                    dd = []
                    if xd:
                        dd.append(xd)
                    if yd:
                        dd.append(yd)
                    self.vx, self.vy = get_direction(self.v, dd)

## ----------------------------------------------------------------

def init_screen():
    """initalize screen"""
    pygame.init()

    screen_x = 1000
    screen_y = 700
        
    screen = pygame.display.set_mode((screen_x, screen_y), HWSURFACE|HWPALETTE, 8)
    
    pygame.display.set_caption(map_json.get('game_name', "Bubba the Beholder"))

    pygame.mouse.set_visible(False)
    
    pygame.display.set_allow_screensaver(False)

    return screen, screen_x, screen_y


def intro(screen, screen_x, screen_y):
    """show cool menu screen"""
    play_flag = True
    background_color = (0,100,0)
    done = False

    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()

    clock_tick = 15
    clock = pygame.time.Clock()
    text_clr = (255,255,255)
    text_shadow_clr = (0,0,1)
    title_font = pygame.font.SysFont('arial', 48)
    txt_font = pygame.font.SysFont('arial', 24)

    title = map_json.get('game_name', "Bubba the Beholder")
    
    title_txt = title_font.render(title, 1, text_clr)
    #txt2 = game_font.render(e.text, 1, (0,0,0))
    txt_xy = title_txt.get_rect(center=(screen_x // 2, 100))
    #txt_xy = txt.get_rect(center=txt_xy)
    #bg.blit(title_txt, (txt_xy[0]+2,txt_xy[1]+2))

    intro_txt = map_json.get("intro_text", "")    

    intro_list = []
    intro_y = 200
    for line in intro_txt.split("\n"):
        intro_y += 33
        if not line.strip():
            continue

        intro_txt = txt_font.render(line, 1, text_clr)
        intro_shadow_txt = txt_font.render(line, 1, text_shadow_clr)
        intro_xy = intro_txt.get_rect(center=(screen_x // 2, intro_y))
        
        intro_json = {"txt": intro_txt, "xy": intro_xy, "shadow": intro_shadow_txt}
        
        intro_list.append(intro_json)

    # created by AI
    game_img = pygame.image.load("resources/beholder.jpeg").convert_alpha()
                    
    

    redraw_flag = True
    
    while not done:

        if redraw_flag:
            bg.fill(background_color)
            bg.blit(game_img, (0, 0))

            bg.blit(title_txt, txt_xy)
            #bg.blit(title_txt, (10,10))

            #pygame.draw.rect(bg, (60,10,0,125), [120, 220, 50, 70])

            for i in intro_list:
                # wanted transparent rect
                #pygame.draw.rect(bg, (0,0,0,200), i['xy'])
                bg.blit(i['shadow'], (i['xy'][0] + 5, i['xy'][1] + 5))
                bg.blit(i['txt'], i['xy'])
            #bg.blit(intro_txt, intro_xy)

            screen.blit(bg, (0, 0))
            pygame.display.flip()
            redraw_flag = False

        clock.tick(clock_tick) 

        
        

        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
                play_flag = False
            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    done = True            
                    play_flag = False

                if event.key == K_RETURN:
                    done = True

                # up or down arrow, highlight menu option
                # Start
                # Quit


    return play_flag


def recolor(surface, d=50):
    """reduce color saturation of an image"""
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            r = surface.get_at((x, y))[0]
            if r > 150:
                r -= d
                r = max(r, 0)
            g = surface.get_at((x, y))[1]
            if g > 150:
                g -= d
                g = max(g, 0)
            b = surface.get_at((x, y))[2]
            if b > 150:
                b -= d
                b = max(b, 0)
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))



def main(screen, screen_x, screen_y, dx, dy):
    """main program"""

    clock_tick = 15
    clock = pygame.time.Clock()

    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()

    m = [screen_x // 2, screen_y // 2]
    mm = [0, 0]

    screen_y = screen_y - 50  # bottom task bar

    pygame.mouse.set_pos(m)

    xoff = 0
    yoff = 0
    
    fog_flag = True

    background_color = convert_color("#000000")
    #background_color = convert_color("#445544")
    #gs = 25 # px
    #gs = 15
    gs = 35
    gs = 55

    xrange = dx
    yrange = dy

    bubba_start = map_json.get("player_start", [4,4])
    bubba = Player(0, bubba_start[0] * gs, bubba_start[1] * gs)
    bubba.alive = True
    xoff = -gs * bubba_start[0] + screen_x // 2
    yoff = -gs * bubba_start[1] + screen_y // 2

    bubba.xi = bubba_start[0]
    bubba.yi = bubba_start[1]
    bubba.av = 0.05 # angular velocity with rotation
    bubba.v = 5 # movement speed
    bubba.gs = gs
    bubba.mana = 25
    bubba.mana_max = 25
    bubba.mana_rate = 0.1
    bubba.hp = bubba.hp_max = 25
    # 1 = acid
    bubba.weapon_dmg_1 = [1,5]
    bubba.mana_weapon_1 = 5
    bubba.weapon_type_1 = "acid"
    # 2 = lightning
    bubba.weapon_dmg_2 = [10,20]
    bubba.mana_weapon_2 = 10
    bubba.weapon_type_2 = "lightning"
    # 3 = fireball
    bubba.weapon_dmg_3 = [20,40]
    bubba.mana_weapon_3 = 20    
    bubba.weapon_type_3 = "fireball"
    # 4 = ?
    
    bubba.dmg_bonus = 1.0 # multiplier

    bubba.weapon = 1 # acid stuff
    bubba.spell_type = bubba.weapon_type_1

    bubba.size = int(0.72 * gs // 2)

    
    # set all specials from map config (setattr?) 
    for s in map_json['spells']:
        setattr(bubba, s, False)

    
    # x padding, y padding to position player
    xp = 15 
    yp = 15 

    b_list = [] # beasts
    # collect monster locations
    teleport_list = [] # list of teleports
    t_list = [] # treasures
    trap_list = [] # traps

    g_json = {} # glyphs and ids
    for b in map_json['monsters']:
        g = map_json['monsters'][b]['glyph']
        g_json[g] = b

    t_json = {}
    for t in map_json['treasure']:
        g = map_json['treasure'][t]['glyph']
        t_json[g] = t

    tr_json = {}
    for tr in map_json['traps']:
        g = str(map_json['traps'][tr]['glyph'])
        tr_json[g] = tr
        

    tele_cnt = 0
    trap_cnt = 0

    for yi in range(dy):
        for xi in range(dx):
            tile = chr(dungeon[xi][yi])



            # teleporter
            if tile == "@":
                dungeon[xi][yi] = 25
                tele_cnt += 1
                tele = Treasure(xi * gs + xp, yi * gs + yp)
                tele.id = f"teleport-{tele_cnt}"
                tele.x = xi
                tele.y = yi
                tele.active = True
                tele.wait = 0
                tele.wait_max = 300
                tele.pulse = 20 + random.randint(1,10) * 10 
                tele.pv = 20 # speed of pulse
                teleport_list.append(tele)

            if tile in ("1234567890"):
                t = tr_json.get(tile)
                if t:
                    tr_info = map_json['traps'][t]
                    dungeon[xi][yi] = 26
                    trap_cnt += 1
                    trap = Treasure(xi * gs + xp, yi * gs + yp)
                    trap.xi = xi
                    trap.yi = yi
                    trap.active = True
                    #trap.id = f"{t}-{trap_cnt}"
                    trap.id = tr_info.get("special")
                    trap.dmg = tr_info.get("damage", 5)
                    trap.time = 23
                    trap_list.append(trap)

            if tile in ("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"):
                b = g_json.get(tile)
                if b:
                    m_info = map_json['monsters'][b]
                    xp = gs // 2
                    yp = gs // 2
                    beast = Beast(xi * gs + xp, yi * gs + yp)
                    #b.target_dist = 25
                    beast.type = b
                    beast.xi = xi
                    beast.yi = yi
                    beast.gs = gs
                    beast.dx = dx
                    beast.dy = dy
                    #beast.mana_max = m_info.get("mana", 100)
                    beast.mana_max = m_info.get("energy", 100) * 10
                    beast.mana = beast.mana_max #random.randint(1, beast.mana_max)
                    beast.id = random_name()
                    beast.v = m_info.get("speed", 1)
                    beast.xp = m_info.get("xp", 0)
                    beast.target_distance = m_info.get("target_distance", 4) * gs
                    beast.attack_distance = m_info.get("attack_distance", 1) * gs
                    beast.hp_max = beast.hp = m_info.get("hp", 1) # eval
                    beast.armor_bonus = m_info.get("armor", 0)
                    beast.weapon = m_info.get("weapon", "")
                    beast.attack_time = m_info.get("attack_time", 25) # how often between attacks
                    beast.dmg = m_info.get("dmg", 0)
                    beast.vx, beast.vy = get_direction(beast.v)
                    beast.immune = m_info.get("immune", "")
                    beast.special = m_info.get("special", "")
                    beast.money = 0       
                    beast.target_flag = 0
                    beast.size = float(m_info.get("scale", 1.0)) # percent of gs
                    #print(f"beast: {b}, size: {beast.size}")
                    beast.img = pygame.image.load(m_info["image"]).convert_alpha()
                    # reduce colors in image
                    #if beast.special == "invisible":
                    #    drop(beast.img, 200)
                        
    
                    beast.img = pygame.transform.scale(beast.img, (gs * beast.size, gs * beast.size))
                    beast.img_pad = int(gs * (1-beast.size) /2)

                    b_list.append(beast)
                    #print(f"- [{xi},{yi}] = {b}: {beast.type} - {beast.id}")

                t = t_json.get(tile)
                if t:
                    t_info = map_json['treasure'][t]
                    xp = gs // 2
                    yp = gs // 2
                    treasure = Treasure(xi * gs + xp, yi * gs + yp)
                    treasure.value = t_info.get("value", 25)
                    treasure.id = t
                    treasure.xi = xi
                    treasure.yi = yi                    
                    # special?  e.g. ring of vision
                    treasure.text = t_info.get("text")
                    treasure.special = t_info.get("special")
                    treasure.img = pygame.image.load(t_info["image"]).convert_alpha()
                    treasure.size = t_info.get("scale", 0.75)
                    treasure.img_pad = int(gs * (1-treasure.size) /2)
                    treasure.img = pygame.transform.scale(treasure.img, (gs * treasure.size, gs * treasure.size))
                    t_list.append(treasure)
                    #print(f"- [{xi},{yi}] = {t}, value: {treasure.value}")

    
    gold_list = []
    
    beast_hit_range = gs // 2  # for bubba to hit
    treasure_dist = gs // 2

    # random gold in the dungeon
    for g in range(10):
        xb = yb = 0
        done = False
        while not done:
            xb = random.randint(0, xrange-1)
            yb = random.randint(0, yrange-1)
            if dungeon[xb][yb] == 0:
                done = True
        #dungeon[xb][yb] = 4

        gold = Player(0, gs*xb + xp, gs*yb + yp)
        gold.v = 0
        gold.xi = xb
        gold.yi = yb
        gold.gs = gs
        gold.money = random.choice([5,10,25])
        gold_list.append(gold)


    game_font = pygame.font.SysFont('arial', 24)
    #game_font = pygame.font.Font('resources/CheyenneSans-Regular.ttf', 32)

    teleport_sound = pygame.mixer.Sound("resources/teleport-90137.mp3")
    shot_sound_1 = pygame.mixer.Sound("resources/mixkit-short-laser-gun-shot-1670.wav")
    shot_sound_2 = pygame.mixer.Sound("resources/mixkit-fast-magic-game-spell-883.wav")
    shot_sound_3 = pygame.mixer.Sound("resources/fire-spell-100276.mp3")
    wall_sound = pygame.mixer.Sound("resources/mixkit-wood-hard-hit-2182.wav")
    break_magic_sound = pygame.mixer.Sound("resources/mixkit-glass-break-with-hammer-thud-759.wav")
    get_magic_sound = pygame.mixer.Sound("resources/sound-effect-twinklesparkle-115095.mp3")
    get_treasure_sound = pygame.mixer.Sound("resources/mixkit-arcade-bonus-229.wav")
    hit_beast_sound = pygame.mixer.Sound("resources/damage-40114.mp3") #metal-hit-84608.mp3
    miss_beast_sound = pygame.mixer.Sound("resources/soul-steal-02-43483.mp3")
    kill_beast_sound = pygame.mixer.Sound("resources/mixkit-enemy-death-voice-3168.wav")
    hit_bubba_sound = pygame.mixer.Sound("resources/metal-hit-84608.mp3")
    player_death_sound = pygame.mixer.Sound("resources/mixkit-enemy-death-voice-3168.wav") # better!

    dead_scale = 1.1
    dead_img = pygame.image.load(map_json['player_dead_img']).convert_alpha()
    dead_img = pygame.transform.scale(dead_img, (gs * dead_scale, gs * dead_scale))



    # hit monster
    # kill monster

    score = 0
    trapb = gs//4 # buffer for trap graphics

    # status bar
    bar_px = 200 # health, mana bar length
    txt_y = 10 # y margin
    gold_x = 45
    hp_x = 200
    mana_x = 475
    key_x = 770
    xp_x = 870
    weapon_x = 10
    status_bar_flag = True
    status_bar_y = 50
    
    done = False
    pcolor = convert_color("#009900")
    pcolor_inv = convert_color("#006600")
    grid_clr = convert_color("#404060")
    floor_clr = convert_color("#303060") 
    floor_clr2 = convert_color("#202040")  # secrets
    #dungeon_border_clr = convert_color("#0066dd")
    dungeon_border_clr = convert_color("#303050")
    water_clr = (0,128,255)
    water_clr2 = (0,128,255)
    lava_clr = (127, 104, 6)
    lava_clr2 = (254, 169, 72)
    door_clr = convert_color("#FFFFFF")
    trap_clr = (255,0,0)
    trap_inactive_clr = (90,99,90)

    lock_door_clr = convert_color("#FFFF44")
    shot_clr = convert_color("#22FF22")
    gold_clr = convert_color("#D4AF37")
    lightning_clr = convert_color("#EEFF1B")
    fire_clr = convert_color("#e25822")
    fire_clr2 = convert_color("#FFFF99")

    # status bar stuff
    status_clr = convert_color("#666699") 
    text_clr = (255,255,255)
    health_clr = convert_color("#bb0022") 
    mana_clr = convert_color("#2211bb")
    empty_clr = convert_color("#183018")
    border_clr = convert_color("#F0F0F0")



    bubba.weapon_clr_1 = shot_clr
    bubba.weapon_clr_2 = lightning_clr
    bubba.weapon_clr_3 = fire_clr

    shot_list = [] # from Bubba
    shot_list2 = [] # from monsters
    effect_list = []

    update_fog(bubba.xi, bubba.yi, dx, dy)
    bubba.hp = bubba.hp_max
    bubba.mana = bubba.mana_max

    t = 0 # clock ticks
    grid_flag = True
    invisible_flag = False
    
    # -----------------------------------------------[ loop ]
    
    while not done:
        
        t += 1
        bg.fill(background_color)
        
        for tele in teleport_list:
            if tele.active:
                if tele.pulse >= 255 or tele.pulse <= 0:
                    #tele.pulse = max(0, tele.pulse)
                    #tele.pulse = min(255, tele.pulse)
                    tele.pv = -1 * tele.pv
                    
                #print("t = {}, pv = {}".format(tele.pulse, tele.pv))
                tele.pulse += tele.pv

                if tele.pulse < 0:
                    tele.pulse = 0
                if tele.pulse > 255:
                    tele.pulse = 255
                #tele.pulse = max(0, tele.pulse)
                #tele.pulse = min(255, tele.pulse)
            else:
                # pause to reset teleporter
                tele.wait += 1
                if tele.wait >= tele.wait_max:
                    tele.active = True
                    tele.wait = 0

        for x in range(dx):
            for y in range(dy):    
                x0 = x * gs + xoff
                y0 = y * gs + yoff
                
                if x0 > screen_x or y0 > screen_y:
                    continue
                
                # fog of war
                if fog_flag:
                    if fog[x][y] == 0: # and fog_flag:
                        continue
                
                    

                if dungeon[x][y] == 1:
                    #pygame.draw.rect(bg, dclr, [x0, y0, gs-1, gs-1])
                    fc = floor_clr
                    if x == 0 or y == 0 or x == dx-1 or y == dy-1:
                        fc = dungeon_border_clr
                        
                    pygame.draw.rect(bg, fc, [x0, y0, gs, gs])
                elif dungeon[x][y] == 4:
                    fc = floor_clr
                    if bubba.vision:
                        fc = floor_clr2
                
                    pygame.draw.rect(bg, fc, [x0, y0, gs, gs])

                elif dungeon[x][y] == 5:
                    # water
                    # should "shimmer"
                    
                    pygame.draw.rect(bg, water_clr, [x0, y0, gs, gs])
                    for _ in range(random.randint(2,6)):
                        xwater = random.randint(2,gs-1)
                        ywater = random.randint(2,gs-1)
                        bg.set_at((int(x0 + xwater), int(y0 + ywater)), water_clr2)    
                                
                elif dungeon[x][y] == 6:
                    # lava
                    # should "shimmer"

                    pygame.draw.rect(bg, lava_clr, [x0, y0, gs, gs])   
                    for _ in range(random.randint(2,6)):
                        xlava = random.randint(2,gs-1)
                        ylava = random.randint(2,gs-1)
                        
                        bg.set_at((int(x0 + xlava), int(y0 + ylava)), lava_clr2)    
                                
                elif dungeon[x][y] == 2:
                    # vertical door
                    pygame.draw.rect(bg, door_clr, [x0 + gs//3, y0, gs // 3, gs])
                elif dungeon[x][y] == 3:
                    # horz door
                    # gs = 25 // 3
                    pygame.draw.rect(bg, door_clr, [x0, y0 + gs // 3, gs, gs // 3])

                elif dungeon[x][y] == 7:
                    # locked
                    pygame.draw.rect(bg, lock_door_clr, [x0 + gs//3, y0, gs // 3, gs])
                elif dungeon[x][y] == 8:
                    # locked
                    pygame.draw.rect(bg, lock_door_clr, [x0, y0 + gs // 3, gs, gs // 3])
                elif dungeon[x][y] == 25:
                    # teleporter
                                        
                    for tele in teleport_list:
                        if tele.x == x and tele.y == y:
                            if tele.active:
                                tc = tele.pulse
                                # yellow
                                tele_clr = (tc, tc, 0)
                                tele_clr2 = (255-tc, 255-tc, 0)

                                pygame.draw.circle(bg, tele_clr, (x0 + gs //2, y0 + gs //2), gs // 5, 0)
                                pygame.draw.circle(bg, tele_clr2, (x0 + gs //2, y0 + gs //2), gs // 7, 0)
                                pygame.draw.circle(bg, door_clr, (x0 + gs //2, y0 + gs //2), gs // 3, 2)
                            else:
                                # teleporter offline
                                pygame.draw.circle(bg, door_clr, (x0 + gs //2, y0 + gs //2), gs // 4, 2)


            if grid_flag:
                pygame.draw.lines(bg, grid_clr, False, [(x * gs + xoff, 0), (x*gs + xoff, screen_y)], 1)

        if grid_flag:
            for y in range(dy):
                if y*gs + yoff < screen_y:
                    pygame.draw.lines(bg, grid_clr, False, [(0, y*gs+yoff), (screen_x, y*gs+yoff)], 1)

        # draw gold
        for g in gold_list:
            # if bubba moved flag
            d = distance(bubba.x, bubba.y, g.x, g.y) 
            if d < treasure_dist:
                score += g.money
                #g_del_list.append(g)
                gold_list.remove(g)
                pygame.mixer.Sound.play(get_treasure_sound)
            else:   
                # fog of war
                if fog_flag:
                    if fog[g.xi][g.yi] == 0: 
                        continue

                if g.x+xoff < screen_x and g.y+yoff < screen_y:
                    pygame.draw.circle(bg, gold_clr, (g.x+xoff, g.y+yoff), 4, 0)    

        # traps
        for trap in trap_list:

            if fog_flag:
                if fog[trap.xi][trap.yi] == 0:
                    continue

            if trap.x + xoff < screen_x and trap.y + yoff < screen_y:
                if trap.active:

                    d = distance(bubba.x, bubba.y, trap.x, trap.y)
                    #print("trap: {}, d: {:.2f}".format(trap.id, d))
                    if d < 15:
                        print("trap triggered: {}, damage = {}".format(trap.id, trap.dmg))
                        trap.active = False
                        # play sound - should be from config
                        pygame.mixer.Sound.play(shot_sound_3)
                        
                        bubba.hp = bubba.hp - trap.dmg
                        # special actions - blocks a door or something somehow with other attr?
                        #if trap.id == "wall":
                        #    pass
                        # speed
                        # not invisible

                        effect = Player(0, trap.x, trap.y)
                        effect.gs = gs
                        effect.id = trap.id
                        effect.time = trap.time

                        effect_list.append(effect)
                        #trap_list.remove(s)
                    else:

                        if bubba.vision:
                            xx = trap.x+xoff-trapb
                            yy = trap.y+yoff-trapb
                            pygame.draw.polygon(bg, trap_clr, [[xx, yy], [xx+gs//2, yy], [xx, yy+gs//2], [xx+gs//2,yy+gs//2], [xx,yy], [xx,yy+gs//2],[xx+gs//2,yy+gs//2], [xx+gs//2,yy]],3)

                else:
                    xx = trap.x+xoff-trapb
                    yy = trap.y+yoff-trapb
                    pygame.draw.polygon(bg, trap_inactive_clr, [[xx, yy], [xx+gs//2, yy], [xx, yy+gs//2], [xx+gs//2,yy+gs//2], [xx,yy], [xx,yy+gs//2],[xx+gs//2,yy+gs//2], [xx+gs//2,yy]],3)


        # draw treasure
        for trs in t_list:

            if fog_flag:
                if fog[trs.xi][trs.yi] == 0:
                    continue


            if trs.x + xoff < screen_x and trs.y + yoff < screen_y:

                d = distance(bubba.x, bubba.y, trs.x, trs.y) 

                if d < treasure_dist:
                    score += trs.value
                    # special properties?
                    if trs.special:
                        
                        if trs.special == "mana":
                            bubba.mana = bubba.mana_max
                        elif trs.special == "heal":
                            bubba.hp = bubba.hp_max
                        elif trs.special == "fog":
                            fog_flag = False
                        elif trs.special == "key":
                            bubba.key_cnt += 1
                        elif trs.special == "mana_increase":
                            bubba.mana_max = bubba.mana_max * 1.5
                            
                        elif trs.special == "hp_increase":
                            bubba.hp_max = bubba.hp_max * 1.5
                            bubba.hp = bubba.hp_max
                        elif trs.special == "speed_increase":
                            bubba.v = bubba.v * 1.5
                            bubba.v = min(bubba.v, 20) # limit to 20?
                        elif trs.special == "damage":
                            bubba.dmg_bonus = 1.25
                        
                        else:
                            # add attribute
                            setattr(bubba, trs.special, True)
                            print("added power: {}".format(trs.special))    
                            print("flag: {}".format(getattr(bubba, trs.special)))

                        if trs.text:                        
                            effect = Player(0, 0, 0)
                            effect.id = "text"
                            effect.text = trs.text
                            effect.time = effect.time_max = 30
                            effect_list.append(effect)


                        pygame.mixer.Sound.play(get_magic_sound)
                    else:
                        pygame.mixer.Sound.play(get_treasure_sound)
                    t_list.remove(trs)
                    
                #pygame.draw.circle(bg, gold_clr, (trs.x+xoff , trs.y+yoff ), trs.size*gs//2, 1)  
                # +5 seems to center better   
                bg.blit(trs.img, (trs.x+xoff - gs//2 + 5, trs.y+yoff - gs//2 + 5))            
                #pygame.draw.circle(bg, gold_clr, (trs.x+xoff , trs.y+yoff ), 5, 0)    

        # draw player - big circle with an eye, I guess
        # ------------------------------------------------------
        if bubba.alive:
            if invisible_flag:
                pygame.draw.circle(bg, pcolor_inv, (bubba.x + xoff, bubba.y + yoff), bubba.size, 0)
            else:
                pygame.draw.circle(bg, pcolor, (bubba.x + xoff, bubba.y + yoff), bubba.size, 0)
            pygame.draw.circle(bg, (255,255,255), (bubba.x0 + xoff, bubba.y0 + yoff), bubba.size * 0.5, 0)
            pygame.draw.circle(bg, (3,3,3), (bubba.x0 + xoff, bubba.y0 + yoff), bubba.size * 0.3, 0) # 0.4 too dilated
        else:
            bg.blit(dead_img, (bubba.x + xoff - gs//2, bubba.y + yoff- gs//2))
        #pygame.draw.lines(bg, pcolor, False, ((bubba.x+xoff, bubba.y+yoff), (bubba.x0+xoff, bubba.y0+yoff)), 2)

        # drain mana if over water
        if dungeon[bubba.xi][bubba.yi] == 5:
            if t % 5 == 0:
                if bubba.mana > 1:
                    bubba.mana = bubba.mana - 1 
            # ugh

        # drain mana if over water
        if dungeon[bubba.xi][bubba.yi] == 6:
            if t % 10 == 0:
                if bubba.hp > 1:
                    bubba.hp = bubba.hp - 1 
            # ouch

        if invisible_flag:
            if t % 10 == 0:
                if bubba.mana > 1:
                    bubba.mana -= 2
                else:
                    invisible_flag = False

        # draw monsters/beasts
        for b in b_list:

            if fog_flag:
                if fog[b.xi][b.yi] == 0:
                    continue

            
            if b.x+xoff < screen_x and b.y + yoff < screen_y:
                # move towards bubba if bubba in range
                b.action()
                d = distance(bubba.x, bubba.y, b.x, b.y) 
                if not bubba.alive:
                    d = 1000 

                if d < b.attack_distance and not invisible_flag:
                    # how often, what is actual distance, can they shoot at player
                    #print(f"{b.id} can attack")
                    if bubba.alive:
                        # swing, dmg affected by bubba's armor dmg = dmg * (1-armor)
                        if b.weapon in ("arrow", "lightning", "fireball", "rock", "acid"):
                            # fire ranged shot at roughly where player is
                            # angle = hmmm
                            # t % 20 can change per weapon/beast
                            if t % b.attack_time == 0:
                                a = math.atan((b.x - bubba.x) / (b.y - bubba.y))
                                #a = 90
                                # bubba above then a = a + 180
                                if bubba.y < b.y:
                                    a = a + math.pi
                                #print("- angle: {:.2f}".format(math.degrees(a)))
                                shot = Player(math.degrees(a), b.x, b.y)
                                # shot sound
                                shot.v = 8

                                if b.weapon == "arrow":
                                    pygame.mixer.Sound.play(shot_sound_1)
                                    shot.v = 12
                                elif b.weapon == "rock":
                                    pygame.mixer.Sound.play(shot_sound_1)
                                    shot.v = 8

                                elif b.weapon == "acid":
                                    pygame.mixer.Sound.play(shot_sound_1)
                                    shot.v = 6
                                elif b.weapon == "lightning":
                                    pygame.mixer.Sound.play(shot_sound_2)
                                    shot.v = 25
                                elif b.weapon == "fireball":
                                    pygame.mixer.Sound.play(shot_sound_3)
                                    shot.v = 20

                                shot.gs = gs
                                
                                shot.time = 10
                                shot.water = True
                                shot.lava = True
                                shot.id = b.weapon
                                shot.src = b.id
                                shot.dmg = b.dmg
                                shot.x0  = b.x
                                shot.y0 = b.y
                                shot_list2.append(shot)
                        else:
                            # swing at bubba
                            if t % b.attack_time == 0:
                                if bubba.alive:
                                    # hit? damage based on armor of bubba
                                    # should be a range set in config
                                    dmg = random.randint(1, b.dmg) 
                                    print(f"{b.id} damages Bubba for {dmg} hp")
                                    bubba.hp = bubba.hp - dmg
                        
                                    pygame.mixer.Sound.play(hit_bubba_sound)


                
                if d < b.target_distance:
                    # update with bubba's new location
                    
                    if not invisible_flag and bubba.alive:
                        # if less than 20% of b.hp then flee away
                        b.set_target(bubba.x, bubba.y)


                #pygame.draw.circle(bg, gold_clr, (b.x+xoff , b.y+yoff ), b.attack_distance, 1)    
                #pygame.draw.circle(bg, gold_clr, (b.x+xoff, b.y+yoff), b.target_distance, 1)    
                if b.special == "invisible" and not bubba.vision:
                    pass
                    #pygame.draw.circle(bg, gold_clr, (b.x+xoff, b.y+yoff), b.size * gs/2, 1)    
                else:
                    bg.blit(b.img, (b.x+xoff - gs//2+b.img_pad, b.y+yoff - gs//2 + b.img_pad))
                #pygame.draw.circle(bg, gold_clr, (b.x+xoff, b.y+yoff), b.size * gs/2, 1)    

        # draw magic from the player
        for s in shot_list:
            do_effect_flag = False
            mf, xx, yy = s.move("w") # mf = move flag
            if dungeon[xx][yy] in (2,3,4):
                # open a door or secret passage
                dungeon[xx][yy] = 0
                do_effect_flag = True

                mf = False
            
            if mf:
                if bubba.weapon == 1:
                    pygame.draw.circle(bg, shot_clr, (s.x+xoff, s.y+yoff), 3, 0)
                elif bubba.weapon == 2:
                    pygame.draw.circle(bg, lightning_clr, (s.x+xoff, s.y+yoff), 3, 0)
                    pygame.draw.lines(bg, lightning_clr, False, ((s.x0+xoff, s.y0+yoff), (s.x+xoff, s.y+yoff)), 5)
                    pygame.draw.lines(bg, (255,255,255), False, ((s.x0+xoff, s.y0+yoff), (s.x+xoff, s.y+yoff)), 1)
                    s.x0 = s.x
                    s.y0 = s.y
                elif bubba.weapon == 3:
                    for _ in range(4):
                        ex = s.x + (gs - random.random() * gs * 1.5)
                        ey = s.y + (gs - random.random() * gs * 1.5)
                        pygame.draw.lines(bg, fire_clr, False, ((s.x+xoff,s.y+yoff), (ex+xoff, ey+yoff)), 2)

                    pygame.draw.circle(bg, fire_clr, (s.x+xoff, s.y+yoff), 8, 0)
                    pygame.draw.circle(bg, fire_clr2, (s.x+xoff, s.y+yoff), 4, 0)

                # did we hit a treasure
                for trs in t_list:
                    d = distance(s.x, s.y, trs.x, trs.y)
                    if d < gs:
                        #t_del_list.append(trs)
                        t_list.remove(trs)
                        do_effect_flag = True
                        #play break_magic_sound
                        pygame.mixer.Sound.play(break_magic_sound)
                # did we hit a beast
                for b in b_list:
                    d = distance(s.x, s.y, b.x, b.y) 
                    #print("d: {:.2f}, s:{:.2f},{:.2f}, b: {}, {},{}".format(d, s.x, s.y, b.bname, b.x, b.y))
                    dmg = 0
                    if d < beast_hit_range:
                        # hit animation
                        # depends on shot id
                        do_effect_flag = True

                        # or b takes damage, is b dead?
                        # to do - make weapon data a list
                        
                        if bubba.spell_type == b.immune:
                            print(f"{b.id} immune to {b.immune}")
                        else:
                            if bubba.weapon == 1:
                                dmg = random.randint(bubba.weapon_dmg_1[0], bubba.weapon_dmg_1[1]) 
                            elif bubba.weapon == 2:
                                dmg = random.randint(bubba.weapon_dmg_2[0], bubba.weapon_dmg_2[1]) 
                            elif bubba.weapon == 3:
                                dmg = random.randint(bubba.weapon_dmg_3[0], bubba.weapon_dmg_3[1]) 
                            dmg = dmg * bubba.dmg_bonus

                        b.hp = b.hp - dmg * (1 - b.armor_bonus)
                        
                        print("hit {} ({}) for {:.1f} damage, {} hp remain".format(b.id, b.type, dmg, b.hp))

                        if b.hp <= 0:
                            #b_del_list.append(b)
                            
                            b_list.remove(b)
                            bubba.xp = bubba.xp + beast.xp
                            print(f"killed: {b.id} ({b.type})")

                            effect = Player(0, 0, 0)
                            effect.id = "text"
                            effect.text = "You killed {} ({})".format(b.id, b.type)
                            effect.time = 30
                            effect_list.append(effect)

                            pygame.mixer.Sound.play(kill_beast_sound)
                            # drop treasure or other bonus
                            if b.money > 0:
                                gold = Player(0, b.x, b.y)
                                gold.v = 0
                                gold.money = b.money
                                gold.gs = gs
                                gold_list.append(gold)
                        else:
                            if dmg > 0:
                                pygame.mixer.Sound.play(hit_beast_sound)
                            else:
                                # no effect
                                pygame.mixer.Sound.play(miss_beast_sound)

            else:
                do_effect_flag = True
                pygame.mixer.Sound.play(wall_sound)

            if do_effect_flag:
                # effect from shot
                effect = Player(0, s.x, s.y)
                effect.gs = gs
                effect.id = s.id
                effect.time = s.time
                effect_list.append(effect)
                shot_list.remove(s)


        # from monsters
        for s in shot_list2:
            do_effect_flag = False
            mf, xx, yy = s.move("w") # mf = move flag
            if dungeon[xx][yy] in (2,3,4):
                # open a door or secret passage
                dungeon[xx][yy] = 0
                do_effect_flag = True

                mf = False

            if mf:
                if s.id == "rock":
                    pygame.draw.circle(bg, (255,255,255), (s.x+xoff, s.y+yoff), 4, 0)
                if s.id == "arrow":
                    pygame.draw.circle(bg, (192, 192, 192), (s.x+xoff, s.y+yoff), 3, 0)
                    pygame.draw.lines(bg, (192, 192, 192), False, ((s.x0+xoff, s.y0+yoff), (s.x+xoff, s.y+yoff)), 5)
                    s.x0 = s.x
                    s.y0 = s.y                    
                if s.id == "lightning":
                    pygame.draw.circle(bg, lightning_clr, (s.x+xoff, s.y+yoff), 3, 0)
                    pygame.draw.lines(bg, lightning_clr, False, ((s.x0+xoff, s.y0+yoff), (s.x+xoff, s.y+yoff)), 5)
                    pygame.draw.lines(bg, (255,255,255), False, ((s.x0+xoff, s.y0+yoff), (s.x+xoff, s.y+yoff)), 1)
                    s.x0 = s.x
                    s.y0 = s.y
                if s.id == "fireball":
                    for _ in range(4):
                        ex = s.x + (gs - random.random() * gs * 1.5)
                        ey = s.y + (gs - random.random() * gs * 1.5)
                        pygame.draw.lines(bg, fire_clr, False, ((s.x+xoff,s.y+yoff), (ex+xoff, ey+yoff)), 2)

                    pygame.draw.circle(bg, fire_clr, (s.x+xoff, s.y+yoff), 8, 0)
                    pygame.draw.circle(bg, fire_clr2, (s.x+xoff, s.y+yoff), 4, 0)

                if s.id == "acid":
                    pygame.draw.circle(bg, shot_clr, (s.x+xoff, s.y+yoff), 3, 0)

                d = distance(s.x, s.y, bubba.x, bubba.y) 
                if d < 20:
                    # how big is bubba?
                    print(f"Bubba hit for {s.dmg} damage")
                    bubba.hp = bubba.hp - s.dmg
                    #shot_list2.remove(s)
                    do_effect_flag = True
                    
                    pygame.mixer.Sound.play(hit_bubba_sound)
            else:
                pygame.mixer.Sound.play(wall_sound)
                do_effect_flag = True

            if do_effect_flag:
                # effect from shot
                effect = Player(0, s.x, s.y)
                effect.gs = gs
                effect.id = s.id
                effect.time = s.time
                effect_list.append(effect)
                shot_list2.remove(s)



        txt_cnt = 0
        for e in effect_list:
            if e.time > 0:
                e.time = e.time - 1
                if e.id == "fire_trap":
                    for _ in range(random.choice([2,5])):
                        xtr = random.randint(-gs//2, gs//2)
                        ytr = random.randint(-gs//2, gs//2)
                        

                        pygame.draw.circle(bg, fire_clr, (e.x +xoff+xtr, e.y+yoff+ytr), random.choice([3,15]), 0)
                if e.id == "ice_trap":
                    for _ in range(10):
                        xtr = random.randint(-gs//2, gs//2)
                        ytr = random.randint(-gs//2, gs//2)
                        # ex2 = ex + (es - random.random() * es * 2)
                        # ey2 = ey + (es - random.random() * es * 2)

                        pygame.draw.lines(bg, (128,255,255), False, ((e.x+xoff,e.y+yoff),(e.x+xoff+xtr,e.y+yoff+ytr)), 3)

                if e.id in ("arrow", "rock"):
                    pygame.draw.circle(bg, (255,255,255), (e.x+xoff, e.y+yoff), e.time+1, 0)
                if e.id in ("green", "acid"):
                    pygame.draw.circle(bg, shot_clr, (e.x+xoff, e.y+yoff), e.time+3, 0)
                if e.id in ("fire", "fireball"):
                    pygame.draw.circle(bg, fire_clr, (e.x+xoff, e.y+yoff), e.time+3, 0)
                if e.id == "lightning":
                    # explosion - shrinks
                    ex = e.x + xoff
                    ey = e.y + yoff
                    es = gs * e.time/10  # 0.8

                    for _ in range(random.choice([3,6])):
                        # random color or choice
                        #lt = random.randint(0, 128)
                        #lclr = (255-lt, 128, 0 + lt)
                        lclr = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                        
                        ex2 = ex + (es - random.random() * es * 2)
                        ey2 = ey + (es - random.random() * es * 2)
                        
                        pygame.draw.lines(bg, lclr, False, ((ex,ey), (ex2, ey2)), 2)
                    """
                    for _ in range(random.choice([2,4])):
                        lclr = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                        
                        ex2 = int(ex + (es - random.random() * es * 2))
                        ey2 = int(ey + (es - random.random() * es * 2))
                        bg.set_at((ex2,ey2), lclr) # int only
                    """

                if e.id == "text":
                    # how many do we have
                    txt_cnt += 1
                    # don't need to always render it unless its fading

                    #pause_pos = (int(screen_bottom_right_px[0] / 2), int(screen_bottom_right_px[1]/2))
                    #pause_text = status_font.render("Paused", 1, text_color)
                    #text_xy = pause_text.get_rect(center=pause_pos)
                    #print(e.text)
                    txt = game_font.render(e.text, 1, text_clr)
                    txt2 = game_font.render(e.text, 1, (0,0,0))
                    txt_xy = txt.get_rect(center=(screen_x // 2, 25 * txt_cnt))
                    #txt_xy = txt.get_rect(center=txt_xy)
                    bg.blit(txt2, (txt_xy[0]+2,txt_xy[1]+2))
                    bg.blit(txt, txt_xy)

                                   

            else:
                effect_list.remove(e)

            

        # bottom status bar
        # if something changed, else use bitcopy

        if status_bar_flag:
            
            pygame.draw.rect(bg, status_clr, [0, screen_y, screen_x, screen_y + status_bar_y])

            gold_text = game_font.render(f"Gold: {score}", 1, text_clr)
            txt_xy = gold_text.get_rect(topleft=(gold_x, screen_y+txt_y)) 
            bg.blit(gold_text, txt_xy) 

        
            hp_text = game_font.render("HP:", 1, text_clr)
            txt_xy = hp_text.get_rect(topleft=(hp_x, screen_y+txt_y))
            bg.blit(hp_text, txt_xy) 

        
            h0 = bar_px * (max(0, bubba.hp) / bubba.hp_max)
            h1 = bar_px * (1 - max(bubba.hp,0) / bubba.hp_max)
            pygame.draw.rect(bg, health_clr, [15 + txt_xy[0] + txt_xy[2], txt_xy[1], h0, txt_xy[3]])
            pygame.draw.rect(bg, empty_clr, [15 + txt_xy[0] + txt_xy[2] + h0, txt_xy[1], h1, txt_xy[3]])
            pygame.draw.rect(bg, border_clr, [15 + txt_xy[0] + txt_xy[2], txt_xy[1], bar_px, txt_xy[3]], 2)

        
            mana_text = game_font.render("Mana:", 1, text_clr)
            txt_xy = mana_text.get_rect(topleft=(mana_x, screen_y+10))
            bg.blit(mana_text, txt_xy) 
            #mana_text = game_font.render(f"{bubba.mana} / {bubba.mana_max}", 1, (255,255,255,100))
            #txt_xy = mana_text.get_rect(center=(500+15+200, screen_y + 10))
            m0 = bar_px * (max(bubba.mana,0) / bubba.mana_max)
            m1 = bar_px * (1 - max(bubba.mana,0) / bubba.mana_max)
            pygame.draw.rect(bg, mana_clr, [15 + txt_xy[0] + txt_xy[2], txt_xy[1], m0, txt_xy[3]])
            pygame.draw.rect(bg, empty_clr, [15 + txt_xy[0] + txt_xy[2] + m0, txt_xy[1], m1, txt_xy[3]])
            pygame.draw.rect(bg, border_clr, [15 + txt_xy[0] + txt_xy[2], txt_xy[1], bar_px, txt_xy[3]], 2)
            # add 16/25 ?
            #pygame.draw.rect(bg, (0,0,0), [txt_xy[0], txt_xy[1], txt_xy[2], txt_xy[3]])
            #bg.blit(mana_text, txt_xy)                                  
            #pygame.draw.rect(bg, (0,0,0), [15 + bubba.e_max + txt_xy[0] + txt_xy[2], txt_xy[1], bubba.mana_max - bubba.mana - e1, txt_xy[3]])

            # key count    
            key_text = game_font.render(f"Keys: {bubba.key_cnt}", 1, text_clr)
            txt_xy = key_text.get_rect(topleft=(key_x, screen_y+txt_y))
            bg.blit(key_text, txt_xy)
            
            xp_text = game_font.render(f"XP: {bubba.xp}", 1, text_clr)
            txt_xy = xp_text.get_rect(topleft=(xp_x, screen_y+txt_y))
            bg.blit(xp_text, txt_xy)

            # weapon color
            
            w_clr = (0,0,0)
            if bubba.weapon == 1:
                w_clr = bubba.weapon_clr_1
            elif bubba.weapon == 2:

                w_clr = bubba.weapon_clr_2
            elif bubba.weapon == 3:
                w_clr = bubba.weapon_clr_3

            pygame.draw.rect(bg, border_clr, [weapon_x-1, screen_y+9, 22, 22])
            pygame.draw.rect(bg, w_clr, [weapon_x, screen_y+10, 20, 20])
            
            

        if yoff > 0 and xoff < 400:
            title_str = "{} - {}".format(map_json.get("game_name", "Bubba the Beholder"), map_json.get("author", "The Dude"))
            title_text = game_font.render(title_str, 1, text_clr)
            #txt_xy = hp_text.get_rect(topleft=(hp_x, screen_y+txt_y))
            bg.blit(title_text, (xoff, yoff-50)) 
            #bg.blit(trs.img, (trs.x+xoff - gs//2, trs.y+yoff - gs//2))    

        screen.blit(bg, (0, 0))
        pygame.display.flip()

        clock.tick(clock_tick) 

        # is Bubba alive
        if bubba.hp <= 0 and bubba.alive:
            pygame.mixer.Sound.play(player_death_sound)
            effect = Player(0, 0, 0)
            effect.id = "text"
            effect.text = "Bubba has died"
            effect.time = effect.time_max = 90
            effect_list.append(effect)
            bubba.alive = False
            # game over

        # actions ---------------------------------

        moved_flag = False
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONUP:
                if bubba.alive:
                    if event.button == 1:
                        invsible_flag = False # standard practice?
                        #print("bubba angle: {:.1f}".format(bubba.a))
                        if bubba.weapon == 1 and bubba.mana > bubba.mana_weapon_1:
                            shot = Player(bubba.a, bubba.x, bubba.y)
                            shot.v = 5 + bubba.v
                            shot.gs = gs
                            shot.time = 10 # 10 frame animation
                            shot.water = True
                            shot.lava = False
                            shot.id = "green"
                            shot_list.append(shot)
                            # shot sound
                            pygame.mixer.Sound.play(shot_sound_1)
                            bubba.mana = bubba.mana - bubba.mana_weapon_1
                        elif bubba.weapon == 2 and bubba.mana > bubba.mana_weapon_2:
                            shot = Player(bubba.a, bubba.x, bubba.y)
                            shot.x0 = bubba.x
                            shot.y0 = bubba.y
                            shot.v = 25
                            shot.gs = gs
                            shot.time = 10 # 10 frame animation
                            shot.water = False
                            shot.lava = True
                            # why these get stuck???
                            shot.id = "lightning"
                            shot_list.append(shot)
                            pygame.mixer.Sound.play(shot_sound_2)
                            # shot sound
                            bubba.mana = bubba.mana - bubba.mana_weapon_2
                        elif bubba.weapon == 3 and bubba.mana > bubba.mana_weapon_3:
                            shot = Player(bubba.a, bubba.x, bubba.y)
                            shot.x0 = bubba.x
                            shot.y0 = bubba.y
                            shot.v = 20
                            shot.gs = gs
                            shot.time = 12 # 10 frame animation
                            shot.water = False
                            shot.lava = True
                            # why these get stuck???
                            shot.id = "fire"
                            shot_list.append(shot)
                            #bubba.mana = bubba.mana - bubba.mana_weapon_3
                            pygame.mixer.Sound.play(shot_sound_3)

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    done = True            
                
                # scaling - need to move all the beasts also
                if event.key == K_PLUS or event.key == K_EQUALS:
                    if gs < 55:
                        gs = gs + 5
                        # need to re-set everyone's scale
                if event.key == K_MINUS or event.key == K_UNDERSCORE:
                    if gs >= 15:
                        gs = gs - 5

                if event.key == K_1:
                    bubba.weapon = 1
                    bubba.spell_type = bubba.weapon_type_1
                if event.key == K_2:
                    # if we have it
                    if bubba.lightning:
                        bubba.weapon = 2
                        bubba.spell_type = bubba.weapon_type_2
                if event.key == K_3:
                    if bubba.fireball:
                        bubba.weapon = 3
                        bubba.spell_type = bubba.weapon_type_3

                if event.key == K_i:
                    
                    if bubba.invisible and bubba.hp > 0:
                        invisible_flag = not invisible_flag

                # cheats
                if event.key == K_h:
                    # cost gold
                    if score > 25:
                        score -= 25
                        bubba.hp = min(bubba.hp + 10, bubba.hp_max)
                        # ressurect
                        if bubba.hp > 0 and not bubba.alive:
                            bubba.alive = True
                if event.key == K_m:
                    if score > 25:
                        score -= 25
                        bubba.mana = min(bubba.mana + 5, bubba.mana_max)
                if event.key == K_f:
                    fog_flag = not fog_flag

            if event.type == pygame.MOUSEMOTION:

                mm = [event.pos[0] - m[0], event.pos[1] - m[1]]
                bubba.turn(mm[0])

            pygame.mouse.set_pos(m)    

        
        keypress = pygame.key.get_pressed()
        if keypress[pygame.K_w]:
            bubba.move("w")
            
            if bubba.x + xoff > screen_x * 0.8:
                xoff -= bubba.v
            if bubba.x + xoff < screen_x * 0.2:
                xoff += bubba.v
            if bubba.y + yoff > screen_y * 0.8:
                yoff -= bubba.v
            if bubba.y + yoff < screen_y * 0.2:
                yoff += bubba.v

            update_fog(bubba.xi, bubba.yi, dx, dy)

            moved_flag = True

        if keypress[pygame.K_s]:
            bubba.move("s")
            # backwards xoff, yoff also
            moved_flag = True

        if keypress[pygame.K_d]:
            bubba.move("d")
            moved_flag = True
        if keypress[pygame.K_a]:
            bubba.move("a")
            moved_flag = True

        if keypress[pygame.K_e]:
            
            xx0 = yy0 = 0
            if bubba.alive:
            
                if 65.0 < bubba.a < 115.0:
                    xx0 = 1
                if 245.0 < bubba.a < 295.0:
                    xx0 = -1            
                if 155.0 < bubba.a < 205.0:
                    yy0 = -1    
                if 335.0 < bubba.a < 360.0:
                    yy0 = 1
                if 0.0 <= bubba.a < 25.0:
                    yy0 = 1

            if xx0 != 0 or yy0 != 0:

                if dungeon[bubba.xi + xx0][bubba.yi + yy0] in (2,3):
                    dungeon[bubba.xi + xx0][bubba.yi + yy0] = 0
                # 7,8 = locked door
                if dungeon[bubba.lastx + xx0][bubba.lasty + yy0] in (7,8):
                    if bubba.key_cnt > 0:
                        bubba.key_cnt -= 1
                        dungeon[bubba.xi + xx0][bubba.yi + yy0] = 0
                    else:
                        print("Bubba needs a key")

        if keypress[pygame.K_UP]: 
            if yoff < 350:
                yoff += 25
        if keypress[pygame.K_DOWN]: 
            if yoff > 400 - gs * dy:
                yoff -= 25

        if keypress[pygame.K_LEFT]: 
            if xoff < 400:
                xoff += 25
            
        if keypress[pygame.K_RIGHT]: 
            # gs * 100 = 2500
            if xoff > 500 - gs * dx:
                xoff -= 25



        if moved_flag:
            moved_flag = False          
            if dungeon[bubba.xi][bubba.yi] == 25:
              
                tele_list = []
                for tele in teleport_list:
                    if tele.x == bubba.xi and tele.y == bubba.yi:
                        #print("teleporter: {}".format(tele.id))
                        if tele.active:
                            tele.active = False
                    else:
                        # add to list of random spots to teleport to
                        if tele.active:
                            tele_list.append(tele)

                if tele_list:
                    t_new = random.choice(tele_list)
                    #print("- new: {}".format(t_new.id)) 
                    bubba.x = t_new.x * gs
                    bubba.y = t_new.y * gs
                    xoff = -gs * t_new.x + screen_x // 2
                    yoff = -gs * t_new.y + screen_y // 2
                    bubba.xi = t_new.x
                    bubba.yi = t_new.y
                    t_new.active = False # reset this one too
                    
                    update_fog(bubba.xi, bubba.yi, dx, dy)
                    
                    pygame.mixer.Sound.play(teleport_sound)

        else:
            if bubba.mana <= bubba.mana_max:
                bubba.mana += bubba.mana_rate



def dungeon_wall(x, y, **kwargs):
    """is there a wall/door/thing here"""
    d_flag = True # there is an obsticle
    water_flag = kwargs.get("water", False) # pass over water
    lava_flag = kwargs.get("lava", False) # pass over lava

    # need to fix - prevent index out of range
    x = min(x, 99)
    y = min(y, 49)
    
    if dungeon[x][y] == 0 or dungeon[x][y] >= 20:
        d_flag = False
    if water_flag and dungeon[x][y] == 5:
        d_flag = False
    if lava_flag and dungeon[x][y] == 6:
        d_flag = False


    return d_flag

def update_fog(x, y, max_x, max_y):

    f = 7
    x0 = x - f
    x1 = x + f
    y0 = y - f
    y1 = y + f

    x0 = max(0, x0)
    x1 = min(x1, max_x)
    y0 = max(0, y0)
    y1 = min(y1, max_y)

    #print("fog - x{}: {} to {}, y{}: {} to {}".format(x, x0, x1, y, y0, y1))

    
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            fog[xx][yy] = 5
            #print(xx, yy, fog[xx][yy])
    

if __name__ == '__main__':

    print("[ Bubba the Beholder ]".center(60, "-"))
    # reduce error traceback
    #sys.tracebacklimit = 0

    # load dungeon function, return dungeon

    
    
    # read in config
    # - dungeon size, file
    # - monsters
    # - traps
    # - stuff

    # load monsters
    map_file = "test-map.yaml"
    map_json = {}
    with open(map_file, "r", encoding="utf-8") as fh:
        try:
            map_json = yaml.load(fh, Loader=yaml.FullLoader)
        except yaml.scanner.ScannerError as err: 
            print("Map file error: {}".format(err))
            sys.exit(1)

    print("map: {}, size: {} ".format(map_json['map'], map_json['map_size']))
  



    dx,dy = map_json['map_size']

    for x in range(dx):
        d = []
        for y in range(dy):
            d.append(0)
        dungeon.append(d)
        # fog.append links dungeon list to fog list

    for x in range(dx):
        d = []
        for y in range(dy):
            d.append(0)
        fog.append(d)

    #print("-" * 100)
    d = map_json['map']
    with open(d, "r") as fh:
        y = 0
        for line in fh:

            
            if not line:
                continue

            x = 0
            dr = []
            for c in line[:dx].strip():
                #fow[x][y] = 0
                #print(c, end="")
                if c == " ":
                    #dr.append(1)
                    dungeon[x][y] = 0
                elif c == "#":
                    dungeon[x][y] = 1
                elif c == "|":
                    dungeon[x][y] = 2
                elif c == "-":
                    dungeon[x][y] = 3
                elif c == "%":
                    dungeon[x][y] = 4
                elif c == ".":
                    dungeon[x][y] = 5

                elif c == ",":
                    dungeon[x][y] = 6

                elif c == "!":
                    # locked door
                    dungeon[x][y] = 7
                elif c == "=":
                    dungeon[x][y] = 8

                # things that can be "walked over"
                #elif c == "@":
                #    # teleport
                #    dungeon[x][y] = 25
                

                else:
                    dungeon[x][y] = ord(c) # ascii 32 -> 
                #else:
                #    # "#"
                #    #dr.append(0)
                #    dungeon[x][y] = 1
                x += 1

            #print()        
            y += 1
            if y > dy:
                continue
    
    # add borders - do this better
    for y in range(dy):
        for x in range(dx):
            if y == 0 or x == 0:
                dungeon[x][y] = 1
            if y == dy -1 or x == dx - 1:
                dungeon[x][y] = 1
            #print(dungeon[x][y], end="")
            #print(fog[x][y], end="")
        #print()


    # full screen option
    screen, screen_x, screen_y = init_screen()

    #main(screen, screen_x, screen_y, dx, dy)
    #pygame.quit()
    
    #sys.exit(0)

    play_flag = True
    while play_flag:

        play_flag = intro(screen, screen_x, screen_y)
        if  play_flag:
            main(screen, screen_x, screen_y, dx, dy)

    

    pygame.quit()
    
    sys.exit(0)

