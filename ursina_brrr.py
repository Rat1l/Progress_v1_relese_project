from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time
import random

app = Ursina()

# ==== ІГРОВІ ЗМІННІ ====
player = FirstPersonController(collider='box')
player.hp = 100
player.max_hp = 100
player.bullets = 30
player.enabled = False  # спочатку гравець неактивний

sky_texture = load_texture("Skybox.png")
reload = False

# ==== HUD ====
gun_model = Entity(
    parent=camera.ui,
    model='shotgun 1.glb',
    scale=1,
    position=Vec2(0.4, -1),
    rotation=Vec3(-10, -20, 0),
    double_sided=True,
    enabled=False
)

bullets_text = Text(
    text=f'Bullets:{player.bullets}',
    parent=camera.ui,
    color=color.black,
    position=Vec2(-0.8, 0.4),
    scale=2,
    enabled=False
)

# Лічильник ворогів
enemy_count_text = Text(
    text='Enemies: 0',
    parent=camera.ui,
    color=color.black,
    position=Vec2(0.5, 0.4),
    scale=2,
    enabled=False
)

hp_bar_bg = Entity(
    parent=camera.ui,
    model='quad',
    color=color.black,
    scale=(0.5, 0.04),
    position=(-0.1, -0.4),
    enabled=False
)

hp_bar = Entity(
    parent=camera.ui,
    model='quad',
    color=color.red,
    scale=(0.4, 0.03),
    position=(-0.3, -0.4),
    origin_x=-.5,
    enabled=False
)

# ==== ПЛАТФОРМА ====
plot = Entity(parent=scene, model='cube', color=color.gray,
              scale=(100, 1, 100), collider='box')

Sky = Entity(parent=scene, model='Sphere', texture=sky_texture,
             scale=1500, double_sided=True)

# ==== МЕНЮ ====
menu_bg = Entity(parent=camera.ui, model='quad',
                 color=color.rgba(0, 0, 0, 180), scale=(2, 2))
title_text = Text(text='MY FPS GAME', origin=(0, 0), y=0.3,
                  scale=3, color=color.white)

play_button = Button(text='PLAY', scale=(0.2, 0.07), y=0.05,
                     color=color.white, text_color=color.black)

exit_button = Button(text='EXIT', scale=(0.2, 0.07), y=-0.1,
                     color=color.white, text_color=color.black)

# ==== GAME OVER ====
game_over_text = Text(text='GAME OVER', origin=(0, 0),
                      scale=4, color=color.red, enabled=False)

retry_button = Button(text='RETRY', position=(-0.1, -0.3), scale=(0.2, 0.05),
                      color=color.white, text_color=color.black, enabled=False)

# ==== СПИСКИ ====
enemies = []
walls = []
maze_map = []  # 2D карта лабіринту


# ==== ФУНКЦІЇ ====
def animation_gun():
    gun_model.animate_rotation(Vec3(-20, -20, 0), duration=0.1, curve=curve.out_expo)
    invoke(gun_model.animate_rotation, Vec3(-10, -20, 0), duration=0.1, curve=curve.in_expo, delay=0.1)


def update_enemy_count():
    """Оновлює текст із кількістю ворогів"""
    enemy_count_text.text = f'Enemies: {len(enemies)}'


def game_over():
    player.enabled = False
    mouse.locked = False

    gun_model.enabled = False
    bullets_text.enabled = False
    hp_bar.enabled = False
    hp_bar_bg.enabled = False
    enemy_count_text.enabled = False

    game_over_text.enabled = True
    retry_button.enabled = True

    for e in enemies:
        destroy(e)
    enemies.clear()


def go_to_menu():
    game_over_text.enabled = False
    retry_button.enabled = False

    menu_bg.enabled = True
    title_text.enabled = True
    play_button.enabled = True
    exit_button.enabled = True


retry_button.on_click = go_to_menu


def restart_game():
    player.hp = player.max_hp
    player.position = Vec3(0, 1, 0)
    player.bullets = 30
    bullets_text.text = f'Bullets:{player.bullets}'
    hp_bar.scale_x = 0.4

    for e in enemies:
        destroy(e)
    enemies.clear()
    for w in walls:
        destroy(w)
    walls.clear()
    maze_map.clear()

    build_maze(25, 25)
    for i in range(10):
        spawn_enemy()
    update_enemy_count()


# ==== ВОРОГ ====
class Enemy(Entity):
    def __init__(self, hp, identify, position):
        super().__init__(parent=scene, model='cube', color=color.black,
                         scale=(1, 3, 1), position=position, collider='box')
        self.hp = 100
        self.state = 'patrol'
        self.speed = 1
        self.notice_radius = 12
        self.attack_range = 2
        self.attack_cooldown = 1
        self._last_attack_time = -999
        self.direction = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1]))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            destroy(self)
            if self in enemies:
                enemies.remove(self)
                update_enemy_count()

    def update(self):
        if not player.enabled:
            return

        dist = distance(self.position, player.position)

        if dist <= self.attack_range:
            self.attack()
        elif dist <= self.notice_radius:
            self.chase()
        else:
            self.patrol()

    def chase(self):
        direction = (player.position - self.position).normalized()
        self.move(direction)

    def patrol(self):
        self.move(self.direction)
        if random.random() < 0.01:
            self.direction = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1]))

    def move(self, direction):
        next_pos = self.position + direction * self.speed * time.dt
        for wall in walls:
            if distance(next_pos, wall.position) < 1.2:
                return
        self.position = next_pos

    def attack(self):
        now = time.time()
        if now - self._last_attack_time >= self.attack_cooldown:
            self._last_attack_time = now
            player.hp -= 10
            hp_bar.scale_x = 0.4 * (player.hp / player.max_hp)
            if player.hp <= 0:
                game_over()


def update():
    if held_keys['escape']:
        app.userExit()


def spawn_enemy():
    free_cells = [(x, z) for x in range(len(maze_map))
                  for z in range(len(maze_map[0])) if maze_map[x][z] == 0]
    if not free_cells:
        return
    cx, cz = random.choice(free_cells)
    pos = Vec3(cx * 2 - len(maze_map), 1, cz * 2 - len(maze_map[0]))
    enemy = Enemy(100, 0, pos)
    enemies.append(enemy)
    update_enemy_count()
    return enemy


def input(key):
    global reload
    if not player.enabled:
        return

    if key == 'r' and not reload:
        reload = True
        invoke(finish_reload, delay=1.5)

    if key == 'left mouse down' and not reload and player.bullets > 0:
        shoot()


def finish_reload():
    global reload
    player.bullets = 30
    bullets_text.text = f'Bullets:{player.bullets}'
    reload = False


def shoot():
    animation_gun()
    player.bullets -= 1
    bullets_text.text = f'Bullets:{player.bullets}'
    bullet = Entity(parent=player, position=Vec3(0, 1.5, 1),
                    model='cube', scale=(0.1, 0.1, 0.3),
                    color=color.red, collider='box')
    bullet.world_parent = scene

    def update_bullet():
        bullet.position += bullet.forward * time.dt * 100
        for enemy in enemies:
            if bullet.intersects(enemy).hit:
                enemy.take_damage(40)
                destroy(bullet)
                return
        if distance(bullet.position, player.position) > 100:
            destroy(bullet)

    bullet.update = update_bullet


# ==== ЛАБІРИНТ ====
def build_maze(width, height):
    cell_size = 2
    for x in range(width):
        maze_map.append([])
        for z in range(height):
            if x == 0 or z == 0 or x == width - 1 or z == height - 1 or random.random() < 0.25:
                maze_map[x].append(1)
                wall = Entity(parent=scene, model='cube', color=color.rgb(100, 100, 100),
                              scale=(2, 5, 2),
                              position=(x * cell_size - width, 1.5, z * cell_size - height),
                              collider='box')
                walls.append(wall)
            else:
                maze_map[x].append(0)


# ==== МЕНЮ ====
def start_game():
    menu_bg.enabled = False
    title_text.enabled = False
    play_button.enabled = False
    exit_button.enabled = False

    gun_model.enabled = True
    bullets_text.enabled = True
    hp_bar.enabled = True
    hp_bar_bg.enabled = True
    enemy_count_text.enabled = True

    player.enabled = True
    mouse.locked = True

    restart_game()


def exit_game():
    app.userExit()


play_button.on_click = start_game
exit_button.on_click = exit_game

app.run()
