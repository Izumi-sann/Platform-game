import pygame
import math
import sys
import random
from Class import *
from Game import Game

class Home(Game):
    def __init__(self, screen_dimension, game_character) -> None:
        super().__init__(screen_dimension=screen_dimension, game_character=game_character)
        
        #home assets
        self.shop = 0
        self.cretits_sign = 0
        
        start_game_texture = pygame.image.load(r"assets\object\start_game.png")
        start_game_rect = start_game_texture.get_rect()
        self.start_game = [start_game_rect, start_game_texture] # [rect, texture]
        
        self.action = False #action indica se è stato attivato un comando di azione quando ci si trova sullo shop o sul start_game; è attivato da "enter", vedere check_events()
        
    def run_game(self):
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
                self.check_collision_assets()
            except:
                print("error here")
            
            
            #set finale
            self.action = False
        
        return True
    
    def check_collision_assets(self):
        #check collision start game
        
            #verifica che il personaggio si trova nei limiti orizzontali della piattaforma
            within_horizontal_bounds = (self.character.position["right"] - 6 > self.start_game[0].left) and\
                                        (self.character.position["left"] + 6 < self.start_game[0].right)
            
            within_vertical_bounds = self.character.position["bottom"] > 680
            
            if within_horizontal_bounds and within_vertical_bounds:
                #scrive a schermo la funzione da attivare
                text_surface = self.font.render(f"start game", True, (95, 95, 95))
                self.screen.blit(text_surface, (self.start_game[0].left - 20, self.SCREEN_HEIGHT - self.start_game[0].height + self.y_offset - 20))
                self.upgrade_message[1] -= 1
                
                if self.action:
                    self.in_game = True
                    self.character.reset("game")
                    return
        