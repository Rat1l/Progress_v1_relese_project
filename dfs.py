from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# === ГРА ===
player = FirstPersonController(enabled=False)
sky = Sky(enabled=False)

# === МЕНЮ ===
menu_bg = Entity(
    parent=camera.ui,
    model='quad',
    scale=(2, 1),
    color=color.rgb(30, 30, 40),  # темний фон
)

title = Text("My Game", parent=camera.ui, scale=2, y=0.4)

start_button = Button(text='▶ Start', color=color.azure, scale=(0.3, 0.1), y=0.1, parent=camera.ui)
quit_button = Button(text='❌ Quit', color=color.red, scale=(0.3, 0.1), y=-0.1, parent=camera.ui)

# === КНОПКА "НАЗАД У МЕНЮ" ===
back_button = Button(
    text='← Menu',
    color=color.orange,
    scale=(0.2, 0.08),
    position=window.top_left + Vec2(0.12, -0.12),
    parent=camera.ui,
)
back_button.enabled = False

# === ФУНКЦІЇ ПЕРЕМИКАННЯ ===
def start_game():
    menu_bg.enabled = False
    title.enabled = False
    start_button.enabled = False
    quit_button.enabled = False
    player.enabled = True
    sky.enabled = True
    mouse.locked = True

def return_to_menu():
    menu_bg.enabled = True
    title.enabled = True
    start_button.enabled = True
    quit_button.enabled = True
    player.enabled = False
    sky.enabled = False
    mouse.locked = False

# === ПРИВ'ЯЗКА КНОПОК ===
start_button.on_click = start_game
quit_button.on_click = application.quit
back_button.on_click = return_to_menu

# === ОБРОБКА ESC + КНОПКИ ===
def update():
    if player.enabled:
        back_button.enabled = True
        if held_keys['escape']:
            return_to_menu()
    else:
        back_button.enabled = False

# === ЗАПУСК ГРИ ===
app.run()
