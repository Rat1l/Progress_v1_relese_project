from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time
import random 
app = Ursina()
player=FirstPersonController(collider='box')
player.hp = 100
player.max_hp = 100
player.bullets = 30
sky_texture = load_texture("Skybox.png")
reload = False
cooldow = 20
gun_model = Entity(
    parent=camera.ui,
    model='shotgun 1.glb',
    scale=1,
    position=Vec2(0.4, -1),
    rotation=Vec3(-10,-20,0),
    double_sided=True
)
bullets_text = Text(
    text = f'Bullets:{player.bullets}',
    parent=camera.ui,
    color = color.black,
    position=Vec2(-0.8, 0.4),
    scale=2
)
game_over_text = Text(
    text='GAME OVER',
    origin=(0,0),
    scale=4,
    color=color.red,
    enabled=False
)
retry_button = Button(
    text='RETRY',
    position = (-0.1, -0.3),
    scale=(0.2,0.05),
    color=color.black,
    enabled=False
)
hp_bar_bg = Entity(
    parent=camera.ui,
    model='quad',
    color=color.black,
    scale=(0.5, 0.04),
    position=(-0.1, -0.4)
)
hp_bar = Entity(
    parent=camera.ui,
    model='quad',
    color=color.red,
    scale=(0.4, 0.03),
    position=(-0.3, -0.4),
    origin_x=-.5
)
plot = Entity(
    parent=scene,
    model='cube', 
    color=color.gray,  
    scale=(50, 1, 50),  
    collider='box'  
)
Sky = Entity(
    parent=scene,
    model='Sphere',
    texture=sky_texture,
    scale=1500,
    double_sided=True
)
def animation_gun():
    print("Анімація пострілу")
    gun_model.animate_rotation(
        Vec3(-20, -20, 0),
        duration=0.1,
        curve=curve.out_expo
    )
    invoke(
        gun_model.animate_rotation,
        Vec3(-10, -20, 0),
        duration=0.1,
        curve=curve.in_expo,
        delay=0.1
    )
def game_over():
    player.enabled = False         
    mouse.locked = False        
    game_over_text.enabled = True 
    retry_button.enabled = True
    for e in enemies:         
        e.enabled = False
def restart_game():
    print("Restarting game...")
    player.enabled = True
    mouse.locked = True
    game_over_text.enabled = False
    retry_button.enabled = False

    player.hp = player.max_hp
    player.position = Vec3(0, 1, 0)
    player.bullets = 30
    bullets_text.text = f'Bullets:{player.bullets}'
    hp_bar.scale_x = 0.4

    for e in enemies:
        destroy(e)
    enemies.clear()

    for i in range(10):
        spawn_enemy()

    print("Game restarted!")
retry_button.on_click = restart_game

class Enemy(Entity):
    def __init__(self,hp,indetify,position,patrol_points=None):
        super().__init__(
            parent=scene,
            model = 'cube',
            color = color.black,
            scale=(1, 3, 1),
            position=position,
            collider = 'box'
        )
        self.hp = 100
        self.state = 'patrol'
        self.speed = 1
        self.notice_radius = 12
        self.attack_range = 2
        self.attack_damage = 25
        self.attack_cooldown = 1
        self._last_attack_time = -999
        if patrol_points:
            self.patrol_points = patrol_points
        else:
            p1 = self.position + Vec3(random.uniform(-8,8), 0, random.uniform(-8,8))
            p2 = self.position + Vec3(random.uniform(-8,8), 0, random.uniform(-8,8))
            self.patrol_points = [p1, p2]
        self._patrol_index = 0
        self.y = 1
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            destroy(self)
            if self in enemies:
                enemies.remove(self)
    def look_at_player(self):
        dir = (player.position - self.position).normalized()
        target = self.position + dir
        self.look_at(target)

    def update(self):
        if self.position.y <= 1:
            self.position.y = 1.1
        dist = distance(self.position, player.position)
        if self.state != 'attack' and dist <= self.attack_range:
            self.state = 'attack'

        elif dist <= self.notice_radius and self.state != 'attack':
            self.state = 'chase'

        elif dist > self.notice_radius and self.state == 'chase':
            self.state = 'patrol'

        if self.state == 'patrol':
            target = self.patrol_points[self._patrol_index]
            dir = (target - self.position)
            dir.y = 0
            if dir.length() < 0.5:
                self._patrol_index = (self._patrol_index + 1) % len(self.patrol_points)
            else:
                self.look_at(target)
                self.position += self.forward * self.speed * time.dt * 0.5  

        elif self.state == 'chase':
            self.look_at_player()
            self.position += self.forward * self.speed * time.dt

        elif self.state == 'attack':
            self.look_at_player()
            now = time.time()
            if now - self._last_attack_time >= self.attack_cooldown:
                self._last_attack_time = now
                player.hp -= 10
                hp_bar.scale_x = 0.4 * (player.hp/player.max_hp)
                print(player.hp)
                if player.hp <= 0:
                    game_over()                
            if dist > self.attack_range + 1:
                self.state = 'chase'
        elif self.state == 'idle':
            pass  
def update():
    if held_keys['escape']:
        app.userExit()
enemies = []
def spawn_enemy():
    pos = Vec3(
        random.randint(-25, 25),
        1,
        random.randint(-25, 25)
    )
    enemy = Enemy(100, 0, pos)
    enemies.append(enemy)
    return enemy
for i in range(10):
    spawn_enemy()
def input(key):
    global reload, cooldow
    if key == 'r' and not reload:
        reload = True
        print("Reloading...")
        invoke(finish_reload, delay=1.5)  

    if key == 'left mouse down' and not reload and player.bullets > 0 and not game_over_text.enabled == True:
        shoot()

def finish_reload():
    global reload
    player.bullets = 30
    bullets_text.text = f'Bullets:{player.bullets}'
    reload = False
    print("Reload complete!")      

def shoot():
    animation_gun()
    player.bullets -= 1
    bullets_text.text = f'Bullets:{player.bullets}'
    bullet = Entity(
        parent=player,
        position=Vec3(0, 1.5, 1),
        model='cube',
        scale=(0.1, 0.1, 0.3),
        color=color.red,
        collider='box'
    )
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
app.run()