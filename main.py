# imports to scan barcodes for food.
from pyzbar.pyzbar import decode
from PIL import Image
import requests

# camera import
import cv2
import numpy as np

# import logging
import logging
from Apis.api_clients import get_nutritional_info
from Business.business_logic import calculate_total_calories, add_calories_for_meal
from Models.database import log_food, register_user

def calculate_and_display_total_calories(self):
    total_calories = calculate_total_calories(self.food_log)
    self.total_calories_label.text = f"Total Calories: {total_calories}"

def log_food_entry(self, food_data):
    log_food(
        user_id=1,  # Replace with the actual user ID
        calories=food_data['calories'],
        carbs=food_data['carbs'],
        fats=food_data['fats'],
        proteins=food_data['proteins'],
        meal_description="Logged via UI"
    )
    
# kv imports
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.list import MDList, MDListItem
from kivymd.uix.textfield import MDTextField


# date picker import (logging exercises)
from datetime import datetime
import pglet
from pglet import DatePicker  

from UI.screen_classes import LoginScreen, RegisterScreen, SocializingScreen, TrackingScreen, CommunityScreen, SettingsScreen, MyPageScreen
import os

# Setting up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# date picker 
class DatePicker(BoxLayout):
    """Class for a date picker to keep track of when exercises occur."""
     
    def __init__(self, **kwargs):
        """Initializes the DatePicker layout and button."""
        super(DatePicker, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text='Select Date')
        self.add_widget(self.label)

        self.button = Button(text='Pick Date')
        self.button.bind(on_press=self.show_popup)
        self.add_widget(self.button)

    def show_popup(self, instance):
        """Displays a popup for date selection."""
        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(Label(text='Date Picker'))
        popup_content.add_widget(Button(text='Close', on_press=lambda x: self.popup.dismiss()))
        
        self.popup = Popup(title='Date Picker', content=popup_content)
        self.popup.open()

class EverythingWellnessApp(MDApp):
    """Main application class for the Everything Wellness fitness app."""
    
    def build(self):
        """Builds the main layout of the application by loading KV files.

        Attempts to load multiple KV files that define the UI components for 
        different screens of the app. If successful, the main layout is returned.

        Returns:
            kivy.uix.boxlayout.BoxLayout: The main layout of the app.
        
        Raises:
            Exception: If there's an error while loading the KV files, it will log the error.
        """
        # Set the app theme (Must be inside a method!)
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        kv_directory = os.path.join(os.path.dirname(__file__), "UI", "screens")
    
        for kv_file in ["bottom_nav.kv", "login.kv", "register.kv", "socializing.kv",
                    "tracking.kv", "community.kv", "settings.kv", "mypage.kv", "main.kv"]:
            kv_path = os.path.join(kv_directory, kv_file)
            if os.path.exists(kv_path):
                print(f"✅ Loading {kv_path}")  # Debug print
                Builder.load_file(kv_path)
            else:
                print(f"⚠️ Warning: {kv_path} not found!")  # Debug print

        main_kv_path = os.path.join(kv_directory, "main.kv")
        if os.path.exists(main_kv_path):
            print("✅ main.kv found and loading!")
            return Builder.load_file(main_kv_path)
        else:
            print("❌ ERROR: main.kv NOT found! White screen issue!")
            return None
    
    def on_login_button_press(self):
        username = self.ids.username_input.text  # Assuming this is the ID for the username input
        password = self.ids.password_input.text  # Assuming this is the ID for the password input
        self.login(username, password)  # Call the login method with the input values

    # Login function
    def login(self, username, password):
        """Handles user login by validating credentials against hardcoded values.

        Compares the provided username and password against hardcoded values.
        If valid, it transitions to the socializing screen; otherwise, it
        displays an error message.

        Args:
            username (str): The username entered by the user.
            password (str): The password entered by the user.
        
        Returns:
            None
        
        Raises:
            Exception: If there's an error during the login process.
        """
        # Hardcoded credentials for testing
        test_username = "user"
        test_password = "pass"
        
        # Check if the provided username and password match the test credentials
        if username == test_username and password == test_password:
            self.root.current = 'socializing'  # Transition to the socializing screen
            return
        
        # If credentials do not match, display an error message
        current_screen = self.root.get_screen('login')  # assuming 'login' is the name of the LoginScreen
        current_screen.ids.error_message.text = 'Invalid username or password'

    # Add post to socializing screen
    def add_post(self):
        """Adds a new post to the socializing screen.

        This function delegates the task of adding a post to the 
        SocializingScreen class, allowing users to share updates.

        Returns:
            None
        """
        socializing_screen = self.root.get_screen('socializing')
        socializing_screen.add_post()

    # Registration function (NEW)
    def register(self, username, password, confirm_password):
        """Handles user registration by storing user details in the database.

        Validates the provided username and passwords. If the passwords match,
        the user is registered in the database, and a success message is displayed.

        Args:
            username (str): The username entered by the user.
            password (str): The password entered by the user.
            confirm_password (str): The confirmation of the password.

        Returns:
            None
        
        Raises:
            Exception: If there's an error during the registration process.
        """
        try:
            if password != confirm_password:
                self.display_error("Passwords do not match.")
                return

            register_user(username, password)  # Now using the imported function
            self.display_error("Registration successful! Please log in.")
            self.root.current = 'login'
        except Exception as e:
            logger.debug(f"Error during registration: {e}")

    def display_error(self, error_message):
        """Displays an error message to the user in a popup.

        Creates a popup window displaying the specified error message 
        for user feedback.

        Args:
            error_message (str): The message to display to the user.

        Returns:
            None
        """
        # Error message popup or update error label
        popup = Popup(title='Error', content=Label(text=error_message), size_hint=(0.6, 0.4))
        popup.open()


if __name__ == '__main__':
    EverythingWellnessApp().run()
