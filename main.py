import pgzrun
import random

# Screen dimensions (constant names capitalized)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MID_WIDTH, MID_HEIGHT = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Shared settings
actor_speed_range = [1, 2]  # Reduced speed for enemies
actor_anim_step = 10

# Actor definition
def create_actor(image_prefix, start_position, initial_speed, num_frames):
    animation_list = [f"{image_prefix}_idle_{i+1}" for i in range(num_frames)]
    return {
        "actor": Actor(animation_list[0], pos=start_position),
        "animation_frames": animation_list,
        "current_frame": 0,
        "frame_timer": 0,
        "speed": initial_speed
    }

# Hero definition
hero = create_actor("hero", (MID_WIDTH, MID_HEIGHT), 3, 2)

# Function to create enemies
def create_enemies(num_of_enemies):
    list_of_enemies = []
    for _ in range(num_of_enemies):
        start_x = random.randint(50, SCREEN_WIDTH - 50)
        start_y = random.randint(50, SCREEN_HEIGHT - 50)
        speed = random.choice(actor_speed_range)
        enemy = create_actor("enemy", (start_x, start_y), speed, 2)
        list_of_enemies.append(enemy)
    return list_of_enemies

# Create enemies
enemies = create_enemies(2)

# Lasers
lasers = []
def fire_laser():
    try:
        laser = Actor("laser", pos=hero["actor"].pos)
        lasers.append(laser)
    except Exception as e:
        print(f"Error while firing laser: {e}")

# Sounds and music
sound_mapping = {
    "game_won": sounds.win,
    "game_lost": sounds.lose
}

# State mapping
GAME_STATE_MAP = {"MENU": 0, "PLAYING": 1, "GAMEOVER": 2}
CURRENT_STATE = GAME_STATE_MAP["MENU"]

# Game variables
game_score = 0

# Rendering functions
def render_game():
    screen.clear()
    if CURRENT_STATE == GAME_STATE_MAP["MENU"]:
        _display_menu()
    elif CURRENT_STATE == GAME_STATE_MAP["PLAYING"]:
        _display_playing_state()
    elif CURRENT_STATE == GAME_STATE_MAP["GAMEOVER"]:
        _display_gameover()

def _display_menu():
    screen.fill("darkblue")
    screen.draw.text("ROGUELIKE GAME", center=(MID_WIDTH, SCREEN_HEIGHT // 3), color="white", fontsize=50)
    screen.draw.text("1. Start Game", center=(MID_WIDTH, MID_HEIGHT), color="white", fontsize=30)
    screen.draw.text("2. Exit", center=(MID_WIDTH, MID_HEIGHT + 50), color="white", fontsize=30)

def _display_playing_state():
    # Draw the space background
    screen.blit("space_background", (0, 0))  # Make sure "space_background" exists in images folder
    hero["actor"].draw()
    for enemy in enemies:
        enemy["actor"].draw()
    for laser in lasers:
        laser.draw()
    screen.draw.text(f"Score: {game_score}", (10, 10), color="white", fontsize=24)

def _display_gameover():
    screen.fill("black")
    screen.draw.text("Game Over!", center=(MID_WIDTH, MID_HEIGHT), color="red", fontsize=50)
    screen.draw.text(f"Final Score: {game_score}", center=(MID_WIDTH, MID_HEIGHT + 50), color="white", fontsize=40)
    screen.draw.text("Press ENTER to return to the menu", center=(MID_WIDTH, MID_HEIGHT + 100), color="white", fontsize=30)

# Game state control
def control_state():
    if CURRENT_STATE == GAME_STATE_MAP["PLAYING"]:
        _manage_hero()
        _manage_enemies()
        _manage_lasers()
        _manage_collisions()

# Hero management
def _manage_hero():
    speed = hero["speed"]
    actr = hero["actor"]
    if keyboard.left and actr.x > 0:
        actr.x -= speed
    if keyboard.right and actr.x < SCREEN_WIDTH:
        actr.x += speed
    if keyboard.up and actr.y > 0:
        actr.y -= speed
    if keyboard.down and actr.y < SCREEN_HEIGHT:
        actr.y += speed
    _manage_animation(hero)

# Enemy management
def _manage_enemies():
    for enemy in enemies:
        enm = enemy["actor"]
        dx = hero["actor"].x - enm.x
        dy = hero["actor"].y - enm.y
        dist = (dx**2 + dy**2) ** 0.5
        speed = enemy["speed"]
        if dist > 0:
            enm.x += (dx / dist) * speed
            enm.y += (dy / dist) * speed
        _manage_animation(enemy)

# Laser management
def _manage_lasers():
    global game_score
    for laser in lasers[:]:
        laser.y -= 5  # Move laser upwards
        if laser.y < 0:
            lasers.remove(laser)
        else:
            for enemy in enemies[:]:
                if laser.colliderect(enemy["actor"]):
                    enemies.remove(enemy)  # Remove the hit enemy
                    lasers.remove(laser)  # Remove the laser
                    game_score += 10

                    # Add a new enemy when one is killed
                    new_enemy = create_actor(
                        "enemy",
                        (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)),
                        random.choice(actor_speed_range),
                        2
                    )
                    enemies.append(new_enemy)
                    break

# Animation management
def _manage_animation(sprite):
    sprite["frame_timer"] += 1
    if sprite["frame_timer"] > actor_anim_step:
        frames = len(sprite["animation_frames"])
        sprite["current_frame"] = (sprite["current_frame"] + 1) % frames
        sprite["actor"].image = sprite["animation_frames"][sprite["current_frame"]]
        sprite["frame_timer"] = 0

# Collision management
def _manage_collisions():
    global CURRENT_STATE
    for enemy in enemies:
        if hero["actor"].colliderect(enemy["actor"]):
            CURRENT_STATE = GAME_STATE_MAP["GAMEOVER"]
            sound_mapping["game_lost"].play()

# Keyboard input management
def manage_keyboard_inputs(key):
    global CURRENT_STATE
    if CURRENT_STATE == GAME_STATE_MAP["MENU"]:
        if key == keys.K_1:
            _game_begin()
        elif key == keys.K_2:
            exit()
    elif CURRENT_STATE == GAME_STATE_MAP["GAMEOVER"] and key == keys.RETURN:
        CURRENT_STATE = GAME_STATE_MAP["MENU"]
    elif key == keys.SPACE and CURRENT_STATE == GAME_STATE_MAP["PLAYING"]:  # Lazer fırlatma
        fire_laser()

def _game_begin():
    global CURRENT_STATE, game_score
    CURRENT_STATE = GAME_STATE_MAP["PLAYING"]
    game_score = 0
    hero["actor"].pos = (MID_WIDTH, MID_HEIGHT)
    for enemy in enemies:
        enemy["actor"].pos = (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50))

# Pygame Zero functions
def draw():
    render_game()

def update():
    control_state()

def on_key_down(key):
    manage_keyboard_inputs(key)

pgzrun.go()
