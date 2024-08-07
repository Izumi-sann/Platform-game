import pygame
import math
import random

class character():
    def __init__(self, screen_dimension:list) -> None:
        #screen
        self.screen_dimension = screen_dimension
        
        #character texture
        #INFORMAZIONE: LA TEXTURE DEL PERSONAGGIO è CAMBIATA NEL METODO UPDATE_FRAME, CHECK_COLLISION_GROUND!
        self.texture = {"idle": [], "walking": [], "jumping": [], "falling": [],"sprinting": []}#da inserire i frame di tutto
        for x in range(3):#caricamento dei frame del personaggio; se aggiungi altri frame cambia l'indice 
            self.texture["idle"].append(pygame.image.load(r"assets\player\character_idle_{:}.png".format(x+1)))
            self.texture["jumping"].append(pygame.image.load(r"assets\player\character_jumping_{:}.png".format(x+1)))
        
        self.current_texture = "idle"
        self.current_frame = 0
        self.image = self.texture["idle"][0]
        
        self.texture_dimension = self.texture["idle"][0].get_size()#width, height
        
        #position
        self.position = {"left": (self.screen_dimension[0]/2) - (self.texture_dimension[0]/2), "top": 50 - self.texture_dimension[1]}
        self.position["right"], self.position["bottom"] = self.position["left"] + self.texture_dimension[0],  self.position["top"] + self.texture_dimension[1]
        self.rect = pygame.Rect(self.position["left"], self.position["top"], self.texture_dimension[0], self.texture_dimension[1])
        
        #movements
        self.movements = [False, False]#sx, dx
        self.x_speed = 3#velocità orizzontale corpo
        self.y_speed = 0#velocità verticale corpo
        self.acceleration = 0.1#aumento velocità per ciclo
        
        self.sprint = [1, 1, False, 10]#indica il numero di sprint possibili, si resetta quando si tocca terra, [reset, attuali, tick(quanto dura)]
        self.jumps = [2, 2, False]
        
        #attack
        self.attack_range = 15 #px
        
        #offset telecamera
        self.y_offset = 0
    
    #aggiorna le variabili di posizione del personaggio; si consiglia eseguire dopo ogni cambiamento.
    def update_frame(self):
        prev_texture = self.current_texture
        if self.y_speed < 0:
            self.current_texture = "jumping"
        
        if prev_texture != self.current_texture:
            self.current_frame = 0
        
        self.current_frame += 0.075
        if self.current_frame >= len(self.texture[self.current_texture]):
            self.current_frame = 0
    
        self.image = self.texture[self.current_texture][int(self.current_frame)]
        self.texture_dimension = self.image.get_size()
    
    def update_position(self):
        self.position["right"], self.position["bottom"] = self.position["left"] + self.texture_dimension[0],  self.position["top"] + self.texture_dimension[1]
        self.rect.x = self.position["left"]
        self.rect.y = self.position["top"]
    
    def vertical_movement(self):
        #fa muovere verticlmente il personaggio
        if self.position["bottom"] <= self.screen_dimension[1]:
            self.position["top"] += self.y_speed
            self.y_speed += self.acceleration
    
    def horizontal_movement(self):
        #verifica lo sprint del personaggio
        if self.sprint[3] > 0 and self.sprint[2]:#lo sprint dura per due tick, ad ogni tick viene sottratto 1 alla durata(sprint[2])
            self.sprint[3] -= 1
        
        if self.sprint[3] == 0:#se la durata è terminata allora la velocità è riportata a 0, e la flag sprint a false
            self.x_speed = 3
            self.sprint[2] = False
            self.sprint[3] = 3
        
        self.position["left"] += (self.movements[1] - self.movements[0]) * self.x_speed
    
    def check_screen_borders(self):
        #gestisce i bordi orizzontali dello schermo
        if self.position["left"] < 0:
            self.position["left"] = 0
        if self.position["right"] > self.screen_dimension[0]:
            self.position["left"] = self.screen_dimension[0] - self.texture_dimension[0]
        
        #verifica che il personaggio non esca dai limiti superiori schermo
        if self.position["top"] < 0 + -(self.y_offset):
            self.position["top"] = 0
            self.y_speed = 0
        #verifica che il personaggio non esca dai limiti inferiori dello schermo
        elif self.position["bottom"] > self.screen_dimension[1]:
            self.position["top"] = self.screen_dimension[1] - (self.texture_dimension[1])
            self.y_speed = 0
            
            #resetta i salti
            self.jumps[2] = False
            self.jumps[1] = self.jumps[0]
            
            #resetta le sprint
            self.sprint[1] = self.sprint[0]
    
    def move(self):
        #fa muovere verticalmente il personaggio
        self.vertical_movement()
        self.update_position()
        
        #fa muovere orizzontalmente il personaggio e gestisce lo sprint
        self.horizontal_movement()
        self.update_position()
        
        #verifica che il personaggio rimanga entro i limiti dello schermo
        self.check_screen_borders()
        self.update_position()
    
    #questi metodi sono da usare nella classe Game, siccome la lista che richiedono è memorizzata solamente li
    def check_collision_ground(self, platform:list):#lista di tutte le piattaforme presenti
        #(scusa, non avevo voglia di farlo. perdonami. conosco le mie colpe.)
        for piattaforma in platform:#piattaforma è un oggetto Ground
            
            #verifica che il personaggio si trovi nei limiti verticali della piattaforma
            within_vertical_bounds = (piattaforma.rect.top < self.position["top"] + self.texture_dimension[1]/6 < piattaforma.rect.bottom) or \
                                    (piattaforma.rect.top < self.position["bottom"] - self.texture_dimension[1]/6  < piattaforma.rect.bottom)
            
            #verifica che il personaggio si trova nei limiti orizzontali della piattaforma
            within_horizontal_bounds = (self.position["right"] - 6 > piattaforma.rect.left) and\
                                        (self.position["left"] + 6 < piattaforma.rect.right)
            
            #verify if the character is on the left or right, considering if it's within it's evrtical range
            if within_vertical_bounds:
                #verifica se il personaggio si trova a sinistra della piattaforma
                on_the_left = self.position["right"] > piattaforma.rect.left and self.position["left"] < piattaforma.rect.left
                
                #verifica se il personaggio si trova a destra della piattaforma
                on_the_right = self.position["left"] < piattaforma.rect.right and self.position["right"] > piattaforma.rect.right
                
                if on_the_left:
                    self.movements[1] = False
                elif on_the_right:
                    self.movements[0] = False
            
            #verify if the character is over or under the platform, considering the platform's horizontal range
            if within_horizontal_bounds:
                on_the_top = (self.position["bottom"] > piattaforma.rect.top and self.position["bottom"] < piattaforma.rect.bottom)
                on_the_bottom = (piattaforma.rect.top+10 < self.position["top"] < piattaforma.rect.bottom)
                
                #verifica se il personaggio si trova sotto la piattaforma
                if on_the_bottom:
                    self.position["top"] = piattaforma.rect.bottom 
                    self.y_speed = 0
                
                #verifica se il personaggio si trova sopra la piattaforma
                elif on_the_top:

                    
                    self.position["top"] = piattaforma.rect.top - self.texture_dimension[1]
                    if not self.jumps[2]:#se non si sta facendo un salto la velocità è 0, in caso contrario non è modificata
                        self.y_speed = 0
                        self.jumps[1] = self.jumps[0]
                        self.jumps[2] = False
                    
                    if self.jumps[2]:
                        self.jumps[1] = self.jumps[0]
                        self.jumps[1] -= 1
                        self.jumps[2] = False

                    #resetta il numero di salti e sprint possibili
                    self.sprint[1] = self.sprint[0]
                    self.current_texture = "idle"

    def attack(self, boxes:list, platform:list):
        
        #delete every last bit of the box presence in the program
        def delete_all(boxes:list, box:Box, platform_list:list):#devi eliminare i campi nella piattaforma, dalla lista boxes
            platform = box.platform
            boxes.pop(boxes.index(box))
            platform_list[platform_list.index(platform)].box_there[0] = False
            platform_list[platform_list.index(platform)].box_there[1] = 0
            
        for box in boxes:
            #verify that the box and the character are on the same y coordinate, if not it proceed in the boxes list
            if not (box.rect.top < self.rect.centery and box.rect.bottom > self.rect.centery):
                continue
            #following the character perspective
            in_range_right = self.position["right"] + self.attack_range > box.rect.left
            in_range_left = self.position["left"] - self.attack_range < box.rect.right
            on_the_right = self.position["right"] < box.rect.right
            on_the_left = self.position["left"] > box.rect.left
            
            #if the character is not moving it attacks all around him
            if self.movements[0] == self.movements[1]:
                if (in_range_right and on_the_right) or (in_range_left and on_the_left):
                    delete_all(boxes, box, platform)
                    continue
            
            #moving on the left
            elif self.movements[0]:
                if in_range_left and on_the_left:
                    delete_all(boxes, box, platform)
                    continue
            
            #moving on the right
            elif self.movements[1]:
                if in_range_right and on_the_right:
                    delete_all(boxes, box, platform)

class Platform():
    def __init__(self, texture:str) -> None:
        self.texture = pygame.image.load(texture) 
        self.texture_dimension = self.texture.get_size()
        self.position = pygame.Vector2()
        self.box_there = [False, 0]

class Ground(Platform):
    def __init__(self, x, y) -> None:
        super().__init__(texture = r"assets\object\platform_3.png")
        self.position.xy = x, y
        self.rect = pygame.Rect(self.position.x, self.position.y, self.texture_dimension[0], self.texture_dimension[1])

class Rock(Platform):
    def __init__(self) -> None:
        super().__init__()

class Destroyable():
    def __init__(self, x, y, texture_path, platform) -> None:
        self.texture = pygame.image.load(texture_path)
        self.position = pygame.Vector2(x, y)
        self.dimension = self.texture.get_size() # width, height
        self.rect = pygame.Rect(self.position.x, self.position.y, self.dimension[0], self.dimension[1])
        self.platform = platform#wich platform the is the box on

class Box(Destroyable):
    def __init__(self, x, y, platform) -> None:
        super().__init__(x, y, r"assets\object\box_2.png", platform)