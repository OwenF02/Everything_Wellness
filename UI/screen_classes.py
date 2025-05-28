# Logging
import logging
logger = logging.getLogger(__name__)

# Date and Time
from datetime import datetime

# Kivy UI Elements
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

# SQL import
from mysql.connector import Error
import requests


# Database Functions
from Models.database import create_connection, log_food as db_log_food

# Date Picker import will be handled inside the method where it's used

class LoginScreen(Screen):
    """Screen for user login."""
    pass

class RegisterScreen(Screen):
    """Screen for user registration."""
    pass

class SocializingScreen(Screen):
    """Screen for socializing features where users can post updates."""
    
    def add_post(self):
        """Adds a post to the socializing feed."""
        posts_container = self.ids.posts_container
        post = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding='10dp')
        
        post.add_widget(Label(text='User Name', font_size='18sp'))
        post.add_widget(Label(text='This is a placeholder for a post. Content will go here.', font_size='14sp'))
        post.add_widget(Label(text='Timestamp', font_size='12sp'))
        
        posts_container.add_widget(post)
        
        posts_container.height += post.height
        self.ids.scroll_view.scroll_y = 0

class FoodSearchScreen(Screen):
    """Screen to search for food items and scan barcodes."""

    def search_food(self, query):
        """Searches for food items based on user input."""
        if query:
            api_url = f'https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&json=1'
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                search_data = response.json().get('products', [])

                # Clear previous results
                self.ids.search_results.clear_widgets()

                # Display each food item found
                for item in search_data:
                    name = item.get('product_name', 'Unknown')
                    button = Button(text=name, size_hint_y=None, height='40dp')
                    button.bind(on_release=lambda btn, food=item: self.log_food(food))
                    self.ids.search_results.add_widget(button)
            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching search results: {e}')

    def start_camera(self):
        """Starts the camera for barcode scanning."""
        # Implement barcode scanning logic here or reuse from TrackingScreen
        pass
    
    def log_food(self, food_data):
        """Logs food data using the database module."""
        user_id = 1  # Replace with actual user ID
        calories = food_data.get('nutriments', {}).get('energy-kcal', 0)
        carbs = food_data.get('nutriments', {}).get('carbohydrates', 0)
        fats = food_data.get('nutriments', {}).get('fat', 0)
        proteins = food_data.get('nutriments', {}).get('proteins', 0)
        meal_description = "Food logged via barcode scanner"
        
        db_log_food(user_id, calories, carbs, fats, proteins, meal_description)

class TrackingScreen(Screen):
    """Screen for tracking fitness activities, calories, and water intake."""
    total_calories = 0
    total_water = 0
    total_exercises = 0
    exercise_log = {}
    food_log = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.meal_count = 3  # Assuming Meal 1, Meal 2, Meal 3 are preset

    def add_meal_entry(self):
        """Dynamically adds a new meal entry to the interface."""
        self.meal_count += 1
        meal_num = f'Meal {self.meal_count}'

        # Add a new BoxLayout for each meal
        meal_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')

        # Add Label for the meal name
        meal_layout.add_widget(Label(text=meal_num, size_hint_x=0.3))

        # TextInput for entering calories
        calorie_input = TextInput(hint_text='Enter calories', multiline=False, size_hint_x=0.4)
        meal_layout.add_widget(calorie_input)

        # Button to add calories for this meal
        add_button = Button(text='Add', size_hint_x=0.3)
        add_button.bind(on_press=lambda instance: self.add_calories_for_meal(calorie_input.text, meal_num))
        meal_layout.add_widget(add_button)

        # Add the new layout to the meal entries section in your Kivy layout
        self.ids.meal_entries.add_widget(meal_layout)

        # Update the height of the meal_entries BoxLayout
        self.ids.meal_entries.height = self.ids.meal_entries.minimum_height

        def navigate_to_food_search(self, meal_number):
            """Navigates to the food search screen for the specified meal number."""
            self.manager.current = 'food_search'  # Update to the correct screen name

            # Optionally set the meal number to a property that FoodSearchScreen can use
            food_search_screen = self.manager.get_screen('food_search')
            food_search_screen.current_meal = meal_number  # You might want to implement this property

    def add_calories_for_meal(self, calorie_text, meal_name):
        """Adds calories from an individual meal entry and updates the total."""
        try:
            calories = int(calorie_text)
            self.total_calories += calories
            self.update_calories_display()
            logger.info(f"Calories for {meal_name} added: {calories}")
        except ValueError:
            logger.debug(f"Invalid calorie input for {meal_name}. Please enter an integer.")

    def update_calories_display(self):
        """Updates the display for total calories."""
        total_calories_label = self.ids.total_calories
        total_calories_label.text = f'Total Calories: {self.total_calories}'
    
    # log food
    def log_food(self, food_data):
        """Logs food data to the database.

        Args:
            food_data (dict): Nutritional information of the food item.
        """
        user_id = 1  # Replace with actual user ID
        calories = food_data.get('nutriments', {}).get('energy-kcal', 0)
        carbs = food_data.get('nutriments', {}).get('carbohydrates', 0)
        fats = food_data.get('nutriments', {}).get('fat', 0)
        proteins = food_data.get('nutriments', {}).get('proteins', 0)
        
        try:
            connection = create_connection()
            if connection.is_connected():
                cursor = connection.cursor()
                insert_query = """
                INSERT INTO nutrition (user_id, date, calories_intake, carbohydrates, fats, proteins, meal_description)
                VALUES (%s, CURDATE(), %s, %s, %s, %s, %s)
                """
                meal_description = "Food logged via barcode scanner"
                cursor.execute(insert_query, (user_id, calories, carbs, fats, proteins, meal_description))
                connection.commit()
                logger.info("Food log added successfully.")
        except Error as e:
            logger.error(f"Error logging food: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def update_water_display(self):
        """Updates the display for total water intake."""
        total_water_label = self.ids.total_water
        total_water_label.text = f'Total Water: {self.total_water} ml'

    # adding exercises
    def add_exercise(self, exercise_text, duration_text):
        """Adds an exercise entry to the exercise log.

        Args:
            exercise_text (str): The name of the exercise.
            duration_text (str): Duration of the exercise in minutes.
        """
        try:
            duration = int(duration_text)
            self.total_exercises += 1
            self.update_exercises_display(exercise_text, duration)
            self.log_exercise(exercise_text, duration)
        except ValueError:
            logger.debug("Invalid duration input. Please enter an integer.")
            self.ids.duration_input.text = ''
            
    def add_water(self, water_text):
        """Adds water intake to the total water count from the input text.

        Args:
            water_text (str): The input text containing water intake value.
        """
        try:
            water = int(water_text)
            self.total_water += water
            self.update_water_display()
        except ValueError:
            logger.debug("Invalid water input. Please enter an integer.")
            self.ids.water_input.text = ''

    def update_exercises_display(self, exercise_text, duration):
        """Updates the display for total exercises.

        Args:
            exercise_text (str): The name of the exercise.
            duration (int): Duration of the exercise in minutes.
        """
        self.ids.total_water.text = f'Total Water: {self.total_water} ml'


    def log_exercise(self, exercise_text, duration):
        """Logs exercise data in the exercise log.

        Args:
            exercise_text (str): The name of the exercise.
            duration (int): Duration of the exercise in minutes.
        """
        date = datetime.now().strftime('%Y-%m-%d')
        if date not in self.exercise_log:
            self.exercise_log[date] = []
        self.exercise_log[date].append({'exercise': exercise_text, 'duration': duration})
        logger.debug(f"Logged exercise: {exercise_text} for {duration} minutes on {date}")

    def show_exercise_log(self):
        """Displays the exercise log popup for the user to select a date."""
        try:
            from pglet import DatePicker

            date_picker = DatePicker()
            content = BoxLayout(orientation='vertical')
            content.add_widget(date_picker)
            
            self.exercise_log_popup = Popup(title='Exercise Log', content=content, size_hint=(0.8, 0.8))
            self.exercise_log_popup.open()
        except ImportError:
            logger.warning("DatePicker module not found. Ensure pglet is installed.")

    def display_log(self, date):
        """Displays the exercise log popup for the user to select a date."""
        if (date in self.exercise_log) and self.exercise_log[date]:
            exercises = self.exercise_log[date]
            log_text = '\n'.join([f"{exercise['exercise']} - {exercise['duration']} minutes" for exercise in exercises])
        else:
            log_text = 'No exercises logged for this date.'
        
        popup = Popup(title=f'Exercise Log for {date}', content=Label(text=log_text), size_hint=(0.9, 0.9))
        popup.open()

class CommunityScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class MyPageScreen(Screen):
    pass

class SettingsButton(Button):
    pass

class BottomNav(BoxLayout):
    pass
