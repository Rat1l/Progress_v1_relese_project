from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
player = FirstPersonController(enabled=False)
sky = Sky(enabled=False)
class Menu:
    def __init__(self):
        self.player = player
        self.sky = sky
        self.menu_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2,1),
            color=color.white
        )
        self.title = Text("Shooter", parent=camera.ui, scale=2, y=0.4)

        self.start_button = Button(text='▶ Start', color=color.azure, scale=(0.3, 0.1), y=0.1, parent=camera.ui)
        self.quit_button = Button(text='❌ Quit', color=color.red, scale=(0.3, 0.1), y=-0.1, parent=camera.ui)

        self.back_button = Button(
            text='← Menu',
            color=color.orange,
            scale=(0.2, 0.08),
            position=window.top_left + Vec2(0.12, -0.12),
            parent=camera.ui,
        )
        self.back_button.enabled = False

        self.start_button.on_click = self.start_game
        self.quit_button.on_click = application.quit
        self.back_button.on_click = self.return_to_menu

    def start_game(self):
        self.menu_bg.enabled = False
        self.title.enabled = False
        self.start_button.enabled = False
        self.quit_button.enabled = False
        player.enabled = True
        sky.enabled = True
        mouse.locked = True

    def return_to_menu(self):
        self.menu_bg.enabled = True
        self.title.enabled = True
        self.start_button.enabled = True
        self.quit_button.enabled = True
        player.enabled = False
        sky.enabled = False
        mouse.locked = False
