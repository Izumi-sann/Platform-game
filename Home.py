import pygame
from Class import *
from Game import Game
from typing import Callable, Tuple

class Home(Game):
    def __init__(self, screen_dimension, game_character) -> None:
        super().__init__(screen_dimension=screen_dimension, game_character=game_character)
        
        #home assets -shops, start_game-
        self.credits_sign:list = [] #put a literal sign int the home with the credits of the game.

        self.shops:dict[str, list] = {"jump": [], "speed": [], "energy": []} #shops è un dizionario che contiene le informazioni degli shop
        self.set_actions_variables()#setta gli assets delle azione, shops e start_game.
        
        self.action:bool = False #action indica se è stato attivato un comando di azione quando ci si trova sullo shop o sul start_game; è attivato da "enter", vedere check_events()
    
    def set_actions_variables(self) -> None:
        def jump_shop(self) -> Tuple[pygame.Rect, pygame.Surface, str, Callable, int, str, bool]:
            """the method return a list with immutable sequence, not a tuple. unluckily, in python you can't annote a list with specific sequence."""
            shop_jump_texture = pygame.image.load(r"assets\object\start_game.png")
            shop_jump_rect = shop_jump_texture.get_rect()
            return [shop_jump_rect, shop_jump_texture, "\tjump shrine\nupgrade your jump", self.action_jumpShop, 30, "jump shrine\nupgrade your jump", True] # type: ignore [rect, texture, message, function, cost, reset text, flag] 

        def speed_shop(self) -> Tuple[pygame.Rect, pygame.Surface, str, Callable, int, str, bool]:
            """the method return a list with immutable sequence, not a tuple. unluckily, in python you can't annote a list with specific sequence."""
            shop_speed_texture = pygame.image.load(r"assets\object\start_game.png")
            shop_speed_rect = shop_speed_texture.get_rect()
            return [shop_speed_rect, shop_speed_texture, "speed shrine\nupgrade your speed", self.action_speedShop, 30, "speed shrine\nupgrade your speed", True] # type: ignore [rect, texture, message, function, cost, reset text, flag]

        def energy_shop(self) -> Tuple[pygame.Rect, pygame.Surface, str, Callable, int, str, bool]:
            """the method return a list with immutable sequence, not a tuple. unluckily, in python you can't annote a list with specific sequence."""
            shop_energy_texture = pygame.image.load(r"assets\object\start_game.png")
            shop_energy_rect = shop_energy_texture.get_rect()
            return [shop_energy_rect, shop_energy_texture, "energy shrine\nupgrade your energy", self.action_energyShop, 100, "energy shrine\nupgrade your energy", True] # type: ignore [rect, texture, message, function, cost, rest text, flag]
        
        def start_game(self) -> Tuple[pygame.Rect, pygame.Surface, str, Callable, int, str, bool]:
            """the method return a list with immutable sequence, not a tuple. unluckily, in python you can't annote a list with specific sequence."""
            start_game_texture = pygame.image.load(r"assets\object\start_game.png")
            start_game_rect = start_game_texture.get_rect()
            return [start_game_rect, start_game_texture, "start game", self.action_startGame, 0] # type: ignore  [rect, texture, message, function, cost] (it has a cost just for the sake of the function check_collision_assets)

        self.shops["jump"] = jump_shop(self) #type: ignore
        self.shops["speed"] = speed_shop(self) #type: ignore
        self.shops["energy"] = energy_shop(self) #type: ignore
        self.start_game = start_game(self) #type: ignore
        
        self.no_money_message = ["not enough money", 0]

    def action_startGame(self) -> None:
        self.in_game = True
        self.character.reset("game")
        return
    
    def action_jumpShop(self) -> None:
        #aggiorna il salto del personaggio, se questo non è al massimo
        #aumenta di 1 il numero di salti iniziali
        if self.character.jumps[8] < 4:
            self.character.jumps[8] += 1
            self.character.jumps[0] = self.character.jumps[8]
            
            self.character.jumps[7] = self.character.jumps_texture_number[self.character.jumps[0]]
            #quando i salti iniziali sono al massimo aumenta i salti massimi di 2(una sola volta.); l'upgrade massimo dalla home è fino a 4 salti, gli altri si ottengono in partita.
            if self.character.jumps[8] == 4:
                self.character.jumps[2] = 6
                
        #aumenta l'altezza del salto
        if self.character.jumps[4] > self.character.jumps[6]+1:
            self.character.jumps[4] -= 0.5

            if self.character.jumps[4] == -5.0:#se l'altezza del salto è al massimo non si può upgradare nient'altro qui, quindi si flagga l'upgrade a False
                self.shops["jump"][2], self.shops["jump"][5] = "jump shrine\nmax level reached", "jump shrine\nmax level reached"
                self.shops["jump"][6] = False #flag di upgrade = False. non si può più fare l'upgrade
                return
        
        self.character.money -= self.shops["jump"][4]
    
    def action_speedShop(self) -> None:
        #aggiorna la velocità del personaggio e il numero di sprint se questi non sono al massimo
        if self.character.sprint[5] <= self.character.sprint[2]-1:
            self.character.sprint[5] += 1
            self.character.sprint[0] = self.character.sprint[5]
            
        if self.character.x_speed[0] <= self.character.x_speed[2]-1:
            self.character.x_speed[3] += 0.5
            self.character.x_speed[0] = self.character.x_speed[3]
            
            if self.character.x_speed[3] == 5.5:
                #idealmente quando la velocità è al massimo non si puù upgradare nient'altro qui, quindi si flagga l'upgrade a False
                self.shops["speed"][2], self.shops["speed"][5] = "speed shrine\nmax level reached", "speed shrine\nmax level reached"
                self.shops["speed"][6] = False #flag di upgrade = False. non si può più fare l'upgrade
                return
        
        self.character.money -= self.shops["speed"][4]
        
    def action_energyShop(self) -> None:
        if self.game_energy[0] < self.game_energy[2]:
            self.game_energy[0] += 100
            self.character.money -= self.shops["energy"][4]
            
        if self.game_energy[0] == 1000:
            self.shops["energy"][2], self.shops["energy"][5] = "energy shrine\nmax level reached", "energy shrine\nmax level reached"
            self.shops["energy"][6] = False #flag di upgrade = False. non si può più fare l'upgrade
    
    def blit_action_message(self, object:list) -> None:
        #scrive a schermo la funzione da attivare
        #object contiene sia il messaggio da mostrare che la funzione da attivare rispetto all'oggetto in questione.
        #quando il tempo del messaggio di mancanza di soldi è a 0, ritorna il messaggio originale. object[2] = object[5] (current = reset)
        #try except per evitare errori se l'oggetto non ha un reset text. caso di start_game.   
        if self.no_money_message[1] == 0:
            try: object[2] = object[5]
            except: pass
            
        text_surface = self.font.render(object[2], True, (95, 95, 95))
        self.screen.blit(text_surface, (object[0].left -40, self.SCREEN_HEIGHT - object[0].height + self.y_offset - 50))
        self.upgrade_message[1] -= 1
        
        #si attiva l'azione se il personaggio preme "enter"
        if self.action:
            try: 
                if not object[6]: #se l'upgrade è al massimo (object[6] = false)    
                    return #non si fa l'upgrade
            except: pass
            
            if self.character.money < object[4]: # se non si hanno abbastanza soldi (soldi posseduti < costo upgrade)
                object[2] = "not enough money"
                self.no_money_message[1] = 120
            
            object[3]() #si esegue la funzione di upgrade dell'oggetto in questione

    #verifica sovrapposizione personaggio con oggetti di azione
    def check_collision_assets(self, object:list) -> None:
            #verifica che il personaggio si trova nei limiti orizzontali della piattaforma
            within_horizontal_bounds = (self.character.position["right"] - 6 > object[0].left) and\
                                        (self.character.position["left"] + 6 < object[0].right)
            
            #verifica che il personaggio non sia  troppo in alto rispetto all'oggetto (680px è sufficiente rispetto alle texture per non fare calcoli e calcoli)
            within_vertical_bounds = self.character.position["bottom"] > 680
            
            #scrive a scehermo il messaggio di mancanza di soldi per 2 secondi; 120 frame; 
            #quando il messaggio è da mostrare no_money_message[1] = 120, altrimenti 0. quando arriva a 0 ritorna il messaggio originale.
            if self.no_money_message[1] > 0:
                self.no_money_message[1] -= 1
            
            #se le condizioni di posizione del personaggio rispetto all'oggetto sono soddisfatte, si mostra il messaggio di azione
            if within_horizontal_bounds and within_vertical_bounds:
                self.blit_action_message(object)

    def run_game(self) -> Tuple[bool, int]:
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
                self.list_object = [self.start_game, self.shops["jump"], self.shops["speed"], self.shops["energy"]]
                [self.check_collision_assets(obj_list) for obj_list in self.list_object]
            #just in case
            except Exception as error:
                print("error -> line 171 Home.py", error)
            
            #set finale
            self.action = False
            
            print(self.character.jumps)
            
        return True, self.game_energy[0]
