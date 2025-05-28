import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()  # Load environment variables from .env file

class Config:
    DEBUG = True
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "everything_wellness")
    API_ID = os.getenv("API_ID", "your_nutritionix_id")
    API_KEY = os.getenv("API_KEY", "your_nutritionix_api_key")


# Fix: Import inside the function to avoid circular imports
def login(username, password):
    from Models.database import retrieve_password_from_db  # Move import here
    
    stored_password = retrieve_password_from_db(username)
    if stored_password and bcrypt.checkpw(password.encode(), stored_password.encode()):
        print("Login successful!")
    else:
        print("Invalid credentials.")

import requests
from config import Config

def fetch_food_suggestions(query, cache):
    """Fetches food suggestions from Nutritionix API with caching."""
    if query in cache:
        return cache[query]

    url = "https://trackapi.nutritionix.com/v2/search/instant"
    headers = {
        "x-app-id": Config.API_ID,  # Corrected
        "x-app-key": Config.API_KEY,  # Corrected
    }
    
    try:
        response = requests.get(url, headers=headers, params={"query": query}, timeout=5)
        response.raise_for_status()
        cache[query] = response.json()
        return cache[query]
    except requests.Timeout:
        print("Request timed out.")
    except requests.RequestException as e:
        print(f"API error: {e}")
    return None

# Fix: Corrected Config.API_ID and Config.API_KEY