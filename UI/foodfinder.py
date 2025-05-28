from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
import requests
import time
from api_clients import fetch_food_suggestions, fetch_food_data
import sqlite3
import hashlib
from api_clients import fetch_food_suggestions, fetch_food_data


from threading import Thread

def search_food(self, query):
    """Searches for food without blocking UI."""
    def fetch():
        food_data = fetch_food_suggestions(query, self.cache)
        self.display_food_results(food_data)

    Thread(target=fetch).start()

class FoodSearchApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Logo or header
        self.header = Label(text="Food Search", font_size=32, bold=True, color=(0.2, 0.6, 1, 1))
        self.layout.add_widget(self.header)

        # Input field for food search
        self.search_input = TextInput(
            hint_text="Search for food (e.g., chicken)",
            multiline=False,
            size_hint=(1, None),
            height=40,
            background_color=(0.9, 0.9, 0.9, 1),  # Light gray background for contrast
            foreground_color=(0, 0, 0, 1),  # Black text color
            font_size=18,  # Font size for visibility
            padding=[10, 10],  # Padding to avoid text being right at the edges
        )
        self.search_input.bind(text=self.on_text_input)
        self.layout.add_widget(self.search_input)
        
        # Drop-down area with scroll for suggestions
        self.dropdown_container = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.dropdown_container.bind(minimum_height=self.dropdown_container.setter('height'))
        self.dropdown_scroll = ScrollView(size_hint=(1, None), height=200)
        self.dropdown_scroll.add_widget(self.dropdown_container)
        self.layout.add_widget(self.dropdown_scroll)

        # Search button with standard appearance
        self.search_button = Button(
            text="Search",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.6, 1, 1),  # Blue background color
            color=(1, 1, 1, 1),  # White text color for contrast
            font_size=18,  # Font size for button text
        )
        self.search_button.bind(on_press=self.search_food)
        self.layout.add_widget(self.search_button)
        
        # Spinner for loading feedback
        self.loading_spinner = Spinner(size_hint=(None, None), size=(50, 50))
        self.loading_spinner.opacity = 0
        self.layout.add_widget(self.loading_spinner)

        # Custom "card" for displaying nutritional information
        self.info_card = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint=(1, None), height=200)
        self.info_card_header = Label(text="Macronutritional Information", bold=True, color=(0.2, 0.6, 1, 1))
        self.info_card.add_widget(self.info_card_header)

        # Labels for each nutrient within the card
        self.calories_label = Label(text="Calories: ", font_size=16)
        self.proteins_label = Label(text="Proteins: ", font_size=16)
        self.carbs_label = Label(text="Carbs: ", font_size=16)
        self.fats_label = Label(text="Fats: ", font_size=16)

        # Add nutrient labels to the info card
        for label in [self.calories_label, self.proteins_label, self.carbs_label, self.fats_label]:
            self.info_card.add_widget(label)

        # Label for serving size (moved here)
        self.serving_size_label = Label(text="Serving Size: ", font_size=16)
        self.info_card.add_widget(self.serving_size_label)
        
        # Label for brand name
        self.brand_label = Label(text="Brand: ", font_size=16)
        self.info_card.add_widget(self.brand_label)


        # Add the info card to the main layout
        self.layout.add_widget(self.info_card)

        # Initialize debounce timer and cache
        self.debounce_timer = None
        self.cache = {}
        
        return self.layout


    def on_text_input(self, instance, value):
        # Cancel previous debounce if still active
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        # Only search if at least 3 characters are typed
        if len(value) >= 3:
            self.loading_spinner.opacity = 1  # Show loading spinner
            self.debounce_timer = Clock.schedule_once(lambda dt: self.update_dropdown(value), 0.5)
        else:
            self.dropdown_container.clear_widgets()
            self.loading_spinner.opacity = 0  # Hide spinner if no search
    
    def update_dropdown(self, query):
        self.loading_spinner.opacity = 1  # Show loading spinner
        self.dropdown_container.clear_widgets()

        food_data = self.fetch_food_suggestions(query)
        if food_data:
            for item in food_data.get('common', []):
                product_name = item['food_name']
                btn = Button(text=product_name, size_hint_y=None, height=40, background_color=(0.95, 0.95, 0.95, 1), color=(0, 0, 0, 1))
                btn.bind(on_release=lambda btn: self.select_product(btn.text))
                self.dropdown_container.add_widget(btn)

    def on_text_input(self, instance, value):
        # Cancel previous debounce if still active
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        # Only search if at least 3 characters are typed
        if len(value) >= 3:
            self.loading_spinner.opacity = 1  # Show loading spinner
            self.debounce_timer = Clock.schedule_once(lambda dt: self.update_dropdown(value), 0.5)
        else:
            self.dropdown_container.clear_widgets()
            self.loading_spinner.opacity = 0  # Hide spinner if no search

    def fetch_food_suggestions(self, query):
        # Check if query is in cache
        if query in self.cache:
            return self.cache[query]

        url = 'https://trackapi.nutritionix.com/v2/search/instant'
        headers = {
            'x-app-id': APP_ID,
            'x-app-key': API_KEY,
        }
        params = {'query': query}

        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()  # Will raise an error for HTTP codes 4xx/5xx
                data = response.json()
            
                # Cache the result
                self.cache[query] = data
                return data

            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)  # Wait a moment before retrying
        print("Failed to fetch data after multiple attempts.")
        return None

    def fetch_food_data(self, food_name):
        url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
        headers = {
            'x-app-id': APP_ID,
            'x-app-key': API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json={"query": food_name})
        if response.status_code == 200:
            data = response.json()
            print("Fetched food data:", data)  # Debug: print the API response
            return data
        else:
            print("Failed to fetch data. Status code:", response.status_code)
            return None

    def get_macronutrients(self, food_data):
        if food_data and 'foods' in food_data and len(food_data['foods']) > 0:
            nutrients = food_data['foods'][0]
            serving_size_grams = nutrients.get('serving_weight_grams', 'N/A')
            serving_size_ounces = f"{round(serving_size_grams * 0.0353, 2)} oz" if serving_size_grams != 'N/A' else 'N/A'
            brand_name = nutrients.get('brand_name', '')
            brand_name = brand_name.strip() if brand_name else "No brand specified"  # Handle None or empty strings
            
            print("Parsed nutrients:", nutrients)  # Debug: print parsed nutrients
            return {
                'brand': brand_name,  # Add brand name to the returned data
                'calories': nutrients.get('nf_calories', 'N/A'),
                'proteins': nutrients.get('nf_protein', 'N/A'),
                'carbs': nutrients.get('nf_total_carbohydrate', 'N/A'),
                'fats': nutrients.get('nf_total_fat', 'N/A'),
                'serving_size_grams': serving_size_grams,
                'serving_size_ounces': serving_size_ounces
            }
        else:
            print("No information on macronutrients.")
            return None
        
def update_dropdown(self, query):
    food_data = fetch_food_suggestions(query, self.cache)
    if food_data:
        for item in food_data.get('common', []):
            product_name = item['food_name']
            btn = Button(text=product_name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.select_product(btn.text))
            self.dropdown_container.add_widget(btn)

def select_product(self, product_name):
    food_data = fetch_food_data(product_name)
    # Process food_data and update UI as needed


    def search_food(self, instance):
        query = self.search_input.text
        food_data = self.fetch_food_data(query)
        if food_data:
            nutrients = self.get_macronutrients(food_data)
            if nutrients:
                # Update labels with the nutritional information
                self.calories_label.text = f"Calories: {nutrients['calories']}"
                self.proteins_label.text = f"Proteins: {nutrients['proteins']}"
                self.carbs_label.text = f"Carbs: {nutrients['carbs']}"
                self.fats_label.text = f"Fats: {nutrients['fats']}"

if __name__ == '__main__':
    FoodSearchApp().run()
