# api_clients.py

import requests
import time
import logging

logger = logging.getLogger(__name__)

# Nutritionix API credentials
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")


def fetch_food_suggestions(query, cache):
    """Fetches food suggestions from the Nutritionix API."""
    if query in cache:
        return cache[query]

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
            response.raise_for_status()
            data = response.json()
            cache[query] = data
            return data
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)
    logger.error("Failed to fetch data after multiple attempts.")
    return None

def fetch_food_data(food_name):
    """Fetches food data from the Nutritionix API."""
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    headers = {
        'x-app-id': APP_ID,
        'x-app-key': API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json={"query": food_name})
    if response.status_code == 200:
        data = response.json()
        logger.debug(f"Fetched food data: {data}")
        return data
    else:
        logger.error(f"Failed to fetch data. Status code: {response.status_code}")
        return None

def get_nutritional_info(barcode):
    """Fetches nutritional information for a barcode from OpenFoodFacts API."""
    try:
        api_url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
        response = requests.get(api_url)
        response.raise_for_status()
        product_data = response.json()
        if product_data['status'] == 1:
            return product_data['product']
        else:
            logger.warning("Product not found")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f'API request failed: {e}')
        return None
