import pgzrun
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MID_WIDTH, MID_HEIGHT = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
class Character:
    def __init__(self, image_prefix, pos, speed, num_frames):
        self.animation_frames = [f"{image_prefix}_idle_{i + 1}" for i in range(num_frames)]
        self.actor = Actor(self.animation_frames[0], pos=pos)
        self.current_frame = 0
        self.frame_timer = 0
        self.speed = speed
    def update_animation(self):
        self.frame_timer += 1
        if self.frame_timer > 10:  # Adjust frame step as needed
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.actor.image = self.animation_frames[self.current_frame]
            self.frame_timer = 0

    def draw(self):
        self.actor.draw()
class Enemy(Character):
    def __init__(self, image_prefix, pos, speed, num_frames):
        super().__init__(image_prefix, pos, speed, num_frames)
        self.move_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.lasers = []  # Lasers fired by the enemy
        self.fire_timer = random.randint(30, 100)  # Randomized fire intervals

    def move(self):
        self.actor.x += self.move_direction[0] * self.speed
        self.actor.y += self.move_direction[1] * self.speed
        if self.actor.left < 0 or self.actor.right > SCREEN_WIDTH:
            self.move_direction = (-self.move_direction[0], self.move_direction[1])
        if self.actor.top < 0 or self.actor.bottom > SCREEN_HEIGHT:
            self.move_direction = (self.move_direction[0], -self.move_direction[1])

    def fire_laser(self):
        self.lasers.append(Laser(self.actor.pos, direction=1))  # Fire downward

    def update_lasers(self):
        self.fire_timer -= 1
        if self.fire_timer <= 0:
            self.fire_laser()
            self.fire_timer = random.randint(60, 120)  # Reset timer
        for laser in self.lasers[:]:
            laser.move()
            if laser.actor.top > SCREEN_HEIGHT:
                self.lasers.remove(laser)

    def draw_lasers(self):
        for laser in self.lasers:
            laser.draw()

class Laser:
    def __init__(self, pos, direction):
        self.actor = Actor("laser", pos=pos)
        self.direction = direction  # -1 for upward, 1 for downward

    def move(self):
        self.actor.y += 5 * self.direction

    def draw(self):
        self.actor.draw()

hero = Character("hero", (MID_WIDTH, MID_HEIGHT), speed=3, num_frames=2)
lasers = []
enemies = []

GAME_STATE_MAP = {"MENU": 0, "PLAYING": 1, "GAMEOVER": 2}
current_state = GAME_STATE_MAP["MENU"]
game_score = 0
background_music_playing = False

def play_background_music():
    global background_music_playing
    if not background_music_playing:
        sounds.background.play(-1)  # Loop background music
        background_music_playing = True

def stop_background_music():
    global background_music_playing
    if background_music_playing:
        sounds.background.stop()
        background_music_playing = False

def spawn_enemy():
    start_x = random.randint(50, SCREEN_WIDTH - 50)
    start_y = random.randint(50, SCREEN_HEIGHT - 50)
    speed = random.uniform(1.0, 2.0)  # Slower enemies
    enemies.append(Enemy("enemy", (start_x, start_y), speed, num_frames=2))

def fire_laser():
    lasers.append(Laser(hero.actor.pos, direction=-1))  # Hero fires upward
    sounds.laser.play()  # Play laser firing sound

def render_game():
    screen.clear()
    screen.blit("space_background", (0, 0))  # Background image
    if current_state == GAME_STATE_MAP["MENU"]:
        _display_menu()
    elif current_state == GAME_STATE_MAP["PLAYING"]:
        _display_playing_state()
    elif current_state == GAME_STATE_MAP["GAMEOVER"]:
        _display_gameover()
def _display_menu():
    screen.fill("darkblue")
    screen.draw.text("ROGUELIKE GAME", center=(MID_WIDTH, SCREEN_HEIGHT // 3), color="white", fontsize=50)
    screen.draw.text("1. Start Game", center=(MID_WIDTH, MID_HEIGHT), color="white", fontsize=30)
    screen.draw.text("2. Exit", center=(MID_WIDTH, MID_HEIGHT + 50), color="white", fontsize=30)
def _display_playing_state():
    hero.draw()
    for enemy in enemies:
        enemy.draw()
        enemy.draw_lasers()
    for laser in lasers:
        laser.draw()
    screen.draw.text(f"Score: {game_score}", (10, 10), color="white", fontsize=24)
def _display_gameover():
    screen.fill("black")
    screen.draw.text("Game Over!", center=(MID_WIDTH, MID_HEIGHT), color="red", fontsize=50)
    screen.draw.text(f"Final Score: {game_score}", center=(MID_WIDTH, MID_HEIGHT + 50), color="white", fontsize=40)
    screen.draw.text("Press ENTER to return to the menu", center=(MID_WIDTH, MID_HEIGHT + 100), color="white", fontsize=30)
def update():
    global current_state, game_score
    play_background_music()
    if current_state == GAME_STATE_MAP["PLAYING"]:
        if keyboard.left and hero.actor.left > 0:
            hero.actor.x -= hero.speed
        if keyboard.right and hero.actor.right < SCREEN_WIDTH:
            hero.actor.x += hero.speed
        if keyboard.up and hero.actor.top > 0:
            hero.actor.y -= hero.speed
        if keyboard.down and hero.actor.bottom < SCREEN_HEIGHT:
            hero.actor.y += hero.speed

        hero.update_animation()

        for enemy in enemies:
            enemy.move()
            enemy.update_animation()
            enemy.update_lasers()
            if enemy.actor.colliderect(hero.actor):
                sounds.lose.play()
                current_state = GAME_STATE_MAP["GAMEOVER"]
                stop_background_music()

            for laser in enemy.lasers:
                if laser.actor.colliderect(hero.actor):
                    sounds.lose.play()
                    current_state = GAME_STATE_MAP["GAMEOVER"]
                    stop_background_music()

        for laser in lasers[:]:
            laser.move()
            if laser.actor.y < 0:
                lasers.remove(laser)
            else:
                for enemy in enemies[:]:
                    if laser.actor.colliderect(enemy.actor):
                        enemies.remove(enemy)
                        lasers.remove(laser)
                        game_score += 10
                        spawn_enemy()
                        sounds.explosion.play()  # Play enemy destruction sound
                        if game_score % 200 == 0:  # Play win sound every 200 points
                            sounds.win.play()

        if len(enemies) < 2:
            spawn_enemy()
def on_key_down(key):
    global current_state
    if current_state == GAME_STATE_MAP["MENU"]:
        if key == keys.K_1:
            _start_game()
        elif key == keys.K_2:
            exit()
    elif current_state == GAME_STATE_MAP["GAMEOVER"] and key == keys.RETURN:
        current_state = GAME_STATE_MAP["MENU"]
    elif key == keys.SPACE and current_state == GAME_STATE_MAP["PLAYING"]:
        fire_laser()
def _start_game():
    global current_state, game_score, enemies
    current_state = GAME_STATE_MAP["PLAYING"]
    game_score = 0
    hero.actor.pos = (MID_WIDTH, MID_HEIGHT)
    enemies = []
    for _ in range(3):
        spawn_enemy()
def draw():
    render_game()
pgzrun.go()