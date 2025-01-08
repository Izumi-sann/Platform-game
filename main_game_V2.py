from Class import *
from Game import Game
from Home import Home

#main game variables
SCREEN_DIMENSION:tuple[int, int]  = (480, 720)
game_character:character    = character(SCREEN_DIMENSION)
game:Game                   = Game(screen_dimension=SCREEN_DIMENSION, game_character=game_character)
home:Home                   = Home(screen_dimension=SCREEN_DIMENSION, game_character=game_character)

#main game cycle
cycle:bool = True
while cycle:
    game.in_game = True
    cycle = game.run_game()#game.in_game = False
    
    home.in_game = False#in game generally means that the player is in the main game, not the home.
    cycle, energy = home.run_game()
    game.game_energy[0] = energy