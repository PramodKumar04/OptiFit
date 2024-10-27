from kivymd.uix.screen import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog

class PersonalDetailsScreen(Screen):
    gender_menu = None
    fitness_goal_menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        # Define gender menu items
        self.gender_menu_items = [
            {"text": "Male", "viewclass": "OneLineListItem", "on_release": lambda x="Male": self.set_gender(x)},
            {"text": "Female", "viewclass": "OneLineListItem", "on_release": lambda x="Female": self.set_gender(x)},
            {"text": "Other", "viewclass": "OneLineListItem", "on_release": lambda x="Other": self.set_gender(x)},
        ]

        # Define fitness goal menu items
        self.fitness_goal_menu_items = [
            {"text": "Weight Loss", "viewclass": "OneLineListItem", "on_release": lambda x="Weight Loss": self.set_fitness_goal(x)},
            {"text": "Muscle Gain", "viewclass": "OneLineListItem", "on_release": lambda x="Muscle Gain": self.set_fitness_goal(x)},
            {"text": "Maintain Weight", "viewclass": "OneLineListItem", "on_release": lambda x="Maintain Weight": self.set_fitness_goal(x)},
        ]

        self.gender_menu = MDDropdownMenu(
            caller=self.ids.gender_field,
            items=self.gender_menu_items,
            width_mult=4,
        )

        self.fitness_goal_menu = MDDropdownMenu(
            caller=self.ids.fitness_goal_field,
            items=self.fitness_goal_menu_items,
            width_mult=4,
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

    def submit_details(self):
        name = self.ids.name.text.strip()
        age = self.ids.age.text.strip()
        gender = self.ids.gender_field.text
        height = self.ids.height.text.strip()
        weight = self.ids.weight.text.strip()
        fitness_goal = self.ids.fitness_goal_field.text

        # Basic validation
        if not name or not age or not height or not weight:
            MDDialog(title="Input Error", text="Please fill in all fields.").open()
            return

        try:
            user_id = auth.current_user['localId']

            # Store user details in Firebase
            user_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "fitness_goal": fitness_goal
            }
            db.child("users").child(user_id).set(user_data)  # Save user data in Firebase
            self.manager.current = 'home'  # Navigate to home screen
        except Exception as e:
            MDDialog(title="Submission Error", text="Failed to submit details. Please try again.").open()
