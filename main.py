import pygame
import os
import random
pygame.font.init() #We use it to display text

# Creating the screen
WIDTH, HEIGHT = 800, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders game")

# Loading enemy spaceship
ENEMY1 = pygame.image.load(os.path.join("assets", "ufo.png"))
ENEMY2 = pygame.image.load(os.path.join("assets", "ufo2.png"))
ENEMY3 = pygame.image.load(os.path.join("assets", "aircraft.png"))
ENEMY4 = pygame.image.load(os.path.join("assets", "alien.png"))
ENEMY5 = pygame.image.load(os.path.join("assets", "ufo3.png"))

# Loading player spaceship
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "spaceship.png"))


# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (WIDTH, HEIGHT)) #We use transform.scale inorder to fill the screen

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # When we shoot laser moves up the screen
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship: # This is an abstract class which means you inherit from this class but do not use it directly.
    COOLDOWN = 30 # This is responsible to how fast you can shoot after one shoot. This regards with our FPS

    def __init__(self, x, y, health=100):
        # x and y values of the ship (co-ordinates)
        self.x = x
        self.y = y # These set attributes for ship so that each ship can store x and y values
        self.health = health # Initial health is set to 100
        # Inititial values are setup
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # Image of laser is drawn every time after 30FPS approximately which half of our FPS
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # Gets height and width of the ship
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)# It helps in picture collision. It lets know that where the pixels are and where it is not. It helps in collision
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    # We are defining enemy dictionary 
    ENEMY_DICT = {
                "enemy1": (ENEMY1, RED_LASER),
                "enemy2": (ENEMY2, GREEN_LASER),
                "enemy3": (ENEMY3, BLUE_LASER),
                "enemy4": (ENEMY4, BLUE_LASER),
                "enemy5": (ENEMY5, GREEN_LASER),
                }

    def __init__(self, x, y, enemy, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.ENEMY_DICT[enemy]
        self.mask = pygame.mask.from_surface(self.ship_img) # Mask is used for collisions it gets the pixels of the image

    def move(self, velocity):
        self.y += velocity # We increment only the y value because enemy ship only comes from up to down

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



# We need this to find the actual collision. Our images has transparent rectangular box around the whole image itself. But we do not need collision to happen when two transparent boxes collide.But instead we want the actual pixels of the img to collide when they collide. Which is my we use mask.overlap property. Sometimes the offset values might be negative but does not matter.
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # It returns none if none of them overlaps if it does it returns the point of intersection (x,y) 

def main():
    run = True
    FPS = 65 # It means we are going to show 65 frames every second
    clock = pygame.time.Clock() # We need this to show FPS 
    level = 0 # Initial level
    lives = 3 # Initial lives that we have
    main_font = pygame.font.SysFont("", 45)
    lost_font = pygame.font.SysFont("", 50)
    win_font = pygame.font.SysFont("", 50)

    enemies = [] # We keep our enemies in this array
    wave_length = 5 # Wave length is used to generate new set of enemies when we get to the next level
    enemy_vel = 1

    player_val = 5
    laser_vel = 5

    player = Player(300, 630) # Initail position of the space ship

    lost = False #lost is initially false coz we did not lose at the beginning
    won = False #won is initially false coz we did not win at the beginning
    lost_count = 0
    won_count = 0

    def redraw_window():
        WINDOW.blit(BG, (0,0))
        # draw text
        lives_text = main_font.render(f"Lives remaining: {lives}", 1, (242,227,17))
        level_text = main_font.render(f"The Current Level: {level}", 1, (85,242,17))

        WINDOW.blit(lives_text, (15, 15)) #Fixes the text in left top corner
        WINDOW.blit(level_text, (485,15)) #Fixes the text in right top corner

        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)
        # We can access this when we lost = True
        if lost:
            lost_text = lost_font.render("You Lost!!", 1, (255,255,255))
            WINDOW.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, 350))

        if won:
            won_text = win_font.render("You Won!!", 1, (255,255,255))
            WINDOW.blit(won_text, (WIDTH/2 - won_text.get_width()/2, 350))


        pygame.display.update() #It refershes the window

    while run:
        clock.tick(FPS) #We tick this clock based on FPS so it stays consistant in every device
        redraw_window()
        # We are checking if we win.
        if level == 5:
            won = True
            won_count += 1
        if won:
            if won_count > FPS * 3:
                run = False
            else:
                continue
        # We are checking if we lost.
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        # We can access this when we lost = True
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if len(enemies) == 0: # Initially enemies is empty array and level is 0 so when game starts we move on to level 1 with 10 enemies
            level += 1
            wave_length += 5 # For each level we are incrementing 5 enemies so in level1 we have 10 enemies as in level0 we have five enemies
            # In this for loop we are spaning enemies above the screen randomly so that they do not come at the same time
            for i in range(wave_length):
                                # This is the x range.        This is the y range initially     Enemies of these 5 randomly spawns
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["enemy1", "enemy2", "enemy3","enemy4","enemy5"]))
                enemies.append(enemy)

        for event in pygame.event.get(): #We are looping through all the events that pygame knows since we are using pygame.event.get() and check either the event is occured or not. 
            if event.type == pygame.QUIT:
                quit() # run = False

        keys = pygame.key.get_pressed() # It gives a dictionary of all keys and say whether they are being pressed or not. And It helps to move diagonaly when two buttons are pressed.
        if keys[pygame.K_UP] and player.y - player_val > 0: # up
            player.y -= player_val
        if keys[pygame.K_DOWN] and player.y + player_val + player.get_height() + 15 < HEIGHT: # down
            player.y += player_val
        if keys[pygame.K_LEFT] and player.x - player_val > 0: # left
            player.x -= player_val
        if keys[pygame.K_RIGHT] and player.x + player_val + player.get_width() < WIDTH: # right
            player.x += player_val
        
        if keys[pygame.K_SPACE]:
            player.shoot()

        # For each enemy we are drawing it on screen. [:] means we are taking a copy of enemies array
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            # If player hits the enemy our enemy disappears and we lose 10 heath points
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy) # We remove the enemy from the array
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("", 50)
    rule_font = pygame.font.SysFont("", 30)
    run = True
    while run:
        WINDOW.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        rule_label1 = rule_font.render("RULES:Press arrow key to move. Press spacebar to shoot.", 1, (255,255,255))
        rule_label2 = rule_font.render("Avoid lasers, complete five levels to win.", 1, (255,255,255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        WINDOW.blit(rule_label1, (WIDTH/2 - title_label.get_width()/2, 400))
        WINDOW.blit(rule_label2, (WIDTH/2 - title_label.get_width()/2, 420))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()