import pygame
import sys
import random
from Class import *
from typing import List, Union

class Game():
    def __init__(self, screen_dimension, game_character:character) -> None:
        # gestione finestra
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_dimension.copy()
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Jumpy Jumpy")
        self.clock = pygame.time.Clock()
        
        # risorse di gioco
        self.background = pygame.image.load(r"assets\background\background_2.png")
        self.base = pygame.image.load(r"assets\background\background_base.png")
        self.money_texture = pygame.image.load(r"assets\text\money_1.png")
        self.character = game_character

        self.platform: list[Ground] = [Ground((self.SCREEN_WIDTH/2) - 50, 50), Ground((self.SCREEN_WIDTH/2) - 100, -40)]
        self.last_layer = [-50, 1]#y min(la minore), numero piattaforme
        self.boxes: list[Box] = []
        self.box_dimension = Box(0, 0 , 0).dimension
        
        # gestione offset
        self.y_offset = 0
        self.x_offset = 0
        
        #screen text
        self.text_color = (255, 255, 255)  # Bianco
        self.font_size = 25
        self.font = pygame.font.Font(None, self.font_size)  # Usa il font predefinito di pygame
        self.upgrade_message:list = ["", 120]#messaggio di potenziamento, ottenuto da funzioni attack() e box_aim(), [messaggio, durata]
        
        #energy
        self.game_energy:list = [100, 100, 1000, pygame.Rect(10, 675, 30, 40)]#energia del gioco, se raggiunge 0 il gioco termina; ogni azione consuma energia [reset, attuale, barra]
        #in alcuni casi non è possibile aggiornare l'energia subito con l'azione quindi si aggiorna alla fine del ciclo con la variabile energy_use
        self.energy_use:int = 0
        
        self.in_game = True
        
    def box_log(self, box, process) -> None:
        if process == "creation":
            with open("box_log.txt", "a") as log:
                log.writelines(f"created box: {self.boxes[-1]}, --list: {self.boxes} \n")
        if process == "deletion":
            with open("box_log.txt", "a") as log:
                log.writelines(f"--deleted box: {self.boxes[-1]}, --list: {self.boxes} \n")

    def check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_a:#move left
                        self.character.movements[0] = True
                        
                    case pygame.K_d:#move right
                        self.character.movements[1] = True
                        
                    case pygame.K_SPACE:#jump
                        # verifica sia possibile saltare
                        if self.character.jumps[1] > 0: 
                            # update jumps variable
                            self.character.y_speed = self.character.jumps[5]  # imposta una velocità negativa preimpostata jumps[5] per muovere il personaggio verso l'alto
                            self.character.jumps[1] -= 1  # numero di salti rimanenti -1
                            self.character.jumps[3] = True  # indica che il personaggio sta saltando
                            
                            # verifica se nella sequenza di texture del salto è indicato un salto con effetto o senza
                            # (jump2 non indica direttaente un salto con effetto, ma è correlato)
                            # nella variabile jumps[7] è presente la sequenza di texture per i salti, jumps[1] indica i salti rimasti
                            if self.character.jumps[7][self.character.jumps[1]] == 1:
                                self.character.current_texture = "jump1" # imposta la texture del salto
                                self.character.effect_texture["jump_effect"][1] = 4 # durata dell'effetto in frame
                                self.energy_use += 5 # consumo energia
                            
                            elif self.character.jumps[7][self.character.jumps[1]] == 2:
                                self.character.current_texture = "jump2"
                                self.character.effect_texture["jump_effect"][1] = 4
                                self.energy_use += 10# consumo energia
                                
                    case pygame.K_LSHIFT:#sprint
                        if True in self.character.movements and self.character.sprint[1] > 0:
                            self.character.x_speed[1] = 50  # imposta la velocità del personaggio per lo sprint
                            self.character.sprint[3] = True #flag sprint attivo
                            self.character.sprint[1] -= 1  # numero di sprint possibili -1
                            
                            if type(self).__name__ == "Game":
                                self.game_energy[1] -= 10#consumo energia
                            
                    case pygame.K_s:#attack
                        self.upgrade_message[0], self.energy_use = self.character.attack(self.boxes, self.platform, self.screen)
                        
                    case pygame.K_LCTRL:#dash attack
                        self.character.dash[0] = True#durante il ciclo verrà attivato il dash automaticamente se dash[0] == True
                    
                    case pygame.K_KP_ENTER:#attiva un' azione
                        self.action = True

            if event.type == pygame.KEYUP:
                match event.key:
                    case pygame.K_a:#stop moving left
                        self.character.movements[0] = False
                    case pygame.K_d:#stop moving right
                        self.character.movements[1] = False

    def update_camera(self) -> None:
        # Calcola l'offset verticale della camera
        new_offset = -(self.character.position["top"] + self.character.texture_dimension[1] / 2 - self.SCREEN_HEIGHT / 2)
        
        #verifica che il cambio di offset sia significativo per evitare di creare un effetto di scorrimento fastidioso
        if new_offset - self.y_offset > 4 or new_offset - self.y_offset < -4:
            self.y_offset = new_offset
            self.character.y_offset = self.y_offset
        
        # Calcola l'offset orizzontale della camera per gestire il movimento del terreno iniziale
        previus_x_offset = self.x_offset
        self.x_offset = -(self.character.position["left"] + self.character.texture_dimension[0] / 2 - self.SCREEN_WIDTH / 2)
        
        if self.x_offset < -135 or self.x_offset > 135:
            self.x_offset = previus_x_offset

    def update_home_positions(self:any) -> None: #type: ignore
            #in questo caso self è riferito ad un oggetto di tipo Home; non è possibile specificarlo negli argomenti della funzione.
            new_y = lambda tex_h: self.SCREEN_HEIGHT - tex_h + self.y_offset
            new_x = lambda x: x + self.x_offset

            #calcola le nuove posizioni degli assets nella home; 
            #rect.top, rect.left = new_y(rect.height), new_x(spacing from 0)
            self.start_game[0].top = new_y(self.start_game[0].height)
            self.start_game[0].left = new_x(self.SCREEN_WIDTH/2 + 200)
            
            self.shops["jump"][0].top = new_y(self.shops["jump"][0].height)
            self.shops["jump"][0].left = new_x(-100)
            
            self.shops["speed"][0].top = new_y(self.shops["speed"][0].height)
            self.shops["speed"][0].left = new_x(0)
            
            self.shops["energy"][0].top = new_y(self.shops["energy"][0].height)
            self.shops["energy"][0].left = new_x(100)

    def blit_following_camera(self, prev_char_texture) -> None:  # telecamera mobile
        #funzioni di blit:
        def blit_background(self):
            self.screen.fill((0, 0, 0))
            background_height = self.background.get_height()
            relative_y = self.y_offset % background_height
            self.screen.blit(self.background, (0, relative_y - background_height))  # Sfondo con offset verticale
            self.screen.blit(self.background, (0, relative_y))  # Sfondo con offset verticale
        
        def blit_baseGround(self):
            if (self.character.position["top"] + (self.SCREEN_HEIGHT/2) + 30) >= self.SCREEN_HEIGHT:
                self.screen.blit(self.base, (-((self.base.get_width()-self.SCREEN_WIDTH)/2) + self.x_offset, self.SCREEN_HEIGHT + self.y_offset))
        
        def blit_characterTexture(self):
            self.character.update_frame(prev_char_texture != self.character.current_texture)
            self.screen.blit(self.character.image,
                            (self.character.position["left"],
                            self.SCREEN_HEIGHT / 2 - self.character.texture_dimension[1] / 2))

        def blit_platform(self):
            for base in self.platform:
                self.screen.blit(base.texture, (base.position.x, base.position.y + self.y_offset))

        def blit_box(self):
            for box in self.boxes:
                self.screen.blit(box.texture, (box.position.x, box.position.y + self.y_offset))
                if box.is_target:
                    self.screen.blit(box.target, (box.position.x-1, box.position.y + self.y_offset))
                    box.is_target = False
        
        def blit_effectTexture(self):
            self.character.update_effect_frame(update_speed=0.3, animation=0, dash= 2)#dash_inizio
            self.character.update_effect_frame(update_speed=-0.3, animation=1, dash= 4)#dash_arrivo
            #nel blocco try catch serve per verificare se la texture dell'effetto è nella lista; 
            #la texture è nella lista solo quando è da usare, in caso contrario non è presente e si passa al prossimo blocco.
            try:
                self.screen.blit(self.character.effect_image[0], (self.character.dash[2].left, self.character.dash[2].top+ self.y_offset))
                self.screen.blit(self.character.effect_image[1], (self.character.dash[4].left, self.character.dash[4].top+ self.y_offset))
            except Exception as error:
                pass#se la texture non è presente significa che non è necessaria al momento.
            
            #effetto salto
            #prima di stampare l'effetto si verifica se il salto da fare è 2(salto con effetto) e se l'effetto è attivo.
            try:
                if self.character.jumps[7][self.character.jumps[1]] == 2 and self.character.effect_texture["jump_effect"][1] > 0:
                    self.screen.blit(self.character.effect_texture["jump_effect"][0], (self.character.position["left"]-9, self.SCREEN_HEIGHT / 2 + self.character.texture_dimension[1] / 2))
                    self.character.effect_texture["jump_effect"][1] -= 1
            except IndexError:
                pass#quando non si salta la variabile self.character.jumps[1] = 6 manda in indexerror self.character.jumps[7]. non è un errore.
            
        def blit_money(self):
            text_surface = self.font.render(f"{self.character.money}", True, self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (30, 10)
            self.screen.blit(self.money_texture, (10, 10))
            self.screen.blit(text_surface, text_rect)
        
        def blit_upgradeMessage(self):
            if self.upgrade_message[1] <= 0:
                self.upgrade_message = ["", 120]
                return
                
            if self.upgrade_message[0] == "":
                return
            
            text_surface = self.font.render(f"{self.upgrade_message[0]}", True, (255, 255, 0))
            self.screen.blit(text_surface, (self.character.position["left"] - 100, (self.SCREEN_HEIGHT / 2 - self.character.texture_dimension[1] / 2) - 50))
            self.upgrade_message[1] -= 1
        
        def blit_score(self): 
            text_surface = self.font.render(f"{int(-1*(self.character.score[1]))}", True, self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (30, 40)
            self.screen.blit(text_surface,(self.SCREEN_WIDTH/2-10, 10))
        
        def blit_home(self):
            try:
                self.update_home_positions()#calcola le nuove posizioni degli assets nella home.
                
                #stampa a schermo le texture
                self.screen.blit(self.start_game[1], (self.start_game[0].left, self.start_game[0].top))
                self.screen.blit(self.shops["jump"][1], (self.shops["jump"][0].left, self.shops["jump"][0].top))
                self.screen.blit(self.shops["speed"][1], (self.shops["speed"][0].left, self.shops["speed"][0].top))
                self.screen.blit(self.shops["energy"][1], (self.shops["energy"][0].left, self.shops["energy"][0].top))
            except Exception as error:
                print("error -> line 226 Game.py", error)
            
        # aggiorna l'offset della camera
        self.update_camera()

        # stampa lo sfondo
        blit_background(self)
        
        #stampa il terreno iniziale (self.base)
        blit_baseGround(self)
        
        # stampa piattaforme
        blit_platform(self)
        
        #stampa box
        blit_box(self)
    
        pygame.draw.rect(self.screen, (220, 200, 150), self.game_energy[3])#barra energia
        
        #stampa gli assets della home se necessario
        if type(self).__name__ == "Home":
            blit_home(self)
        
        # stampa texture personaggio
        blit_characterTexture(self)
        
        #stampa texture di effetto
        blit_effectTexture(self)
        
        #stampa il denaro
        blit_money(self)
        
        #stampa altezza
        blit_score(self)
        
        #stampa messaggio di potenziamento
        blit_upgradeMessage(self)

    def create_x(self, piattaforme) -> list[int]:
        # Genera le piattaforme con una distribuzione orizzontale più bilanciata
        positions = []
        while len(positions) < piattaforme:
            x = random.randrange(0, self.SCREEN_WIDTH-100)
            if all(abs(x - pos) > 50 for pos in positions):  # Assicura che le piattaforme non siano troppo vicine tra loro
                positions.append(x)
        
        return positions

    def platform_spawn(self) -> None:
        # Verifica se è necessario generare un nuovo layer di piattaforme
        if self.character.position["top"] - self.SCREEN_HEIGHT/2 - 50 <= self.last_layer[0]:
            
            # Numero di piattaforme da generare
            piattaforme = random.choices([1, 2, 3], [60, 35, 5], k=1)[0]  # Restituisce il numero di piattaforme da creare per il layer corrente
            
            # Aggiorna la posizione del layer precedente con una variazione casuale
            self.last_layer[0] -= random.randint(80, 90)
            y = 0 #modificatore della coordinata y, NON UTILIZZATO
            
            #genera la posizione x per tutte le piattaforme
            positions = self.create_x(piattaforme)
            
            #creazione delle piattaforme e aggiunta in lista self.platfor 
            for x in positions:
                #crea la piattaforma
                self.platform.append(Ground(x, self.last_layer[0] + y))#MODIFICATORE Y NON USATO, Y=0!
                self.box_spawn("prob", self.platform[-1])#con "prob" si usa la parte della funzione che determina la presenza o meno del box, il resto è gestito dalla funzione

            self.last_layer[1] = piattaforme

        # Rimuove le piattaforme extra
        if len(self.platform) >= 50:#inizia a rimuovere quando il numero di piattaforme > 50
            if self.platform[1].box_there[0]:#if there's a box on the platform it proceeds to delete it
                #self.box_log(self.platform[1].box_there[1], "deletion")
                self.boxes.pop(self.boxes.index(self.platform[1].box_there[1]))#delete the box by searching the object reference
            self.platform.pop(1)#remove the platform; the first one needs to remain saved

    def box_spawn(self, function:str, platform:Ground) -> None:
        if function == "prob":
            #determina se creare o no il box
            spwan = random.choices([True, False], [20, 80], k=1)[0]
            if spwan:
                self.box_spawn("spawn", platform)
        
        if function == "spawn":
            #funzione di creazione box
            x = random.randrange(int(platform.position.x), platform.rect.right - self.box_dimension[0])
            self.boxes.append(Box(x, platform.position.y - self.box_dimension[1], platform))
            platform.box_there[0] = True
            platform.box_there[1] = self.boxes[-1]#a reference to the object
            
            #self.box_log(self.boxes[-1], "creation")

    def run_game(self) -> bool:
        self.game_energy[1] = self.game_energy[0]
        while self.in_game:
            # set iniziale
            pygame.display.update()
            self.clock.tick(60)#set the tik per second to 60            
            self.check_events()#check the happening events
            self.energy_count()#count the energy of the game
            
            #memorizza la texture del personaggio all'inizio del frame
            prev_texture = self.character.current_texture
            #memorizza il messaggio di potenziamento all'inizio del ciclo
            message = self.upgrade_message.copy()
            #memorizza il movimento del personaggio all'inizio del ciclo
            character_movement_L = self.character.movements[0]#left movement
            character_movement_R = self.character.movements[1]#right movement
            
            #game
            self.platform_spawn()#il metodo comprende anche lo spawn di box
    
            self.character.check_collision_ground(self.boxes)#verifica le collisioni con le box
            self.character.check_collision_ground(self.platform)#verifica le collisioni con le piattaforme e la base inferiore
            self.character.move()#movimento personaggio
            
            self.upgrade_message[0], energy_use = self.character.box_aim(self.boxes, self.platform, self.screen)#auto-aim per box(funzione di attacco associata è compresa)
            # scrittura su schermo
            if message[0] != "" and message[1] > 0:#se il messaggio di potenziamento è attivo
                self.upgrade_message[0] = message[0]#ripristino del messaggio di potenziamento se non è scaduto
            self.blit_following_camera(prev_texture)

            #set finali
            self.energy_use += energy_use#aggiorna l'energia usata nel ciclo corrente
            self.energy_count()#aggiorna l'energia del gioco
            
            #verifica il movimento del personaggio per ripristinarlo in caso di cambiamenti non volontari(see module check_collisions in Class.py\Character)
            if self.character.movements[0] != character_movement_L:
                self.character.movements[0] = character_movement_L
            if self.character.movements[1] != character_movement_R:
                self.character.movements[1] = character_movement_R
            
            self.character.dash[0] = False#reset del dash
            
        return True
        
    def energy_count(self) -> None:
        self.game_energy[1] -= self.energy_use
        self.energy_use = 0
        #conta l'energia del gioco e crea la barre dell'energia ad ogni ciclo
        if self.game_energy[1] <= 0:
            self.reset_game()
            return
        
        self.game_energy[3].width = self.game_energy[1]/4#aggiorna la barra dell'energia
        
    def reset_game(self) -> None:
        #resetta il gioco tranne il denaro generale e le statistiche
        self.platform: list[Ground] = [Ground((self.SCREEN_WIDTH/2) - 50, 50), Ground((self.SCREEN_WIDTH/2) - 100, -40)]
        self.last_layer = [-50, 1]#y min(la minore), numero piattaforme
        self.boxes: list[Box] = []
        
        self.y_offset = 0
        self.x_offset = 0
           
        self.character.reset("home")
        self.game_energy[1] = self.game_energy[0]
        
        self.in_game = False
