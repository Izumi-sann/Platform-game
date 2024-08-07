import pygame
import math
import random
import sys

class character():
    def __init__(self, screen_dimension:list) -> None:
        #screen
        self.screen_dimension = screen_dimension
        
        #character texture
        #INFORMAZIONE: LA TEXTURE DEL PERSONAGGIO è CAMBIATA NEI METODI UPDATE_FRAME, CHECK_COLLISION_GROUND, DASH_ATTACK, CHECK_EVENT! (findstr /n /i "self.current_texture" Class.py)
        self.set_texture()
        self.texture_dimension = self.texture["idle"][0].get_size()#width, height
        
        #position
        self.position = {"left": (self.screen_dimension[0]/2) - (self.texture_dimension[0]/2), "top": 50 - self.texture_dimension[1]}
        self.position["right"], self.position["bottom"] = self.position["left"] + self.texture_dimension[0],  self.position["top"] + self.texture_dimension[1]
        self.rect = pygame.Rect(self.position["left"], self.position["top"], self.texture_dimension[0], self.texture_dimension[1])
        
        #lo score indica il punteggio del personaggio, è calcolato in base all'altezza raggiunta e alle box distrutte
        self.score = [0, 0, 0]#[piattaforme saltate, score, altezza ultimo salto]
        
        
        #movements
        self.movements = [False, False]#sx, dx
        self.x_speed = [3, 3, 6]#[reset, corrente, massima]
        self.y_speed = 0#velocità verticale corpo
        self.acceleration = 0.1#aumento velocità per ciclo (y_speed)
        
        self.sprint = [1, 0, 2, False, 3]#[reset, attuali, massimi, flag, tick(quanto dura)]
        self.jumps = [4, 4, 4, False, -3, -6]#indica il numero di salti possibili, si resetta quando si tocca terra, [reset, attuali, max_jumps, flag, jump height, max jump height]
        
        #attack
        self.attack_range = [15, 15, 50] #[reset, current, max]
        self.dash = [False, [], pygame.Rect(0, 0, 0, 0), [], pygame.Rect(0, 0, 0, 0), 120, 200] #[flag, character center, animation center, character center 2, animation center 2, range, max range]
        
        #offset telecamera
        self.y_offset = 0
        
        #currency management
        self.money = 0
        
    def set_texture(self):#carica e inizializza tutte le texture necessarie al personaggio
        self.texture = {"idle": [], "walking": [], "jump1": [], "jump2": [], "falling": [], "sprinting": []} #contiene tutte le texture del personaggio
        self.effect_texture = {"dash": [], "jump_effect": [0, 4]}#contiene le texture degli effetti che vengono mostrati in parallelo al personaggio
        
        for x in range(3):#caricamento dei frame del personaggio; se aggiungi altri frame cambia l'indice 
            self.texture["idle"].append(pygame.image.load(r"assets\player\idle\character_idle_{:}.png".format(x+1)))
            self.texture["jump1"].append(pygame.image.load(r"assets\player\jump1\character_jump1_{:}.png".format(x+1)))
        
        for x in range(14):
            self.effect_texture["dash"].append(pygame.image.load(r"assets\player\dash\dash_effect_{:}.png".format(x+1)))
        
        for x in range (7):
            self.texture["jump2"].append(pygame.image.load(r"assets\player\jump2\character_jump2_{:}.png".format(x+1)))
        
        self.effect_texture["jump_effect"][0] = pygame.image.load(r"assets\player\jump2\character_jump2_effect_2.png")#inserisce l'effetto del salto
        
        self.current_texture = "idle"
        self.current_frame = 0
        self.image = self.texture["idle"][0]
        
        self.current_effect_texture = ["none", "none"]#[0] = animation1, [1] = animation2; eseguire animazioni in parallelo
        self.current_effect_frame = [0, 13]
        self.effect_image = ["none", "none"]
    
    #aggiorna le variabili di posizione del personaggio; si consiglia eseguire dopo ogni cambiamento.
    def update_frame(self, texture_changed = False) -> None:
        if texture_changed:
            self.current_frame = 0
        
        self.current_frame += 0.075

        if self.current_frame >= len(self.texture[self.current_texture]):
            if self.current_texture == "jump2":
                self.current_frame = 3
            else:
                self.current_frame = 0
    
        self.image = self.texture[self.current_texture][int(self.current_frame)]
        self.texture_dimension = self.image.get_size()
    
    #viene modificato, eventualmente, il frame dei un effetto
    def update_effect_frame(self, update_speed, animation, dash) -> None:
        if self.current_effect_texture[animation] == "none":#se l'effetto è terminato la funzione si chiude
            return
        
        self.current_effect_frame[animation] += update_speed#aggiorna il frame dell'effetto
        
        #gestisce le due istanze di dash, inizio e arrivo, la seconda va al contrario quindi termina a 0
        if int(self.current_effect_frame[0]) >= len(self.effect_texture[self.current_effect_texture[animation]]):
            self.current_effect_frame[0] = 0
            self.current_effect_texture[0] = "none"
            self.effect_image[0] = "none"
            return
        if int(self.current_effect_frame[1]) <= 0:
            self.current_effect_frame[1] = 13
            self.current_effect_texture[1] = "none"
            self.effect_image[1] = "none"
            return
            
        try:#se l'effetto non è presente nella lista la funzione si chiude, il problema si riscontra con "none"
            self.effect_image[animation] = self.effect_texture[self.current_effect_texture[animation]][int(self.current_effect_frame[animation])]
            self.dash[dash] = self.effect_image[animation].get_rect()
            self.dash[dash].center = self.dash[dash-1]
        except KeyError:
            return
    
    def update_position(self):
        self.position["right"], self.position["bottom"] = self.position["left"] + self.texture_dimension[0],  self.position["top"] + self.texture_dimension[1]
        self.position["top"] = self.position["bottom"] - self.texture_dimension[1]
        self.rect.x = self.position["left"]
        self.rect.y = self.position["top"]
    
    #funzioni di movimento e di collisione
    def vertical_movement(self):
        #fa muovere verticlmente il personaggio
        if self.position["bottom"] <= self.screen_dimension[1]:
            self.position["top"] += self.y_speed
            self.y_speed += self.acceleration
    
    def horizontal_movement(self):
        #verifica lo sprint del personaggio
        if self.sprint[4] > 0 and self.sprint[3]:#lo sprint dura per due tick, ad ogni tick viene sottratto 1 alla durata(sprint[2])
            self.sprint[4] -= 1
        
        if self.sprint[4] == 0:#se la durata è terminata allora la velocità è riportata a 0, e la flag sprint a false
            self.x_speed[1] = self.x_speed[0]#velocità normale di reset
            self.sprint[3] = False
            self.sprint[4] = 3
        
        self.position["left"] += (self.movements[1] - self.movements[0]) * self.x_speed[1]
    
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
        elif self.position["bottom"] >= self.screen_dimension[1]:
            self.position["top"] = self.screen_dimension[1] - self.texture_dimension[1]
            if not self.jumps[3]:#se non si sta facendo un salto la velocità è 0, in caso contrario non è modificata
                self.y_speed = 0
                self.jumps[1] = self.jumps[0]
                self.jumps[3] = False
                self.current_texture = "idle"
                self.dash[0] = False
            
            if self.jumps[3]:
                self.jumps[1] = self.jumps[0]
                self.jumps[1] -= 1
                self.jumps[3] = False

            #resetta il numero di salti e sprint possibili
            self.sprint[1] = self.sprint[0]
            self.jumps[3] = False
            self.jumps[1] = self.jumps[0]
            
    
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
    
    #tutti i metodi seguenti sono da usare nella classe Game, siccome la lista che richiedono è memorizzata solamente li
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
            
            #verify if the character is on top or under the platform, considering the platform's horizontal range
            if within_horizontal_bounds:
                on_the_top = (self.position["bottom"] > piattaforma.rect.top and self.position["bottom"] < piattaforma.rect.bottom)
                on_the_bottom = (piattaforma.rect.top+10 < self.position["top"] < piattaforma.rect.bottom)
                
                #verifica se il personaggio si trova sotto la piattaforma
                if on_the_bottom:
                    self.position["top"] = piattaforma.rect.bottom 
                    self.y_speed = 0
                
                #verifica se il personaggio si trova sopra la piattaforma
                elif on_the_top:
                    #calcola lo score del personaggio
                    if piattaforma.rect.top < self.score[2]:
                        self.score[0] += 1
                        self.score[1] = piattaforma.rect.top/4
                        self.score[2] = piattaforma.rect.top
                        
                    self.position["top"] = piattaforma.rect.top - self.texture_dimension[1]
                    if not self.jumps[3]:#se non si sta facendo un salto la velocità è 0, in caso contrario non è modificata
                        self.y_speed = 0
                        self.jumps[1] = self.jumps[0]
                        self.jumps[3] = False
                        self.current_texture = "idle"
                        self.dash[0] = False
                    
                    if self.jumps[3]:
                        self.jumps[1] = self.jumps[0]
                        self.jumps[1] -= 1
                        self.jumps[3] = False

                    #resetta il numero di salti e sprint possibili
                    self.sprint[1] = self.sprint[0]

    #delete every last bit of the box presence in the program
    def delete_box(self, boxes:list, box, platform_list:list, screen) -> str:
        def create_currency():
            #genera una quantità di soldi ongi volta che si distrugge una cassa
            currecny_chance = [1, 2, 3, 4, 5, 6, 7, 8, 9]#soldi che si possono ottenere
            currecny_weights = [90, 80, 70, 60, 50, 40, 30, 20, 10]#probabilità di ottenere i soldi
            currency_get = random.choices(population= currecny_chance, weights=currecny_weights, k=1)
            self.money += currency_get[0]#aggiunge i soldi ottenuti al totale
        
        def create_upgrade() -> str:
            upgrade_chance = ["up_jump", "up_speed", "up_attackRange", "up_dashRange", "up_jumpNumber", "up_sprintNumber", "nothing"]#upgrade che si possono ottenere
            upgrade_weights = [12, 11, 14, 8, 7, 7, 41]#probabilità di ottenere i soldi
            upgrade = random.choices(population= upgrade_chance, weights=upgrade_weights, k=1)[0]
            match upgrade:
                case "up_jump":
                    if self.jumps[4] > self.jumps[5]:
                        self.jumps[3] -= 0.2
                        return "Jump height increased by 0.2"
                    return "Jump height already at maximum"
                
                case "up_speed":
                    if self.x_speed[0] < self.x_speed[2]:
                        self.x_speed[0] += 0.1
                        return "Speed increased by 0.1"
                    return "Speed already at maximum"
                                    
                case "up_attackRange":
                    if self.attack_range[1] < self.attack_range[2]:
                        self.attack_range[1] += 1.5
                        return "Attack range increased by 1.5"
                    return "Attack range already at maximum"
                    
                case "up_dashRange":
                    if self.dash[5] < self.dash[6]:
                        self.dash[5] += 5
                        return "Dash range increased by 5"
                    return "Dash range already at maximum"
                    
                case "up_jumpNumber":
                    if self.jumps[0] < self.jumps[2]:
                        self.jumps[0] += 1
                        return "Jump number increased by 1"
                    return "Jump number already at maximum"
                
                case "up_sprintNumber":
                    if self.sprint[0] < self.sprint[2]:
                        self.sprint[0] += 1
                        return "Sprint number increased by 1"
                    return "Sprint number already at maximum"
                
                case "nothing":
                    return ""
            
        platform = box.platform
        boxes.pop(boxes.index(box))
        platform_list[platform_list.index(platform)].box_there[0] = False
        platform_list[platform_list.index(platform)].box_there[1] = 0
        
        self.score[1] -= random.randint(10, 50)
        
        create_currency()
        message = create_upgrade()
        return message, 5
        
    def attack(self, boxes:list, platform:list, screen) -> str:
        message = ""
        energy_use = 0
        for box in boxes:
            #verify that the box and the character are on the same y coordinate, if not it proceed in the boxes list
            if not (box.rect.top < self.rect.centery and box.rect.bottom > self.rect.centery):
                continue
            #following the character perspective
            in_range_right = self.position["right"] + self.attack_range[1] > box.rect.left
            in_range_left = self.position["left"] - self.attack_range[1] < box.rect.right
            on_the_right = self.position["right"] < box.rect.right
            on_the_left = self.position["left"] > box.rect.left
            
            #if the character is not moving it attacks all around him
            if self.movements[0] == self.movements[1]:
                if (in_range_right and on_the_right) or (in_range_left and on_the_left):
                    message, energy_use = self.delete_box(boxes, box, platform, screen)
                    return message, energy_use
            
            #moving on the left
            elif self.movements[0]:
                if in_range_left and on_the_left:
                    message, energy_use = self.delete_box(boxes, box, platform, screen)
                    return message, energy_use
            
            #moving on the right
            elif self.movements[1]:
                if in_range_right and on_the_right:
                    message, energy_use = self.delete_box(boxes, box, platform, screen)
                    return message, energy_use
        
        return message, energy_use

    #the following method are used for the auto aim system for boxes
    def line_intersection(self, line1_start, line1_end, line2_start, line2_end):
        x1, y1 = line1_start
        x2, y2 = line1_end
        x3, y3 = line2_start
        x4, y4 = line2_end

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return False  # Le linee sono parallele o coincidenti

        #-t- and -u- are parameters used to determine if and where the line segments intersect 
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom #intersezione su segmento 1
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom #intersezione su segmento 2

        if 0 <= t <= 1 and 0 <= u <= 1:
            return True

        return False
    
    def line_intersects_rect(self, line_start, line_end, platform):
        for plat in platform:
            # Ottieni i quattro lati del rettangolo
            rect_lines = [
                (plat.rect.topleft, plat.rect.topright),
                (plat.rect.topright, plat.rect.bottomright),
                (plat.rect.bottomright, plat.rect.bottomleft),
                (plat.rect.bottomleft, plat.rect.topleft)
            ]
            # Verifica l'intersezione con ciascun lato del rettangolo
            for rect_line_start, rect_line_end in rect_lines:
                if self.line_intersection(line_start, line_end, rect_line_start, rect_line_end):
                    return True
        
        return False
    
    def box_aim(self, boxes:list, platform:list, screen) -> str:
        #inside the method the character will aim to the nearest box, if there is one
        if not (self.y_speed > 1 or self.y_speed < -1 or self.jumps[3]):#verify that the character is not over a platform but mid-hair
            return "", 0
        
        char_x, char_y = self.rect.center#create the (x, y) coordinates of the character center
        nearer_box = [300, 0]#contiene la box alla quale mirare, se nearer_box[1] = 0 non esiste la box a qui mirare
        
        #cicla su tutte le box, verificando quali soddisfano le condizioni per l'auto aim, stabilendo la box più vicina
        for box in boxes:
            
            #create the (x, y) coordinates of the box center
            box_x, box_y = box.rect.center
            point_distance = math.sqrt(math.pow(box_x-char_x, 2) + math.pow(box_y-char_y, 2))
            
            #if the distance between the character and the box is too high
            if point_distance < 180 or point_distance > 180+self.dash[5]:
                continue

            #verifica che tra il personaggio e la box non ci siano piattaforme
            intersect = self.line_intersects_rect(line_start=(char_x, char_y), line_end=(box_x, box_y), platform=platform)
            if intersect:
                continue
            
            if point_distance < nearer_box[0]:
                nearer_box[0], nearer_box[1] = point_distance, box
        
        #se non c'è una box alla quale mirare chiude la funzione
        if nearer_box[1] == 0:
            return "", 0
        
        nearer_box[1].is_target = True

        #if self.dash[0] is true the character will teleport to the target box
        message, energy_use = self.dash_attack(boxes, nearer_box[1], platform, screen)
        return message, energy_use
    
    def dash_attack(self, boxes:list, box, platform:list, screen) -> str:
        energy_use = 0
        if self.dash[0]:
            #set the animation of the dash_start
            self.current_effect_texture[0], self.current_effect_texture[1] = "dash", "dash"
            self.dash[1] = (self.rect.center)#memorizza la posizione iniziale del dash
            
            #set the character position to the box position
            self.movements = [False, False]
            self.position["left"], self.position["top"] = box.rect.left, box.rect.top
            self.update_position()
            self.dash[0] = False
            self.y_speed = 0
            message, energy_use = self.delete_box(boxes, box, platform, screen)
            
            #set the animation of dash_arrival
            self.dash[3] = (self.rect.center)
            return message, energy_use
        return "", 0
    
    def reset(self):
        #resetta le variabili del personaggio
        self.score = [0, 0, 0]
        self.movements = [False, False]
        self.x_speed = [3, 3, 6]
        self.y_speed = 0
        
        self.sprint = [1, 0, 2, False, 3]
        self.jumps = [4, 4, 4, False, -3, -6]
        
        self.attack_range = [15, 15, 50]
        self.dash = [False, [], pygame.Rect(0, 0, 0, 0), [], pygame.Rect(0, 0, 0, 0), 120, 200]
        
        self.position = {"left": (self.screen_dimension[0]/2) - (self.texture_dimension[0]/2), "top": self.screen_dimension[1] - self.texture_dimension[1] -10}
        self.update_position()
        

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
        
        self.target = pygame.image.load(r"assets\object\red_aim_box.png")
        self.target_size = self.target.get_size()
        
        self.is_target = False
