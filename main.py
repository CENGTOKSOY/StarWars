import pgzrun
import random
from pygame import mouse

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MID_WIDTH, MID_HEIGHT = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
class Button:
    def __init__(self, text, pos, width=200, height=50, color_normal="blue", color_hover="lightblue", color_click="darkblue"):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_click = color_click
        self.current_color = color_normal
        self.is_hovered = False
        self.is_clicked = False

    def draw(self):
        screen.draw.filled_rect(self.get_rect(), self.current_color)
        screen.draw.text(self.text, center=self.pos, fontsize=30, color="white")

    def get_rect(self):
        return Rect((self.pos[0] - self.width // 2, self.pos[1] - self.height // 2), (self.width, self.height))

    def update(self, mouse_pos, mouse_clicked):
        self.is_hovered = self.get_rect().collidepoint(mouse_pos)
        self.is_clicked = self.is_hovered and mouse_clicked

        if self.is_clicked:
            self.current_color = self.color_click
        elif self.is_hovered:
            self.current_color = self.color_hover
        else:
            self.current_color = self.color_normal
class Slider:
    def __init__(self, pos, width=200, height=10, min_value=1, max_value=3):
        self.pos = pos
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value  # Başlangıç değeri
        self.dragging = False  # Slider sürükleniyor mu?

    def draw(self):
        # Slider çubuğunu çiz
        screen.draw.filled_rect(Rect((self.pos[0] - self.width // 2, self.pos[1] - self.height // 2), (self.width, self.height)), "gray")
        # Slider düğmesini çiz
        button_x = self.pos[0] - self.width // 2 + (self.value - self.min_value) * (self.width / (self.max_value - self.min_value))
        screen.draw.filled_circle((button_x, self.pos[1]), 10, "blue")

    def update(self, mouse_pos, mouse_clicked):
        button_x = self.pos[0] - self.width // 2 + (self.value - self.min_value) * (self.width / (self.max_value - self.min_value))
        button_rect = Rect((button_x - 10, self.pos[1] - 10), (20, 20))

        if button_rect.collidepoint(mouse_pos):
            if mouse_clicked:
                self.dragging = True
        if not mouse_clicked:
            self.dragging = False

        if self.dragging:
            relative_x = mouse_pos[0] - (self.pos[0] - self.width // 2)
            self.value = self.min_value + (relative_x / self.width) * (self.max_value - self.min_value)
            self.value = max(self.min_value, min(self.max_value, self.value))  # Değeri sınırla

    def get_difficulty(self):
        if self.value < 1.5:
            return "Easy"
        elif self.value < 2.5:
            return "Medium"
        else:
            return "Hard"

class Character:
    def __init__(self, image_prefix, pos, speed, num_frames):
        self.animation_frames = [f"{image_prefix}_idle_{i + 1}" for i in range(num_frames)]
        self.actor = Actor(self.animation_frames[0], pos=pos)
        self.current_frame = 0
        self.frame_timer = 0
        self.speed = speed

    def update_animation(self):
        self.frame_timer += 1
        if self.frame_timer > 10:  # Animasyon hızı
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.actor.image = self.animation_frames[self.current_frame]
            self.frame_timer = 0

    def draw(self):
        self.actor.draw()

class Enemy(Character):
    def __init__(self, image_prefix, pos, speed, num_frames):
        super().__init__(image_prefix, pos, speed, num_frames)
        self.move_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.lasers = []  # Düşmanın lazerleri
        self.fire_timer = random.randint(30, 100)  # Lazer ateşleme aralığı

    def move(self):
        self.actor.x += self.move_direction[0] * self.speed
        self.actor.y += self.move_direction[1] * self.speed
        if self.actor.left < 0 or self.actor.right > SCREEN_WIDTH:
            self.move_direction = (-self.move_direction[0], self.move_direction[1])
        if self.actor.top < 0 or self.actor.bottom > SCREEN_HEIGHT:
            self.move_direction = (self.move_direction[0], -self.move_direction[1])

    def fire_laser(self):
        self.lasers.append(Laser(self.actor.pos, direction=1))  # Aşağıya lazer ateşle

    def update_lasers(self):
        self.fire_timer -= 1
        if self.fire_timer <= 0:
            self.fire_laser()
            self.fire_timer = random.randint(60, 120)  # Lazer ateşleme zamanını sıfırla
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
        self.direction = direction  # -1 yukarı, 1 aşağı

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
sound_enabled = True  # Sesin açık/kapalı olduğunu tutan değişken
difficulty_slider = Slider((MID_WIDTH, MID_HEIGHT + 150))  # Zorluk seviyesi slider'ı

buttons = [
    Button("Start Game", (MID_WIDTH, MID_HEIGHT - 80)),  # Başlangıç butonu
    Button("Toggle Sound", (MID_WIDTH, MID_HEIGHT)),     # Ses açma/kapama butonu
    Button("Exit", (MID_WIDTH, MID_HEIGHT + 80))         # Çıkış butonu
]

def play_background_music():
    global background_music_playing
    if not background_music_playing and sound_enabled:
        sounds.background.play(-1)  # Arka plan müziğini döngüye al
        background_music_playing = True

def stop_background_music():
    global background_music_playing
    if background_music_playing:
        sounds.background.stop()
        background_music_playing = False

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    if not sound_enabled:
        stop_background_music()
    else:
        play_background_music()

def spawn_enemy():
    start_x = random.randint(50, SCREEN_WIDTH - 50)
    start_y = random.randint(50, SCREEN_HEIGHT - 50)

    if difficulty_slider.get_difficulty() == "Easy":
        speed = random.uniform(1.0, 1.5)
    elif difficulty_slider.get_difficulty() == "Medium":
        speed = random.uniform(1.5, 2.0)
    else:
        speed = random.uniform(2.0, 2.5)
    enemies.append(Enemy("enemy", (start_x, start_y), speed, num_frames=2))

def fire_laser():
    lasers.append(Laser(hero.actor.pos, direction=-1))
    if sound_enabled:
        sounds.laser.play()

def start_game():
    global current_state, game_score, enemies
    current_state = GAME_STATE_MAP["PLAYING"]
    game_score = 0
    hero.actor.pos = (MID_WIDTH, MID_HEIGHT)
    enemies = []

    if difficulty_slider.get_difficulty() == "Easy":
        num_enemies = 2
    elif difficulty_slider.get_difficulty() == "Medium":
        num_enemies = 3
    else:  # Hard
        num_enemies = 4
    for _ in range(num_enemies):
        spawn_enemy()


def draw():
    screen.clear()
    if current_state == GAME_STATE_MAP["MENU"]:
        screen.fill("darkblue")

        screen.draw.text("STAR WARS GAME", center=(MID_WIDTH, SCREEN_HEIGHT // 4), color="white", fontsize=50)
        for button in buttons:
            button.draw()

        sound_status = "ON" if sound_enabled else "OFF"
        screen.draw.text(f"Sound: {sound_status}", center=(MID_WIDTH, MID_HEIGHT + 120), color="white", fontsize=24)

        difficulty_slider.draw()
        screen.draw.text(f"Difficulty: {difficulty_slider.get_difficulty()}", center=(MID_WIDTH, MID_HEIGHT + 180), color="white", fontsize=24)
    elif current_state == GAME_STATE_MAP["PLAYING"]:
        screen.blit("space_background", (0, 0))
        hero.draw()
        for enemy in enemies:
            enemy.draw()
            enemy.draw_lasers()
        for laser in lasers:
            laser.draw()
        screen.draw.text(f"Score: {game_score}", (10, 10), color="white", fontsize=24)
    elif current_state == GAME_STATE_MAP["GAMEOVER"]:
        screen.fill("black")
        screen.draw.text("Game Over!", center=(MID_WIDTH, MID_HEIGHT), color="red", fontsize=50)
        screen.draw.text(f"Final Score: {game_score}", center=(MID_WIDTH, MID_HEIGHT + 50), color="white", fontsize=40)
        screen.draw.text("Press ENTER to return to the menu", center=(MID_WIDTH, MID_HEIGHT + 100), color="white", fontsize=30)


def update():
    global current_state, game_score
    mouse_pos = mouse.get_pos()
    mouse_clicked = mouse.get_pressed()[0]

    for button in buttons:
        button.update(mouse_pos, mouse_clicked)

    difficulty_slider.update(mouse_pos, mouse_clicked)

    if current_state == GAME_STATE_MAP["MENU"]:
        if buttons[0].is_clicked:
            start_game()
        elif buttons[1].is_clicked:
            toggle_sound()
        elif buttons[2].is_clicked:
            exit()
    elif current_state == GAME_STATE_MAP["PLAYING"]:
        play_background_music()
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
                if sound_enabled:
                    sounds.lose.play()
                current_state = GAME_STATE_MAP["GAMEOVER"]
                stop_background_music()

            for laser in enemy.lasers:
                if laser.actor.colliderect(hero.actor):
                    if sound_enabled:
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
                        if sound_enabled:
                            sounds.explosion.play()
                        if game_score % 100 == 0 and sound_enabled:
                            sounds.win.play()


        if difficulty_slider.get_difficulty() == "Easy":
            max_enemies = 1
        elif difficulty_slider.get_difficulty() == "Medium":
            max_enemies = 3
        else:
            max_enemies = 7
        if len(enemies) < max_enemies:
            spawn_enemy()
    elif current_state == GAME_STATE_MAP["GAMEOVER"] and keyboard.RETURN:
        current_state = GAME_STATE_MAP["MENU"]

def on_key_down(key):
    if key == keys.SPACE and current_state == GAME_STATE_MAP["PLAYING"]:
        fire_laser()

pgzrun.go()