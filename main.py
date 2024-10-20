import pyrebase
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

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


# Define Screens
class LoginScreen(Screen):
    pass


class SignupScreen(Screen):
    pass


class MyScreenManager(ScreenManager):
    pass


# Define the Main App Class
class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase = firebase
        self.auth = self.firebase.auth()
        self.db = firebase.database()

    def build(self):
        return Builder.load_file("thelab.kv")

    def change_screen(self, screen_name):
        self.root.current = screen_name

    def login(self):
        email = self.root.get_screen('login').ids.email.text
        password = self.root.get_screen('login').ids.password.text

        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            print("User logged in successfully!")
            self.change_screen('home')  # Assuming you have a 'home' screen
        except Exception as e:
            print("Login error:", e)

    def signup(self):
        email = self.root.get_screen('signup').ids.email.text
        password = self.root.get_screen('signup').ids.password.text
        confirm_password = self.root.get_screen('signup').ids.confirm_password.text

        if password == confirm_password:
            try:
                # Create the user in Firebase Authentication
                user = self.auth.create_user_with_email_and_password(email, password)
                print("User registered successfully!")

                # Store additional user information in Firebase Realtime Database
                user_data = {"email": email}
                self.db.child("users").push(user_data)  # Pushing data to the "users" node in Firebase

                self.change_screen('login')  # Navigate to login screen after signup
            except Exception as e:
                print("Signup error:", e)
        else:
            print("Passwords do not match.")


if __name__ == "__main__":
    MyApp().run()
