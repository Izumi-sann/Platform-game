import pygame
import math
import sys
import random
from Class import *

class Game():
    def __init__(self, width=480, height=720) -> None:
        # gestione finestra
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("game title")
        self.clock = pygame.time.Clock()

        # risorse di gioco
        self.background = pygame.image.load(r"assets\background\background_2.png")
        self.base = pygame.image.load(r"assets\background\background_base.png")
        self.character = character([self.SCREEN_WIDTH, self.SCREEN_HEIGHT])
        self.platform: list[Ground] = [Ground((self.SCREEN_WIDTH/2) - 50, 50), Ground((self.SCREEN_WIDTH/2) - 100, -50)]
        self.last_layer = [-50, 1]#y min(la minore), numero piattaforme

        # gestione offset
        self.y_offset = 0
        self.x_offset = 0

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_a:
                        self.character.movements[0] = True
                    case pygame.K_d:
                        self.character.movements[1] = True
                    case pygame.K_SPACE:
                        if self.character.jumps[1] > 0:  # verifica sia possibile saltare
                            self.character.y_speed = -3  # imposta una velocità negativa per muovere il personaggio verso l'alto
                            self.character.jumps[1] -= 1  # numero di salti possibili
                            self.character.jumps[2] = True  # indica se il personaggio sta saltando
                    case pygame.K_LSHIFT:
                        if True in self.character.movements and self.character.sprint[1] > 0:
                            self.character.x_speed = 50  # imposta la velocità del personaggio per lo sprint
                            self.character.sprint[2] = True
                            self.character.sprint[1] -= 1  # numero di sprint possibili -1

            if event.type == pygame.KEYUP:
                match event.key:
                    case pygame.K_a:
                        self.character.movements[0] = False
                    case pygame.K_d:
                        self.character.movements[1] = False

    def update_camera(self):
        # Calcola l'offset verticale della camera
        new_offset = -(self.character.position["top"] + self.character.texture_dimension[1] / 2 - self.SCREEN_HEIGHT / 2)
        
        if new_offset - self.y_offset > 3 or new_offset - self.y_offset < -3:
            self.y_offset = new_offset
            self.character.y_offset = self.y_offset
            
            previus_x_offset = self.x_offset
            self.x_offset = -(self.character.position["left"] + self.character.texture_dimension[0] / 2 - self.SCREEN_WIDTH / 2)
        
        if self.x_offset < -135 or self.x_offset > 135:
            self.x_offset = previus_x_offset

    def blit_following_camera(self):  # telecamera mobile
        # aggiorna l'offset della camera
        self.update_camera()

        # stampa lo sfondo
        self.screen.fill((0, 0, 0))
        background_height = self.background.get_height()
        relative_y = self.y_offset % background_height
        self.screen.blit(self.background, (0, relative_y - background_height))  # Sfondo con offset verticale
        self.screen.blit(self.background, (0, relative_y))  # Sfondo con offset verticale
        
        #stampa il terreno iniziale (self.base)
        if (self.character.position["top"] + (self.SCREEN_HEIGHT/2) + 30) >= self.SCREEN_HEIGHT:
            self.screen.blit(self.base, (-((self.base.get_width()-self.SCREEN_WIDTH)/2) + self.x_offset, self.SCREEN_HEIGHT + self.y_offset))
        
        # stampa personaggio
        self.character.update_frame()
        self.screen.blit(self.character.image,
                        (self.character.position["left"],
                        self.SCREEN_HEIGHT / 2 - self.character.texture_dimension[1] / 2))

        # stampa piattaforme
        for base in self.platform:
            self.screen.blit(base.texture, (base.position.x, base.position.y + self.y_offset))

    def create_x(self, piattaforme) -> list:
        # Genera le piattaforme con una distribuzione orizzontale più bilanciata
        positions = []
        while len(positions) < piattaforme:
            x = random.randrange(0, self.SCREEN_WIDTH-100)
            if all(abs(x - pos) > 50 for pos in positions):  # Assicura che le piattaforme non siano troppo vicine tra loro
                positions.append(x)
        
        return positions

    def platform_spawn(self):
        '''
        #modifica, eventualmente, la posizione y di pochi pixel per diversificare la posizione delle piattaforme
        if self.last_layer[1] > 1:
            for indice in range(1, len(positions)):
                for piattaforma in range(self.last_layer[1]):
                    #verifica che verticalmente la nuova piattaforma non sia sovrapposta ad una piattaforma del layer precedente
                    if self.platform[piattaforma].rect.centerx + 50 < positions[indice] or self.platform[piattaforma].rect.centerx -50 > positions[indice] + self.platform[piattaforma].texture_dimension[0]:
                        y = random.randrange(10, 30) #crea un modificatore della y
                
        '''
        
        # Verifica se è necessario generare un nuovo layer di piattaforme
        if self.character.position["top"] - self.SCREEN_HEIGHT/2 - 50 <= self.last_layer[0]:
            
            # Numero di piattaforme da generare
            piattaforme = random.choices([1, 2, 3], [60, 35, 5], k=1)[0]  # Restituisce il numero di piattaforme da creare per il layer corrente
            
            if piattaforme == 0:
                return
            
            # Aggiorna la posizione del layer precedente con una variazione casuale
            self.last_layer[0] -= random.randint(80, 110)
            y = 0 #modificatore della coordinata y
            
            #genera la posizione x per tutte le piattaforme
            positions = self.create_x(piattaforme)
            
            #creazione delle piattaforme e aggiunta in lista self.platform
            for x in positions:
                #crea la piattaforma
                self.platform.append(Ground(x, self.last_layer[0] + y))

            self.last_layer[1] = piattaforme
        # Rimuove le piattaforme extra
        if len(self.platform) >= 50:
            self.platform.pop(1)

    def run_game(self):
        while True:
            # set iniziale
            pygame.display.update()
            self.clock.tick(60)
            self.check_events()
            
            # game
            self.character.check_collision_ground(self.platform)
            self.character.move()
            self.platform_spawn()
            
            # scrittura su schermo e set finale
            self.blit_following_camera()


Game().run_game()
