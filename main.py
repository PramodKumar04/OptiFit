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
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
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
        confirm_password = self.ids.confirm_password.text

        if password != confirm_password:
            MDDialog(title="Password Mismatch", text="Passwords do not match. Please try again.").open()
            return

        try:
            user = auth.create_user_with_email_and_password(email, password)
            if user:
                self.manager.current = 'personal_details'
        except Exception as e:
            MDDialog(title="Signup Error", text="Failed to create account. Please try again.").open()

# Personal Details Screen
from kivymd.uix.label import MDLabel  # Add this to display BMI

class PersonalDetailsScreen(Screen):
    gender_menu = None
    fitness_goal_menu = None

    def on_enter(self):
        # Setup for gender and fitness goal dropdowns
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

    def calculate_bmi(self, height, weight):
        # Convert height from centimeters to meters for BMI calculation
        height_in_meters = float(height) / 100
        return round(float(weight) / (height_in_meters ** 2), 2)  # BMI formula

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
            # Calculate BMI
            bmi = self.calculate_bmi(height, weight)
            # Save user data to Firebase
            user_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "fitness_goal": fitness_goal,
                "bmi": bmi  # Add BMI to user data
            }
            db.child("users").child(user_id).set(user_data)
            self.manager.current = 'home'
            # Display BMI to the user
            MDDialog(title="Details Saved", text=f"Your BMI is: {bmi}").open()
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


# Workout Plans Screen
class WorkoutPlansScreen(Screen):
    workout_plan = {
        "Day 1: Chest & Triceps": [
            "Bench Press - 4 sets of 8-10 reps",
            "Dumbbell Flyes - 3 sets of 10-12 reps",
            "Tricep Dips - 4 sets of 8-10 reps",
            "Skull Crushers - 3 sets of 10-12 reps",
            "Push-Ups - 3 sets to failure"
        ],
        "Day 2: Back & Biceps": [
            "Pull-Ups - 4 sets of 8-10 reps",
            "Bent Over Rows - 4 sets of 8-10 reps",
            "Lat Pulldowns - 3 sets of 10-12 reps",
            "Barbell Curls - 4 sets of 8-10 reps",
            "Hammer Curls - 3 sets of 10-12 reps"
        ],
        "Day 3: Legs": [
            "Squats - 4 sets of 8-10 reps",
            "Leg Press - 4 sets of 8-10 reps",
            "Lunges - 3 sets of 10-12 reps per leg",
            "Leg Extensions - 3 sets of 12 reps",
            "Calf Raises - 4 sets of 15 reps"
        ],
        "Day 4: Shoulders": [
            "Overhead Press - 4 sets of 8-10 reps",
            "Dumbbell Lateral Raises - 3 sets of 10-12 reps",
            "Front Raises - 3 sets of 10-12 reps",
            "Face Pulls - 3 sets of 12 reps",
            "Shrugs - 4 sets of 15 reps"
        ],
        "Day 5: Full Body/Core": [
            "Deadlift - 4 sets of 6-8 reps",
            "Plank - 3 sets of 1 minute",
            "Russian Twists - 3 sets of 20 reps",
            "Bicycle Crunches - 3 sets of 20 reps",
            "Mountain Climbers - 3 sets of 1 minute"
        ],
        "Days 6 & 7: Rest and Recovery": [
            "Rest and recovery. Engage in light stretching or yoga."
        ]
    }

    current_day = 1  # Track the day the user is viewing

    def on_enter(self):
        self.display_workout_for_day(self.current_day)

    def display_workout_for_day(self, day):
        # Clear previous workout plan display
        self.ids.workout_list.clear_widgets()

        day_name = f"Day {day}: " + list(self.workout_plan.keys())[day - 1].split(": ")[1]
        exercises = self.workout_plan[day_name]

        # Set the title for the current day
        self.ids.workout_day_title.text = day_name

        # Add each exercise in a card
        for exercise in exercises:
            card = MDCard(
                orientation="vertical",
                padding="10dp",
                size_hint=(0.9, None),
                height="60dp",  # Adjust this height as needed
                pos_hint={"center_x": 0.5}
            )
            card.add_widget(MDLabel(text=exercise, halign="center"))
            self.ids.workout_list.add_widget(card)

    def next_day(self):
        if self.current_day < len(self.workout_plan):
            self.current_day += 1
            self.display_workout_for_day(self.current_day)

    def previous_day(self):
        if self.current_day > 1:
            self.current_day -= 1
            self.display_workout_for_day(self.current_day)


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
