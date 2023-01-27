from typing import List
from random import choice
# from time import sleep

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT
from pygame.locals import *
from pygame import mixer
import math

clock = pygame.time.Clock()
FPS = 60

# philips game functions
def get_dist(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1/2)

# returm abs value for going left and right (negative or pos)
def sign(x):
    return x / abs(x)

# Ian Titor gave template
def boss_ai(boss_move, boss_x, fighter_x, boss_speed, fighter_speed):
    boss_move = boss_move * 0.9 + (fighter_x - boss_x) * 0.1
    boss_x += sign(boss_move) * min(abs(boss_move), boss_speed)
    if boss_speed < fighter_speed:
        boss_speed += 1
    return boss_move, boss_x, boss_speed

# sprite frames
def get_sprite_frames(sprite_sheet, sprite_frame_size):

    sprite_sheet_width, sprite_sheet_height = sprite_sheet.get_size()
    sprite_frame_width, sprite_frame_height = sprite_frame_size

    sprite_rows = int(sprite_sheet_height / sprite_frame_height)
    sprite_cols = int(sprite_sheet_width / sprite_frame_width)

    sprite_frames = []

    for row in range(sprite_rows):
        for col in range(sprite_cols):
            section = (col * sprite_frame_height, row * sprite_frame_width, sprite_frame_width, sprite_frame_height)
            sprite_frame = sprite_sheet.subsurface(section)
            sprite_frames.append(sprite_frame)

    return sprite_frames


class ScreenInterface:

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        ...

    def update(self) -> None:
        ...

    def draw(self, surface: pygame.Surface) -> None:
        ...


#================================================================================================


class PauseScreen:

    def __init__(self, parent: ScreenInterface):
        self.parent = parent
        self.base_font = pygame.font.Font(None, 100)
        self.base_font2 = pygame.font.Font(None, 70)
        self.text_surface = self.base_font.render('PAUSED', True, (100, 100, 100))
        self.text_surface2 = self.base_font2.render('P TO CONTINUE', True, (100, 100, 100))

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    Game.set_screen(self.parent)

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self.parent.draw(surface)

        background = pygame.Surface((Game.WIDTH, Game.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(background, (0, 0, 0, 128),
                         (0, 0, Game.WIDTH, Game.HEIGHT))

        surface.blit(background, (0, 0))
        surface.blit(self.text_surface, (820, 500)) 
        surface.blit(self.text_surface2, (770, 650)) 

#================================================================================================


class Level_1:
        
    def __init__(self) -> None:
        #  sprites and background
        self.background = pygame.image.load('assets/battle_background.jpg')
        self.background = pygame.transform.scale(self.background, (1920, 1080))
        # <a href="https://www.freepik.com/free-vector/ancient-architecture-with-arches-torches_22444977.htm#query=dungeon%20background&position=0&from_view=keyword">Image by upklyak</a> on Freepik

        #sprite sheets
        fighter_sprite_sheet = pygame.image.load('assets/fighter.png')
        # LuizMelo
        boss_sprite_sheet = pygame.image.load('assets/boss.png')
        # LuizMelo

        #load sprite frames
        self.fighter_sprite_frames = get_sprite_frames(fighter_sprite_sheet, (162, 162))
        self.boss_sprite_frames = get_sprite_frames(boss_sprite_sheet, (250, 250))
        
        # list for sprite animation
        self.animations = {
                'fighter idle': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                'fighter run': [10, 11, 12, 13, 14, 15, 16, 17],
                'fighter jump': [20],
                'fighter attack': [30, 31, 32, 33, 34, 35, 36],
                'fighter alt attack': [40, 41, 42, 43, 44, 45, 46],
                'fighter special attack': [21, 22, 23, 24, 25, 26, 27, 28],
                'boss idle': [0, 1, 2, 3, 4, 5, 6, 7],
                'boss run': [8, 9, 10, 11, 12, 13, 14, 15],
                'boss attack': [32, 33, 34, 35, 36, 37, 38, 39],
                'boss dying': [48, 48, 48, 48, 48, 49, 49, 49, 49, 49, 50, 50, 50, 50, 50, 51, 51, 51, 51, 51, 52, 52, 52, 52, 52, 53, 53, 53, 53, 53],
                'boss dead': [54]}


        #boss theme!!
        pygame.mixer.init()
        self.bg_music = pygame.mixer.Sound('assets/theme.wav') # https://www.youtube.com/watch?v=tDHRpWNq2-s
        self.death_sound = pygame.mixer.Sound('assets/death.wav')
        self.hits = []
        self.wooshes = []
        for i in range(4):
            self.hits.append(pygame.mixer.Sound(f'assets/hit_{i}.wav'))
            self.wooshes.append(pygame.mixer.Sound(f'assets/woosh_{i}.wav'))
        self.magics = []
        for i in range(3):
            self.magics.append(pygame.mixer.Sound(f'assets/magic_{i}.wav'))
        self.magics[-1].play(-1)
        self.magics[-1].set_volume(0)
        self.special_hit = pygame.mixer.Sound('assets/special_hit.wav')

        self.bg_music.play(-1)

        # variables
        self.fighter_frame = 0
        self.boss_frame = 0
        self.base_font = pygame.font.Font(None, 35)
        self.base_font2 = pygame.font.Font(None, 35)
        self.text_surface = self.base_font.render('GEORGE THE EATER OF WORLDS', True, (255, 255, 255))
        self.text_surface2 = self.base_font2.render('DESTOYER7130', True, (255, 255, 255))
        self.ground = 965
        self.fighter_x = 10
        self.fighter_y = 710
        self.boss_x = 1750
        self.boss_y = 710
        self.fighter_speed = 30
        self.jumping = False
        self.jump_height = 10
        self.vel_y = self.jump_height
        self.attack_type = 0
        self.attack_effect = 0
        self.attack_radius = 0
        self.attack_cooldown = 0
        self.boss_hp = 100
        self.fighter_hp = 100
        self.boss_move = 0
        self.boss_speed = 30
        self.fighter_hit = False
        self.boss_alive = True
        self.fighter_alive = True
        self.fighter_animation = self.animations['fighter idle']
        self.boss_animation = self.animations['boss run']
        self.fighter_direction = 0
        self.boss_direction = 0
        self.fighter_attacking = 0
        self.start_dying = True
        self.mortal = True


    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Game.set_screen(ScreenTwo())
                print('Click')
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    Game.set_screen(PauseScreen(self))
                    self.bg_music.set_volume(0)
        

    def update(self) -> None:
        clock.tick(FPS)
        self.attack_cooldown -= 1

        # distance calculation
        distance = get_dist(self.fighter_x, self.fighter_y, self.boss_x, self.boss_y)

        # boss theme stop playing when
        if self.boss_hp <= 0 or self.fighter_hp <= 0:
            self.bg_music.set_volume(0)
            self.magics[-1].stop()
        else:
            self.bg_music.set_volume(1)
        
        # game (win or loss)
        if self.boss_hp <= 0:
            print('fighter wins')
            print(f'boss hp: {self.boss_hp}, fighter hp: {self.fighter_hp}')
            self.boss_alive = False
            #exit()

        if self.fighter_hp <= 0:
            print('fighter loses')
            print(f'boss hp: {self.boss_hp}, fighter hp: {self.fighter_hp}')
            self.fighter_alive = False
            Game.set_screen(lose())
            #exit()

        # boss
        if self.boss_alive:
            self.boss_move, self.boss_x, self.boss_speed = boss_ai(self.boss_move, self.boss_x, self.fighter_x, self.boss_speed, self.fighter_speed)
            self.boss_direction = sign(self.boss_move)
            if distance < 100:
                self.boss_animation = self.animations['boss attack']
                self.fighter_hit = True
                if self.mortal:
                    self.fighter_hp -= 1
                self.magics[-1].set_volume(1)
            else:
                self.magics[-1].set_volume(0)
                self.boss_animation = self.animations['boss run']
        else:
            if self.start_dying:
                self.boss_animation = self.animations['boss dying']
                self.start_dying = False
                self.death_sound.play()
                self.boss_frame = 0
            if self.boss_frame > len(self.animations['boss dying']):
                self.boss_animation = self.animations['boss dead']


        # keypress
        keys = pygame.key.get_pressed()

        if self.fighter_alive:
            # left, right movement
            self.fighter_animation = self.animations['fighter idle']
            if keys[pygame.K_a] or keys[pygame.K_d]:
                self.fighter_animation = self.animations['fighter run']
                if keys[pygame.K_a]:
                    self.fighter_direction = -1
                    self.fighter_x -= self.fighter_speed
                if keys[pygame.K_d]:
                    self.fighter_direction = 1
                    self.fighter_x += self.fighter_speed 

            # jump
            if keys[pygame.K_SPACE] and self.jumping == False:
                self.jumping = True

            #attack type and cooldowns
            if (keys[pygame.K_w] or keys[pygame.K_s]) and (self.attack_cooldown <= 0 or not self.mortal):
                choice(self.wooshes).play()
                if keys[pygame.K_w]:
                    self.attack_type = 1
                    self.attack_cooldown = 8
                if keys[pygame.K_s]:
                    self.attack_type = 2
                    self.attack_cooldown = 100
        if keys[pygame.K_b] and keys[pygame.K_y] and keys[pygame.K_r]:
            self.mortal = False
        if keys[pygame.K_t] and keys[pygame.K_v] and keys[pygame.K_n]:
            self.mortal = True


        # stay on screen
        if self.fighter_y >= 1080:
            self.fighter_y -= self.fighter_speed
        if self.fighter_x <= 0:
            self.fighter_x += self.fighter_speed
        if self.fighter_x >= 1910:
            if self.boss_alive:
                self.fighter_x -= self.fighter_speed
            else:
                Game.set_screen(win())

        
        # not fall of screen from jumping
        # Written by tyler wen.
        # tylers_cpt.py?
        if self.jumping:
            self.fighter_animation = self.animations['fighter jump']
            self.fighter_y -= self.jump_height * 3
            self.jump_height -= 1
            if self.jump_height < -10:
                self.jumping = False
                self.jump_height = 10

        #attacking hitbox/dmg
        if self.attack_type:
            self.fighter_attacking = self.attack_type
            self.fighter_frame = 0
            if distance < 300:
                self.attack_radius = 200
                self.attack_effect = self.attack_type
                if self.attack_type == 1:
                    self.boss_hp -= 1
                    choice(self.hits).play()
                if self.attack_type == 2:
                    self.boss_hp -= 10
                    self.boss_speed = 1
                    self.special_hit.play()
            self.attack_type = 0


        #attack animation stuff
        if self.fighter_attacking:
            if self.fighter_attacking == 1:
                self.fighter_animation = self.animations[choice(('fighter attack', 'fighter alt attack'))]
            if self.fighter_attacking == 2:
                self.fighter_animation = self.animations['fighter special attack']
            if self.fighter_frame > len(self.fighter_animation):
                self.fighter_attacking = 0



    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0,0))

        pygame.draw.rect(surface, (100, 100, 100), (20, 20, 540, 50)) # main fighter hp background
        pygame.draw.rect(surface, (0, 255, 0), (20, 20, 540 * self.fighter_hp / 100, 50)) # main fighter hp
        pygame.draw.rect(surface, (100, 100, 100), (1360, 20, 539, 50)) # main boss hp background
        # left to right health drain
        var = 540 * self.boss_hp / 100
        pygame.draw.rect(surface, (0, 255, 0), (1900 - var, 20, var, 50)) # the boss hp

        surface.blit(self.text_surface, (1370, 37)) # boss health name
        surface.blit(self.text_surface2, (30, 37)) # fighter health name

        # pygame.draw.rect(surface, (0, 0, 255), (self.fighter_x, self.fighter_y, 125, 250)) # main fighter character
        # pygame.draw.rect(surface, (0, 255, 0), (self.boss_x, self.boss_y, 125, 250)) # the boss

        fighter_frame = self.fighter_animation[int(self.fighter_frame % len(self.fighter_animation))]
        fighter_sprite_frame = self.fighter_sprite_frames[int(fighter_frame)]
        fighter_sprite_frame = pygame.transform.scale(fighter_sprite_frame, (648, 648))
        fighter_sprite_frame = pygame.transform.flip(fighter_sprite_frame, self.fighter_direction == -1, False)
        surface.blit(fighter_sprite_frame, (self.fighter_x - 324, self.fighter_y - 140))
        
        boss_frame = self.boss_animation[int(self.boss_frame % len(self.boss_animation))]
        boss_sprite_frame = self.boss_sprite_frames[int(boss_frame)]
        boss_sprite_frame = pygame.transform.scale(boss_sprite_frame, (1000, 1000))
        boss_sprite_frame = pygame.transform.flip(boss_sprite_frame, self.boss_direction == -1, False)
        surface.blit(boss_sprite_frame, (self.boss_x - 500, self.boss_y - 400))
        
        # surface.blit(self.fighter_sprite, (self.fighter_x, self.fighter_y, 125, 250)) # main fighter character

        # surface.blit(self.sprites[self.current_sprite_index], (125, 250)) # sprite animation drawing

        # surface.blit(self.boss_sprite, (self.boss_x, self.boss_y, 125, 250)) # the boss

        #attack circle effects/ hit markers
        self.attack_color = [(255, 0, 0), (255, 255, 0)]
        if self.fighter_hit:
            self.fighter_hit = False
            # pygame.draw.circle(surface, (255, 255, 255), (self.fighter_x, self.fighter_y), 100)
        if self.attack_effect:
            # pygame.draw.circle(surface, attack_color[self.attack_effect - 1], (self.boss_x, self.boss_y), self.attack_radius)
            if self.attack_radius > 0:
                self.attack_radius -= 5
            else:
                self.attack_effect = 0

        self.fighter_frame += 0.7
        self.boss_frame += 0.7
        

#================================================================================================


class main_menu:

    def __init__(self) -> None:
        self.menu_background = pygame.image.load('assets/main_background.png') #https://www.deviantart.com/albertov
        self.menu_background = pygame.transform.scale(self.menu_background, (1920, 1080))

        self.base_font = pygame.font.Font(None, 140)
        self.text_surface = self.base_font.render("?", True, (255, 255, 255))

        self.green = 71, 148, 58
        self.red = 255, 0, 0
        self.game2_button = pygame.Rect(20, 950, 100, 100) 

        self.click = False
        
        self.speed = 0.05
        self.amplitude = 20
        self.angle = 0
        self.title_x = 550
        self.title_y = 0

        #main menu stuff(title and whatnot)
        self.title = pygame.image.load('assets/title.png')
        self.title = pygame.transform.scale(self.title, (800, 800))

        self.menu_word = pygame.image.load('assets/main_menu_word.png')
        self.menu_word = pygame.transform.scale(self.menu_word, (800, 800))

    def handle_events(self, events: List[pygame.event.Event]) -> None:
            clock.tick(FPS)
            mx, my = pygame.mouse.get_pos()
            for event in events:
                if event.type == KEYDOWN:
                        if event.key == pygame.K_w:
                            Game.set_screen(Level_1())
                if event.type == MOUSEBUTTONDOWN:
                    if self.game2_button.collidepoint((mx, my)):
                        Game.set_screen(instructions())


    def update(self) -> None:
        self.angle += self.speed
        self.title_y = self.amplitude * math.sin(self.angle) + 100

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((255, 255, 255))  # always the first drawing command

        #menu background
        surface.blit(self.menu_background, (0,0)) 
        surface.blit(self.menu_word, (670, 450)) 

        #title
        surface.blit(self.title, (self.title_x, int(self.title_y)))

        pygame.draw.rect(surface, (0, 0, 0), self.game2_button)
        surface.blit(self.text_surface, (38, 960))
        

#================================================================================================


class lose:

    def __init__(self) -> None:
        self.base_font = pygame.font.Font(None, 150)
        self.base_font2 = pygame.font.Font(None, 75)
        self.text_surface = self.base_font.render("YOU DIED.", True, (255, 0, 0))
        self.text_surface2 = self.base_font2.render("Main Menu", True, (0, 0, 255))
        self.text_surface3 = self.base_font2.render("Retry?", True, (0, 0, 255))
        self.main_menu_button = pygame.Rect(600, 750, 300, 100) 
        self.retry_button = pygame.Rect(1000, 750, 300, 100) 
        self.click = False

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.main_menu_button.collidepoint((mx, my)):
                    Game.set_screen(main_menu())
                if self.retry_button.collidepoint((mx, my)):
                    Game.set_screen(Level_1())
          
          

    def update(self) -> None:
        ...

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))  # always the first drawing command
        # pygame.draw.rect(surface, (255, 0, 0), (255, 420, 800, 200))
        # pygame.draw.rect(surface, (100, 100, 100), (255, 420, 1410, 150)) # input box outline
        # pygame.draw.rect(surface, (255, 255, 255), (260, 425, 1400, 140)) # input box inner 
        pygame.draw.rect(surface, (0, 255, 0), self.main_menu_button)
        pygame.draw.rect(surface, (0, 255, 0), self.retry_button)
        surface.blit(self.text_surface, (685, 400))
        surface.blit(self.text_surface2, (615, 780))
        surface.blit(self.text_surface3, (1075, 780))

#================================================================================================

class instructions:

    def __init__(self) -> None:
        self.controls = pygame.image.load('assets/controls.png')
        self.controls = pygame.transform.scale(self.controls, (1920, 1080))

        self.base_font2 = pygame.font.Font(None, 75)
        self.text_surface2 = self.base_font2.render("Go Back", True, (255, 255, 255))
        self.main_menu_button = pygame.Rect(800, 970, 300, 100) 
        self.click = False

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.main_menu_button.collidepoint((mx, my)):
                    Game.set_screen(main_menu())
          
          

    def update(self) -> None:
        ...

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))  # always the first drawing command
        surface.blit(self.controls, (0,0))
        pygame.draw.rect(surface, (0, 0, 0), self.main_menu_button)
        surface.blit(self.text_surface2, (840, 1000))
        
#================================================================================================

class win:

    def __init__(self) -> None:
        self.base_font = pygame.font.Font(None, 100)
        self.base_font2 = pygame.font.Font(None, 75)
        self.text_surface = self.base_font.render("Congratulations you escaped :)", True, (0, 255, 0))
        self.text_surface2 = self.base_font2.render("Main Menu", True, (0, 0, 0))
        self.main_menu_button = pygame.Rect(800, 750, 300, 100) 
        self.click = False

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.main_menu_button.collidepoint((mx, my)):
                    Game.set_screen(main_menu())
          
          

    def update(self) -> None:
        ...

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))  # always the first drawing command
        # pygame.draw.rect(surface, (255, 0, 0), (255, 420, 800, 200))
        pygame.draw.rect(surface, (100, 100, 100), (255, 420, 1410, 150)) # input box outline
        pygame.draw.rect(surface, (255, 255, 255), (260, 425, 1400, 140)) # input box inner 
        pygame.draw.rect(surface, (0, 255, 0), self.main_menu_button)
        surface.blit(self.text_surface, (475, 460))
        surface.blit(self.text_surface2, (813, 780))
        

#================================================================================================

class Game:
    instance: 'Game'
    WIDTH = 1920
    HEIGHT = 1080
    SIZE = (WIDTH, HEIGHT)

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(self.SIZE)
        self.clock = pygame.time.Clock()

        self.current_screen = main_menu()

        Game.instance = self

    @classmethod
    def set_screen(cls, new_screen: ScreenInterface):
        cls.instance.current_screen = new_screen

    def run(self):
        running = True
        while running:
            # EVENT HANDLING
            events = pygame.event.get()
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                elif event.type == QUIT:
                    running = False

            self.current_screen.handle_events(events)
            self.current_screen.update()
            self.current_screen.draw(self.screen)

            # Must be the last two lines
            # of the game loop
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
