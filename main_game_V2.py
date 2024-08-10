import pygame
import math
import sys
import random

from Class import *
from Game import Game
from Home import Home

"""DEV LOG, GAME VERSIONS (iniziato giorno 17-06-24, stand-by dal 23/06 al 24/07 per vacanze; TOTALI 23 giorni di sviluppo):
MODIFICHE 25-07-24 \V2.01/: migliorata funzione Character.attak() - aggiunta metodo Character.delete_box() -; 
                            migliorie al processo di rimozione di box dalla lista Game.boxes e dal parametro Platform.box_there.
MODIFICHE 26-07-24 \V2.02/: Aggiunta funzione di auto-aim per box, aggiunta assets puntatore.
MODIFICHE 27-07-24:         aggiunta animazione jump1
MODIFICHE 29-07-24:         upgrade dell'algoritmo di cambiamento texture, aggiunta animazione jump2
MODIFICHE 30-07-24:         aggiunta attacco Dash, aggiunta animazione attacco dash
MODIFICHE 31-07-24:         continuazione animazione attacco dash
MODIFICHE 01-08-24:         miglioria funzione -Game.blit_following_camera-, commenti più precisi e aggiunta nuovi, aggiuti soldi
MODIFICHE 03-08-24:         aggiunta power-up e messaggio di ottenimento power-up #mi sto per sparare in testa
MODIFICHE 04-08-24 \V2.03/: aggiunta score
MODIFICHE 05-08-24:         miglioramento ordine liste -salto sprint dash x_speed-, aggiunta livello massimo potenziamenti, 
                            miglioramento texture per salti 3 e 4, correzzione bug velocità di sprint
MODIFICHE 06-08-24:         aggiunta barra energia, aggiunta funzione di consumo energia
MODIFICHE 07-08-24:         aggiunta repository su github(sistemati vari errori), funzione di reset del gioco
MODIFICHE 08-08-24 \V2.1/:  aggiunta classe Home, sistemata texture base background, 
                            aggiunto file main_game_V2 -which contaions the main game loop (game -> home -> game) and some global varaibles-
MODIFICHE 09-08-24:         migliorato ciclo di transizione game-home
MODIFICHE 10-08-24:         creazione texture shop - start game, 
"""


SCREEN_DIMENSION = [480, 720]
game_character = character(SCREEN_DIMENSION)
game = Game(screen_dimension=SCREEN_DIMENSION, game_character=game_character)
home = Home(screen_dimension=SCREEN_DIMENSION, game_character=game_character)

cycle = True
while cycle:
    game.in_game = True
    cycle = game.run_game()#game.in_game = False
    
    home.in_game = False#in game generally means that the player is in the main game, not the home.
    cycle = home.run_game()
