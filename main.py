import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
import pyrebase
from kivymd.uix.menu import MDDropdownMenu

# Load Firebase credentials from environment variable
firebase_cred = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_cred)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DATABASE_URL")  # Your actual database URL
})

# Firebase configuration
firebaseConfig = {
    "apiKey": "AIzaSyCfVXAq6ebFt8UVkWfJ8wrBrUaqyqSh43E",
    "authDomain": "optifit-50096.firebaseapp.com",
    "databaseURL": "https://optifit-50096-default-rtdb.firebaseio.com",
    "projectId": "optifit-50096",
    "storageBucket": "optifit-50096.appspot.com",
    "messagingSenderId": "151853610236",
    "appId": "1:151853610236:web:a74c7beed18b9cf4a35379",
    "measurementId": "G-GT45418WNX"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

class MDScreenManager(ScreenManager):
    pass

class LoginScreen(Screen):
    def login(self):
        email = self.ids.email.text
        password = self.ids.password.text
        try:
            # Login user
            user = auth.get_user_by_email(email)  # Verify user existence
            # Implement actual password checking if needed
            self.manager.current = 'home'
        except Exception as e:
            MDDialog(title="Error", text=str(e)).open()

class SignupScreen(Screen):
    def signup_step_one(self):
        email = self.ids.signup_email.text
        password = self.ids.signup_password.text

        try:
            # Create a new user with email and password
            user = auth.create_user(email=email, password=password)
            self.manager.current = 'signup_details'
        except Exception as e:
            MDDialog(title="Error", text=str(e)).open()

class SignupDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fitness_goal_menu = MDDropdownMenu(
            caller=self.ids.fitness_goal_field,
            items=[
                {"text": "Muscle Gain", "viewclass": "OneLineListItem", "on_release": lambda x="muscle_gain": self.set_fitness_goal(x)},
                {"text": "Weight Loss", "viewclass": "OneLineListItem", "on_release": lambda x="weight_loss": self.set_fitness_goal(x)},
            ],
            width_mult=4,
        )

    def set_fitness_goal(self, goal):
        self.ids.fitness_goal.text = goal
        self.fitness_goal_menu.dismiss()

    def open_fitness_goal_menu(self):
        self.fitness_goal_menu.open()

class HomeScreen(Screen):
    def on_enter(self):
        user_id = auth.current_user.uid
        user_info = db.child("users").child(user_id).get()
        user_name = user_info.val()["name"]
        self.ids.welcome_label.text = f"Welcome, {user_name}!"

# Load the KV file
Builder.load_file('thelab.kv')

class MainApp(MDApp):
    def build(self):
        return MDScreenManager()

if __name__ == "__main__":
    MainApp().run()
