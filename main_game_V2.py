from Class import *
from Game import Game
from Home import Home

"""DEV LOG, GAME VERSIONS (iniziato giorno 17-06-24). TOTALI 26 giorni di sviluppo:
   --> stand-by dal 23/06 al 24/07 per vacanze MARE;
         -> ci ho lavorato lo stesso ma ho perso tutto il lavoro fatto.  muoio.
   --> stand-by dal 10/08 al 17/08 per vacanze LIVIGNO;
         -> c'è stata occasione per lavorare da webbrowser, ma non potevo testare.
   --> stand-by dal 19/08 al 27/08 per vacanze SARDEGNA;
         -> ...basta vacanze. vi prego. 26 giorni di sviluppo in 60+ giorni.
         -> ritornato il 27...sfinito.

MODIFICHE 25-07-24 \\V2.01/: migliorata funzione Character.attak() - aggiunta metodo Character.delete_box() -; 
                            migliorie al processo di rimozione di box dalla lista Game.boxes e dal parametro Platform.box_there.
MODIFICHE 26-07-24 \\V2.02/: Aggiunta funzione di auto-aim per box, aggiunta assets puntatore.
MODIFICHE 27-07-24:         aggiunta animazione jump1
MODIFICHE 29-07-24:         upgrade dell'algoritmo di cambiamento texture, aggiunta animazione jump2
MODIFICHE 30-07-24:         aggiunta attacco Dash, aggiunta animazione attacco dash
MODIFICHE 31-07-24:         continuazione animazione attacco dash
MODIFICHE 01-08-24:         miglioria funzione -Game.blit_following_camera-, commenti più precisi e aggiunta nuovi, aggiuti soldi
MODIFICHE 03-08-24:         aggiunta power-up e messaggio di ottenimento power-up #mi sto per sparare in testa
MODIFICHE 04-08-24 \\V2.03/: aggiunta score
MODIFICHE 05-08-24:         miglioramento ordine liste -salto sprint dash x_speed-, aggiunta livello massimo potenziamenti, 
                            miglioramento texture per salti 3 e 4, correzzione bug velocità di sprint
MODIFICHE 06-08-24:         aggiunta barra energia, aggiunta funzione di consumo energia
MODIFICHE 07-08-24:         aggiunta repository su github(sistemati vari errori), funzione di reset del gioco
MODIFICHE 08-08-24 \\V2.1/:  aggiunta classe Home, sistemata texture base background, 
                            aggiunto file main_game_V2 -which contaions the main game loop (game -> home -> game) and some global varaibles-
MODIFICHE 09-08-24:         migliorato ciclo di transizione game-home
MODIFICHE 10-08-24:         creazione texture start game + funzione start game
MODIFIHCE 11-08-24:         minori cambiamenti alla classe alla funzione start game(scrittura a schermo). fuori  casa per 7 giorni.
MODIFICHE 13-08-24 \\V2.12/: miglioratometodo di creazione variabili shop e assets in Home -funzione set_action_vriables-, 
                            aggiunta funzione di upgrade per salto, velocità e energia.
MODIFICHE 15-08-24:         aggiunta funzione per il blit degli assets home + funzione di update della posizione; 
                            //TODO migliorare funzione di calcolo posizione.
MODIIFCHE 17-08-24:         migliorata funzione blit e update assets home(TODO), migiorata funzione di check_collision_assets, 
                            modificata variabile game_energy(aggiunto max_energy) e gestita meglio nel programma, aggiunta condizioni di upgrade massimo. 
                            //TODO: aggiungere condizioni di costo. + animazione di acquisizione.
MODIFICHE 18-08-24:         migliorata la disposizione degli assets in Home, miglioramenti minori alla funzione Game.update_effect_texture,
                            migliorata leggibilità e precisione del codice per quanto riguarda i tipi di ritorno delle funzioni.
                            migliorata la variabile character.jumps, con aggiunta di sequenza di texture per i salti -> modificata la logica di modifica texture di salto.
MODIFICHE 28-08-24:         Aggiunte condizioni di costo per gli upgrade(TODO), aggiunta messaggio per mancanza di soldi in upgrade, aggiunto limite di upgrade.
                            //TODO: aumeto numero soldi ottenuti da box in base al numero di soldi da parte, distribuisci a campana i soldi ottenuti, messaggio acquisizione upgrade.
MODIFICHE 29-08-24:         migliorato limitatore degli upgrade, hot fix dei bug nella funzione di reset del personaggio(speed, jump ...)
"""


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
