
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

# Define Screens
class HomeScreen(Screen):
    pass

class WorkoutPlansScreen(Screen):
    pass

class DietaryRecommendationsScreen(Screen):
    pass

class MotivationSupportScreen(Screen):
    pass

class UserProfileScreen(Screen):
    pass

class DaywiseWorkoutScreen(Screen):
    pass

class MotivationQuotesScreen(Screen):
    pass

class LogoutScreen(Screen):
    pass

class MyScreenManager(ScreenManager):
    pass

# Define the Main App Class
class MyApp(MDApp):
    def build(self):

        # Load the .kv file
        return Builder.load_file("thelab.kv")

# Run the app
if __name__ == "__main__":
    MyApp().run()
