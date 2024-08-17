import pygame
import math
import sys
import random
from Class import *
from Game import Game

class Home(Game):
    def __init__(self, screen_dimension, game_character) -> None:
        super().__init__(screen_dimension=screen_dimension, game_character=game_character)
        
        #home assets -shops, start_game-
        self.credits_sign:list = None #put a literal sign int the home with the credits of the game.

        self.shops:dict[str, list] = {"jump": None, "speed": None, "energy": None}
        self.set_actions_variables(self)#setta gli assets delle azione, shops e start_game.
        
        self.action:bool = False #action indica se è stato attivato un comando di azione quando ci si trova sullo shop o sul start_game; è attivato da "enter", vedere check_events()
    
    def set_actions_variables(self) -> None:
        def jump_shop(self) -> tuple[pygame.Rect, pygame.Surface, str, function]:
            shop_jump_texture = pygame.image.load(r"assets\object\start_game.png")
            shop_jump_rect = shop_jump_texture.get_rect()
            return [shop_jump_rect, shop_jump_texture, "jump shrine\nupgrade your jump", self.action_jumpShop] # [rect, texture, message, function]

        def speed_shop(self) -> tuple[pygame.Rect, pygame.Surface, str, function]:
            shop_speed_texture = pygame.image.load(r"assets\object\start_game.png")
            shop_speed_rect = shop_speed_texture.get_rect()
            return [shop_speed_rect, shop_speed_texture, "speed shrine\nupgrade your speed", self.action_speedShop]

        def energy_shop(self) -> tuple[pygame.Rect, pygame.Surface, str, function]:
            shop_energy_texture = pygame.image.load(r"assets\object\start_game.png")
            shop_energy_rect = shop_energy_texture.get_rect()
            return [shop_energy_rect, shop_energy_texture, "energy shrine\nupgrade your energy", self.action_energyShop]
        
        def start_game(self) -> tuple[pygame.Rect, pygame.Surface, str, function]:
            start_game_texture = pygame.image.load(r"assets\object\start_game.png")
            start_game_rect = start_game_texture.get_rect()
            return [start_game_rect, start_game_texture, "start game", self.action_startGame()] # [rect, texture] 

        self.shops["jump"] = jump_shop(self)
        self.shops["speed"] = speed_shop(self)
        self.shops["energy"] = energy_shop(self)
        self.start_game = start_game(self)

    def action_startGame(self) -> None:
        self.in_game = True
        self.character.reset("game")
        return
    
    def action_jumpShop(self) -> None:
        self.character.jumps[0] += 1
        self.character.jumps[2] += 1
        self.character.jumps[4] -= 0.5
        return
    
    def action_speedShop(self) -> None:
        if self.character.x_speed[0] <= 5.5:
            self.character.x_speed[0] += 0.5
        self.character.sprint[0] += 1

    def action_energyShop(self) -> None:
        self.game_energy[0] *= 2

    #verifica sovrapposizione personaggio con oggetti di azione
    def check_collision_assets(self, object:list) -> None:
        
            #verifica che il personaggio si trova nei limiti orizzontali della piattaforma
            within_horizontal_bounds = (self.character.position["right"] - 6 > object[0].left) and\
                                        (self.character.position["left"] + 6 < object[0].right)
            
            within_vertical_bounds = self.character.position["bottom"] > 680
            
            if within_horizontal_bounds and within_vertical_bounds:
                #scrive a schermo la funzione da attivare
                text_surface = self.font.render(object[2], True, (95, 95, 95))
                self.screen.blit(text_surface, (object[0].left - 20, self.SCREEN_HEIGHT - object[0].height + self.y_offset - 20))
                self.upgrade_message[1] -= 1
                
                if self.action:
                    object[3]
                    return

    def run_game(self) -> bool:
        while self.in_game == False:
            # set iniziale
            pygame.display.update()
            self.clock.tick(60)#set the tik per second to 60            
            self.check_events()#check the happening events
            
            #memorizza la texture del personaggio all'inizio del frame
            prev_texture = self.character.current_texture
            
            #game
            self.character.move()#movimento personaggio
            
            try:
                self.blit_following_camera(prev_texture)
                map(self.check_collision_assets, [self.start_game, self.shops["jump"]])
                #self.check_collision_assets(self.start_game)
            except:
                print("error here")
            
            #set finale
            self.action = False
        
        return True