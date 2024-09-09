from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
class LoginScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class TheLabApp(MDApp):
    def build(self):
        return Builder.load_file('thelab.kv')

    def change_screen(self, screen_name):
        # Change screen based on the button click
        self.root.current = screen_name

    def login(self):
        return

    def signup(self):
        return
TheLabApp().run()