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
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import mainthread
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import json
import re
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import mainthread
from kivy.uix.button import Button
from kivymd.uix.list import MDList
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp



Window.size = (360, 640)
# Firebase configuration for client-side actions
firebaseConfig = {
    
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()


# Screen Manager with transition effects
class MDScreenManager(ScreenManager):
    transition = SlideTransition()

class SplashScreen(Screen):
    def on_enter(self):
        # Schedule the transition to the login screen after 5 seconds
        Clock.schedule_once(self.redirect_to_login, 5)

    def redirect_to_login(self, *args):
        self.manager.current = 'login'
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
        url = "URL"
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
    gmail_signup = ""

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
                {"text": "Weight Loss", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Weight Loss": self.set_fitness_goal(x)},
                {"text": "Muscle Gain", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Muscle Gain": self.set_fitness_goal(x)},
                {"text": "Maintain Weight", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Maintain Weight": self.set_fitness_goal(x)}
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
                "gmail": gmail_signup
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
        # Fetch the user's name from the Django backend
        if auth.current_user:
            user_email = auth.current_user['email']
            self.load_user_name(user_email)

    def load_user_name(self, email):
        # Fetch user data from the Django API
        url = "http://127.0.0.1:8000/api/posts/"
        response = requests.get(url, params={"email": email})

        if response.status_code == 200:
            # Assuming the response contains the user's data with the 'name' field
            user_data = response.json()
            user_name = user_data.get('name', 'User')  # Default to 'User' if no name is found
            self.ids.welcome_label.text = f"Welcome, {user_name}!"
        else:
            self.ids.welcome_label.text = "Welcome!"
            print(f"Failed to load user data: {response.json()}")  # Log error message

    def logout(self):
        auth.current_user = None
        self.manager.current = 'login'


# Profile & Settings Screen
class ProfileSettingsScreen(Screen):
    gmail = ""

    def on_enter(self):
        # Check if user is logged in and fetch profile data
        if auth.current_user:
            self.gmail = auth.current_user['email']
        self.load_profile_data(self.gmail)

    def load_profile_data(self, gmail):
        url = "http://127.0.0.1:8000/api/posts/"

        # Add email as query parameter
        response = requests.get(url, params={"email": gmail})

        if response.status_code == 200:
            profile_data = response.json()
            print(profile_data['name'])
            name = profile_data['name']
            email = profile_data['gmail']
            gender = profile_data['gender']
            fitness_goal = profile_data['fitness_goal']
            bmi = profile_data['bmi']
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

# WorkoutScreen class to manage the workout day navigation and display

class WorkoutPlansScreen(Screen):
    workout_plan = ListProperty([])
    current_day = NumericProperty(1)
    gmail = StringProperty("")
    gender = StringProperty("")
    fitness_goal = StringProperty("")

    def on_enter(self):
        if auth.current_user:  # Ensure `auth` is defined globally
            self.gmail = auth.current_user['email']
        self.load_profile_data(self.gmail)

    def load_profile_data(self, gmail):
        try:
            url = "http://127.0.0.1:8000/api/posts/"
            response = requests.get(url, params={"email": gmail})

            if response.status_code == 200:
                profile_data = response.json()
                self.gender = profile_data.get('gender', '')
                self.fitness_goal = profile_data.get('fitness_goal', '')
                self.fetch_workout_plan()
            else:
                self.ids.workout_day_title.text = f"Error: {response.json().get('error', 'Unknown Error')}"
        except Exception as e:
            self.ids.workout_day_title.text = f"Error: Unable to fetch profile data ({e})"

    def fetch_workout_plan(self):
        try:
            prompt = f"""
            Create a 7-day workout plan tailored specifically for a {self.gender.lower()} whose fitness goal is '{self.fitness_goal.lower()}'. 
            Include details of exercises focusing on common goals for {self.gender.lower()}s. Ensure:
            - Day 1 to Day 7 workouts, including two rest days.
            - Structured daily routines with clear exercises.
            """

            headers = {
                'Authorization': 'Bearer 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',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'llama3-8b-8192',
                'temperature': 0.7,
                'max_tokens': 1024,
                'messages': [{'role': 'user', 'content': prompt}]
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=data,
                headers=headers
            )

            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    raw_plan = response_data['choices'][0]['message']['content']
                    self.workout_plan = self.split_days(raw_plan)
                    self.display_workout_for_day(self.current_day)
                else:
                    raise Exception("Invalid response from API.")
            else:
                MDDialog(
                    title="API Error",
                    text=f"Failed to fetch workout plan: {response.status_code}, {response.text}"
                ).open()
        except Exception as e:
            MDDialog(title="Connection Error", text=f"Unable to connect to the API: {e}").open()

    def split_days(self, workout_plan):
        day_pattern = r"(Day \d+:.*?)(?=Day \d+:|$)"
        days = re.findall(day_pattern, workout_plan, re.DOTALL)
        return [day.strip() for day in days]

    @mainthread

    def display_workout_for_day(self, day):
        self.ids.workout_list.clear_widgets()

        if not self.workout_plan:
            self.ids.workout_day_title.text = "No Workout Plan Available"
            return

        if day <= len(self.workout_plan):
            day_plan = self.workout_plan[day - 1]
            self.ids.workout_day_title.text = f"Day {day}"
        else:
            day_plan = "Rest Day"
            self.ids.workout_day_title.text = f"Day {day}: Rest Day"


        exercises = [exercise.strip() for exercise in day_plan.split("\n") if exercise.strip()]

        for index, exercise in enumerate(exercises, start=1):
            card = MDCard(
                orientation="vertical",
                padding=dp(10),
                size_hint=(0.9, None),
                pos_hint={"center_x": 0.5},
                height=dp(60),
            )
            card.add_widget(MDLabel(
                text=f"{index}. {exercise}",
                halign="left",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(40),
            ))
            self.ids.workout_list.add_widget(card)

    def go_to_prev_day(self):
        if self.current_day > 1:
            self.current_day -= 1
            self.display_workout_for_day(self.current_day)

    def go_to_next_day(self):
        if self.current_day < len(self.workout_plan):
            self.current_day += 1
            self.display_workout_for_day(self.current_day)

    def go_home(self):
        self.root.current = 'home'

class DietRecommendationsScreen(Screen):
    diet_plan = {}
    current_day = NumericProperty(1)
    fitness_goal = StringProperty("")

    def on_enter(self):
        if not self.diet_plan:
            self.fetch_diet_plan(self.fitness_goal)

    def fetch_diet_plan(self, fitness_goal):
        try:
            prompt = f"""
            Create a 7-day diet plan tailored specifically for a person whose fitness goal is '{fitness_goal.lower()}'. 
            Include details on meals and snacks focusing on common dietary needs for this goal. Ensure:
            - Day 1 to Day 7 meals, including two rest days.
            - Structured meal plans with breakfast, lunch, and dinner.
            """

            headers = {
                'Authorization': 'Bearer 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',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'llama3-8b-8192',  # Model name used for Groq AI
                'temperature': 0.7,
                'max_tokens': 1024,
                'messages': [{'role': 'user', 'content': prompt}]
            }

            # API call to Groq AI
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=data,
                headers=headers
            )

            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    raw_plan = response_data['choices'][0]['message']['content']
                    self.diet_plan = self.split_days(raw_plan)
                    self.display_diet_for_day(self.current_day)
                else:
                    raise Exception("Invalid response from API.")
            else:
                MDDialog(
                    title="API Error",
                    text=f"Failed to fetch diet plan: {response.status_code}, {response.text}"
                ).open()
        except Exception as e:
            MDDialog(title="Connection Error", text=f"Unable to connect to the API: {e}").open()

    def split_days(self, diet_plan):
        # Assuming the response contains structured data like "Day 1: Meal 1, Meal 2"
        day_pattern = r"(Day \d+:.*?)(?=Day \d+:|$)"
        days = re.findall(day_pattern, diet_plan, re.DOTALL)
        return [day.strip() for day in days]

    def display_diet_for_day(self, day):
        self.ids.diet_list.clear_widgets()

        if not self.diet_plan:
            self.ids.diet_day_title.text = "No Diet Plan Available"
            return

        if day <= len(self.diet_plan):
            day_plan = self.diet_plan[day - 1]
            self.ids.diet_day_title.text = f"Day {day}"
        else:
            day_plan = "Rest Day"
            self.ids.diet_day_title.text = f"Day {day}: Rest Day"

        meals = [meal.strip() for meal in day_plan.split("\n") if meal.strip()]

        for index, meal in enumerate(meals, start=1):
            card = MDCard(
                orientation="vertical",
                padding=dp(10),
                size_hint=(0.9, None),
                pos_hint={"center_x": 0.5},
                height=dp(60),
            )
            card.add_widget(MDLabel(
                text=f"{index}. {meal}",
                halign="left",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(40),
            ))
            self.ids.diet_list.add_widget(card)

    def go_to_prev_day(self):
        # Move to the previous day only if we're not on the first day
        if self.current_day > 1:
            self.current_day -= 1
            self.display_diet_for_day(self.current_day)

    def go_to_next_day(self):
        # Move to the next day only if we haven't reached the end of the plan
        if self.current_day < len(self.diet_plan):
            self.current_day += 1
            self.display_diet_for_day(self.current_day)
# Motivation Screen (Daily Random Quote)
class MotivationScreen(Screen):
    motivational_quotes = [
        "Believe in yourself!",
        "Push yourself; no one else is going to do it for you.",
        "You are stronger than you think.",
        "Success is the sum of small efforts, repeated day in and day out.",
        "The only bad workout is the one that didn't happen.",
        "Your body can stand almost anything. It's your mind you have to convince.",
        "The pain you feel today will be the strength you feel tomorrow.",
        "It does not matter how slowly you go as long as you do not stop.",
        "Success is not about how fast you run, but how long you can keep running.",
        "The only person you are destined to become is the person you decide to be.",
        "Don't stop when you're tired, stop when you're done.",
        "The mind is everything. What you think you become.",
        "The only way to do great work is to love what you do.",
        "In the middle of difficulty lies opportunity."
    ]

    motivational_images = [
        "image.jpeg",  # Replace with the paths to your images
        "image1.jpeg",
        "image2.jpeg",
        "image3.jpeg",
        "image4.jpeg",
        "images.jpeg",
    ]

    def on_enter(self):
        self.get_daily_quote_and_image()  # Show a quote and image when entering the screen

    def get_daily_quote_and_image(self):
        # Get the current day of the year to ensure randomness based on the day
        day_of_year = datetime.now().timetuple().tm_yday
        random.seed(day_of_year)  # Seed random with the day of the year

        # Choose a random quote and image
        daily_quote = random.choice(self.motivational_quotes)
        daily_image = random.choice(self.motivational_images)

        # Update the UI with the chosen quote and image
        self.ids.quote_label.text = daily_quote
        self.ids.motivation_image.source = daily_image

        print(f"Displaying quote: {daily_quote}")
        print(f"Displaying image: {daily_image}")
class MainApp(MDApp):
    def build(self):
        # Load the .kv file here, after the app is initialized
        Builder.load_file('thelab.kv')
        return MDScreenManager()


if __name__ == "__main__":
    MainApp().run()
