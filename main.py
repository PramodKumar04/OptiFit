import os
import random
import webbrowser
import pyrebase
import firebase_admin
from firebase_admin import credentials
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime

# Firebase configuration for client-side actions
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
auth = firebase.auth()
db = firebase.database()

# Firebase Admin SDK setup for server-side actions
cred = credentials.Certificate(
    os.getenv('FIREBASE_CREDENTIALS_PATH', 'C:\\Users\\pramo\\OneDrive\\Desktop\\kivy thelab\\optifit_user_details.json'))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://optifit-50096-default-rtdb.firebaseio.com/'
})

# Screen Manager
class MDScreenManager(ScreenManager):
    pass

# Login Screen
class LoginScreen(Screen):
    def login(self):
        email = self.ids.email.text
        password = self.ids.password.text
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            if user:
                self.manager.current = 'home'
        except Exception as e:
            MDDialog(title="Login Error", text="Invalid email or password. Please try again.").open()

    def google_login(self):
        url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={firebaseConfig['apiKey']}&redirect_uri=http://localhost&response_type=token&scope=email%20profile"
        webbrowser.open(url)

# Signup Screen
class SignupScreen(Screen):
    def signup_step_one(self):
        email = self.ids.signup_email.text
        password = self.ids.signup_password.text
        try:
            user = auth.create_user_with_email_and_password(email, password)
            if user:
                self.manager.current = 'personal_details'
        except Exception as e:
            MDDialog(title="Signup Error", text="Failed to create account. Please try again.").open()

# Personal Details Screen
class PersonalDetailsScreen(Screen):
    gender_menu = None
    fitness_goal_menu = None

    def on_enter(self):
        self.gender_menu_items = [
            {"text": "Male", "viewclass": "OneLineListItem", "on_release": lambda x="Male": self.set_gender(x)},
            {"text": "Female", "viewclass": "OneLineListItem", "on_release": lambda x="Female": self.set_gender(x)},
            {"text": "Other", "viewclass": "OneLineListItem", "on_release": lambda x="Other": self.set_gender(x)},
        ]
        self.fitness_goal_menu_items = [
            {"text": "Weight Loss", "viewclass": "OneLineListItem", "on_release": lambda x="Weight Loss": self.set_fitness_goal(x)},
            {"text": "Muscle Gain", "viewclass": "OneLineListItem", "on_release": lambda x="Muscle Gain": self.set_fitness_goal(x)},
            {"text": "Maintain Weight", "viewclass": "OneLineListItem", "on_release": lambda x="Maintain Weight": self.set_fitness_goal(x)},
        ]
        self.gender_menu = MDDropdownMenu(caller=self.ids.gender_field, items=self.gender_menu_items, width_mult=4)
        self.fitness_goal_menu = MDDropdownMenu(caller=self.ids.fitness_goal_field, items=self.fitness_goal_menu_items, width_mult=4)

    def open_gender_menu(self):
        self.gender_menu.open()

    def open_fitness_goal_menu(self):
        self.fitness_goal_menu.open()

    def set_gender(self, gender):
        self.ids.gender_field.text = gender
        self.gender_menu.dismiss()

    def set_fitness_goal(self, fitness_goal):
        self.ids.fitness_goal_field.text = fitness_goal
        self.fitness_goal_menu.dismiss()

    def submit_details(self):
        name = self.ids.name.text.strip()
        age = self.ids.age.text.strip()
        gender = self.ids.gender_field.text
        height = self.ids.height.text.strip()
        weight = self.ids.weight.text.strip()
        fitness_goal = self.ids.fitness_goal_field.text

        if not name or not age or not height or not weight:
            MDDialog(title="Input Error", text="Please fill in all fields.").open()
            return

        try:
            user_id = auth.current_user['localId']
            user_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "fitness_goal": fitness_goal
            }
            db.child("users").child(user_id).set(user_data)
            self.manager.current = 'home'
        except Exception as e:
            MDDialog(title="Submission Error", text="Failed to submit details. Please try again.").open()

# Home Screen
class HomeScreen(Screen):
    def on_enter(self):
        try:
            user_id = auth.current_user['localId']
            user_info = db.child("users").child(user_id).get()
            user_name = user_info.val().get("name", "User")
            self.ids.welcome_label.text = f"Welcome, {user_name}!"
        except Exception as e:
            self.ids.welcome_label.text = "Welcome!"
            print(f"Error: {e}")

    def logout(self):
        auth.current_user = None
        self.manager.current = 'login'

# Profile & Settings Screen
class ProfileSettingsScreen(Screen):
    def on_enter(self):
        user_id = auth.current_user['localId']
        user_info = db.child("users").child(user_id).get()
        self.ids.name.text = user_info.val().get("name", "")
        self.ids.email.text = auth.current_user['email']
        self.ids.gender_field.text = user_info.val().get("gender", "")
        self.ids.fitness_goal_field.text = user_info.val().get("fitness_goal", "")

    def submit_settings(self):
        name = self.ids.name.text.strip()
        gender = self.ids.gender_field.text
        fitness_goal = self.ids.fitness_goal_field.text
        if name and gender and fitness_goal:
            user_id = auth.current_user['localId']
            user_data = {"name": name, "gender": gender, "fitness_goal": fitness_goal}
            db.child("users").child(user_id).update(user_data)
            MDDialog(title="Success", text="Profile updated successfully.").open()
        else:
            MDDialog(title="Error", text="Please fill in all fields.").open()

# Workout Plans Screen
class WorkoutPlansScreen(Screen):
    def on_enter(self):
        user_id = auth.current_user['localId']
        user_info = db.child("users").child(user_id).get()
        fitness_goal = user_info.val().get("fitness_goal", "Not Set")
        self.ids.workout_plan.text = f"Workout Plan for: {fitness_goal}"

# Motivation Screen (Daily Random Quote)
class MotivationScreen(Screen):
    motivational_quotes = [
        "Believe in yourself!",
        "Push yourself, no one else is going to do it for you.",
        "You are stronger than you think.",
        "Success is the sum of small efforts, repeated day in and day out."
    ]

    def get_daily_quote(self):
        day_of_year = datetime.now().timetuple().tm_yday
        random.seed(day_of_year)  # Use day of year to seed randomness
        daily_quote = random.choice(self.motivational_quotes)
        self.ids.quote_label.text = daily_quote

Builder.load_file('thelab.kv')

# Main App
class MainApp(MDApp):
    def build(self):
        return MDScreenManager()

if __name__ == "__main__":
    MainApp().run()
