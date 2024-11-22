import os
import requests
import random
import webbrowser
import pyrebase
import firebase_admin
from kivy.core.window import Window
from firebase_admin import credentials
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
Window.size = (360, 640)
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



# Screen Manager with transition effects
class MDScreenManager(ScreenManager):
    transition = SlideTransition()

# Login Screen
class LoginScreen(Screen):
    def login(self):
        email = self.ids.email.text
        password = self.ids.password.text
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            if user:
                self.manager.current = 'home'
        except Exception:
            MDDialog(title="Login Error", text="Invalid email or password. Please try again.").open()

    def google_login(self):
        url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={firebaseConfig['apiKey']}&redirect_uri=http://localhost&response_type=token&scope=email%20profile"
        webbrowser.open(url)

# Signup Screen
class SignupScreen(Screen):
    def signup_step_one(self):
        email = self.ids.signup_email.text
        password = self.ids.signup_password.text
        confirm_password = self.ids.confirm_password.text

        if password != confirm_password:
            MDDialog(title="Password Mismatch", text="Passwords do not match. Please try again.").open()
            return

        try:
            user = auth.create_user_with_email_and_password(email, password)
            if user:
                self.manager.current = 'personal_details'
        except Exception:
            MDDialog(title="Signup Error", text="Failed to create account. Please try again.").open()

# Personal Details Screen
class PersonalDetailsScreen(Screen):
    gender_menu = None
    fitness_goal_menu = None
    gmail_signup=""

    def on_enter(self):
        # Setup for gender and fitness goal dropdowns
        self.gmail_signup = self.manager.get_screen('signup').ids.signup_email.text
        self.gender_menu = MDDropdownMenu(
            caller=self.ids.gender_field,
            items=[
                {"text": "Male", "viewclass": "OneLineListItem", "on_release": lambda x="Male": self.set_gender(x)},
                {"text": "Female", "viewclass": "OneLineListItem", "on_release": lambda x="Female": self.set_gender(x)},
                {"text": "Other", "viewclass": "OneLineListItem", "on_release": lambda x="Other": self.set_gender(x)}
            ],
            width_mult=4
        )
        self.fitness_goal_menu = MDDropdownMenu(
            caller=self.ids.fitness_goal_field,
            items=[
                {"text": "Weight Loss", "viewclass": "OneLineListItem", "on_release": lambda x="Weight Loss": self.set_fitness_goal(x)},
                {"text": "Muscle Gain", "viewclass": "OneLineListItem", "on_release": lambda x="Muscle Gain": self.set_fitness_goal(x)},
                {"text": "Maintain Weight", "viewclass": "OneLineListItem", "on_release": lambda x="Maintain Weight": self.set_fitness_goal(x)}
            ],
            width_mult=4
        )

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

    def calculate_bmi(self, height, weight):
        # Convert height from centimeters to meters for BMI calculation
        height_in_meters = float(height) / 100
        return round(float(weight) / (height_in_meters ** 2), 2)

    def submit_details(self):
        name = self.ids.name.text.strip()
        age = self.ids.age.text.strip()
        gender = self.ids.gender_field.text
        height = self.ids.height.text.strip()
        weight = self.ids.weight.text.strip()
        fitness_goal = self.ids.fitness_goal_field.text
        gmail_signup = self.gmail_signup
        if not name or not age or not height or not weight or not gender or not fitness_goal:
            MDDialog(title="Input Error", text="Please fill in all fields.").open()
            return

        try:
            bmi = self.calculate_bmi(height, weight)
            user_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "fitness_goal": fitness_goal,
                "bmi": bmi,
                "gmail":gmail_signup
            }
            # Send POST request to Django API to create a new post
            url = "http://127.0.0.1:8000/api/posts/"
            # Replace with your actual Django API endpoint
            response = requests.post(url, data=user_data)

            if response.status_code == 201:  # If successful, 201 means created
                MDDialog(title="Details Saved", text=f"Your BMI is: {bmi}").open()
                self.manager.current = 'home'
            else:
                MDDialog(title="Submission Error", text="Failed to submit details. Please try again.").open()

        except Exception as e:
            MDDialog(title="Submission Error", text="Failed to submit details. Please try again.").open()
            print(f"Error: {e}")  # Log error for debugging

# Additional screens and classes are set up similarly...
# Home Screen
class HomeScreen(Screen):
    def on_enter(self):
            self.ids.welcome_label.text = "Welcome to OptiFit!"

    def logout(self):
        auth.current_user = None
        self.manager.current = 'login'

# Profile & Settings Screen
class ProfileSettingsScreen(Screen):
    gmail=""
    def on_enter(self):
        # Check if user is logged in and fetch profile data
        if auth.current_user:
            self.gmail = auth.current_user['email']
        self.load_profile_data(self.gmail)
            

    def load_profile_data(self, gmail):
        url = "http://127.0.0.1:8000/api/posts/"

        # Add email as query parameter
        response = requests.get(url, params={"email":gmail})

        if response.status_code == 200:
            profile_data = response.json()
            print(profile_data['name'])
            name=profile_data['name']
            email= profile_data['gmail']
            gender=profile_data['gender']
            fitness_goal=profile_data['fitness_goal']
            bmi=profile_data['bmi']
            # Set the fields in the Kivy interface with the fetched data
            self.ids.name.text = name
            self.ids.email.text = email  # Display the email from the Django API
            self.ids.gender_field.text = gender
            self.ids.fitness_goal_field.text = fitness_goal

            # Make Gmail field uneditable (if desired, as per your request)
            self.ids.email.readonly = True
        else:
            self.profile_label.text = f"Error: {response.json()['error']}"

    def submit_details(self):
        name = self.ids.name.text.strip()
        age = self.ids.age.text.strip()
        gender = self.ids.gender_field.text
        height = self.ids.height.text.strip()
        weight = self.ids.weight.text.strip()
        fitness_goal = self.ids.fitness_goal_field.text
        

        if not name or not age or not height or not weight or not gender or not fitness_goal:
            MDDialog(title="Input Error", text="Please fill in all fields.").open()
            return

        try:
            user_id = auth.current_user['localId']
            print(f"User ID: {user_id}")  # Check if user ID is being fetched correctly

            user_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "fitness_goal": fitness_goal
            }

            # Check if user data looks correct before submitting
            print(f"User Data: {user_data}")

            # Attempt to save to Firebase
            db.child("users").child(user_id).set(user_data)
            self.manager.current = 'home'
            print("Data successfully submitted!")

        except Exception as e:
            MDDialog(title="Submission Error", text="Failed to submit details. Please try again.").open()
            print(f"Error: {e}")  # Print detailed error for debugging
#workout plans screen
class WorkoutPlansScreen(Screen):
    workout_plan = {}
    current_day = 1

    def go_home(self):
        self.manager.current = 'home'

    def on_enter(self):
        if not self.workout_plan:
            self.fetch_workout_plan()  # Fetch workout plan when the screen is entered
        self.display_workout_for_day(self.current_day)

    def fetch_workout_plan(self):
        try:
            response = requests.get("http://localhost:4000/workout")
            if response.status_code == 200:
                self.workout_plan = response.json()
            else:
                MDDialog(title="Error", text="Failed to fetch workout plan from server.").open()
        except Exception as e:
            MDDialog(title="Connection Error", text=f"Unable to connect to the server: {e}").open()

    def display_workout_for_day(self, day):
        self.ids.workout_list.clear_widgets()

        if not self.workout_plan:
            self.ids.workout_day_title.text = "No Workout Plan Available"
            return

        day_key = list(self.workout_plan.keys())[day - 1]
        day_name = day_key.split(": ")[0]
        exercises = self.workout_plan[day_key]

        self.ids.workout_day_title.text = day_name

        for exercise in exercises:
            card = MDCard(
                orientation="vertical",
                padding="10dp",
                size_hint=(0.9, None),
                height="60dp",
                pos_hint={"center_x": 0.5}
            )
            card.add_widget(MDLabel(text=exercise, halign="center"))
            self.ids.workout_list.add_widget(card)

    def open_planner_form(self):
        # Replace with your server's actual URL if not localhost
        webbrowser.open("http://localhost:4000/")

class DietRecommendationsScreen(Screen):
    diet_plan = {}

    def go_home(self):
        self.manager.current = 'home'

    def on_enter(self):
        if not self.diet_plan:
            self.fetch_diet_plan()  # Fetch workout plan when the screen is entered


    def fetch_diet_plan(self):
        try:
            response = requests.get("http://localhost:3000/diet")
            if response.status_code == 200:
                self.diet_plan = response.json()
        except Exception as e:
            MDDialog(title="Connection Error", text=f"Unable to connect to the server: {e}").open()



        if not self.diet_plan:
            self.ids.diet_day_title.text = "Get Your Fitness Plan"
            return
    def open_planner_form(self):
        webbrowser.open("http://localhost:3000/")




# Motivation Screen (Daily Random Quote)
class MotivationScreen(Screen):
    motivational_quotes = [
        "Believe in yourself!",
        "Push yourself; no one else is going to do it for you.",
        "You are stronger than you think.",
        "Success is the sum of small efforts, repeated day in and day out."
        "The only bad workout is the one that didn't happen."
        "Your body can stand almost anything. It's your mind you have to convince."
        "The pain you feel today will be the strength you feel tomorrow."
        "It does not matter how slowly you go as long as you do not stop."
        "Success is not about how fast you run, but how long you can keep running."
        "The only person you are destined to become is the person you decide to be."
        "Don't stop when you're tired, stop when you're done."
        "The mind is everything. What you think you become."
        "The only way to do great work is to love what you do."
        "In the middle of difficulty lies opportunity."
    ]

    def on_enter(self):
        self.get_daily_quote()  # Get the daily quote when entering the screen

    def get_daily_quote(self):
        day_of_year = datetime.now().timetuple().tm_yday
        random.seed(day_of_year)  # Seed random with the day of the year
        daily_quote = random.choice(self.motivational_quotes)
        self.ids.quote_label.text = daily_quote

class MainApp(MDApp):
    def build(self):
        # Load the .kv file here, after the app is initialized
        Builder.load_file('thelab.kv')
        return MDScreenManager()

if __name__ == "__main__":
    MainApp().run()
