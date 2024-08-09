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
        self.start_game = pygame.rect.Rect(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 100, 100)
        
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
            except:
                print("error here")
            