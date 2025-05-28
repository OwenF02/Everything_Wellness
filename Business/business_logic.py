# business_logic.py

import logging

logger = logging.getLogger(__name__)

def calculate_total_calories(meals):
    """Calculates the total calories from a list of meals."""
    total_calories = sum(meal.get('calories', 0) for meal in meals)
    logger.debug(f"Total calories calculated: {total_calories}")
    return total_calories

def add_calories_for_meal(meal, calories):
    """Adds calories to a meal."""
    meal['calories'] = meal.get('calories', 0) + calories
    logger.debug(f"Added {calories} calories to meal: {meal}")
    return meal

def calculate_nutrition(meals):
    """Calculates total calories, proteins, fats, and carbs from meals."""
    totals = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
    for meal in meals:
        totals["calories"] += meal.get("calories", 0)
        totals["proteins"] += meal.get("proteins", 0)
        totals["fats"] += meal.get("fats", 0)
        totals["carbs"] += meal.get("carbs", 0)
    return totals
