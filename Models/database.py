# database.py

import mysql.connector
from mysql.connector import Error
import bcrypt
import logging

# Setting up logging for the database module
logger = logging.getLogger(__name__)

from mysql.connector import pooling
from config import Config

db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
)

def get_connection():
    """Returns a database connection from the pool."""
    return db_pool.get_connection()


def hash_password(password):
    """Hashes a password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_connection():
    """Establishes and returns a connection to the MySQL database.
    
    Returns:
        connection: MySQL connection object if successful, else None.
    """
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="Jadekirby12@",
            database="everything_wellness"
        )
        if connection.is_connected():
            logger.info("Successfully connected to the database")
            return connection
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        return None

def register_user(username, password):
    """Registers a new user by hashing their password and storing the details in the database.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.

    Raises:
        Exception: If there's an error during the database operations.
    """
    hashed_password = hash_password(password)
    try:
        connection = create_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, hashed_password))
            connection.commit()
            logger.info("User registered successfully.")
    except Error as e:
        logger.error(f"Error registering user: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def retrieve_password_from_db(username):
    """Fetches the hashed password for the provided username from the database.
    
    Args:
        username (str): The username for which to fetch the password.

    Returns:
        str: Hashed password if found, else None.
    """
    try:
        connection = create_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Error as e:
        logger.error(f"Database error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def log_food(user_id, calories, carbs, fats, proteins, meal_description):
    """Logs food data to the database."""
    try:
        connection = create_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO nutrition (user_id, date, calories_intake, carbohydrates, fats, proteins, meal_description)
            VALUES (%s, CURDATE(), %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (user_id, calories, carbs, fats, proteins, meal_description))
            connection.commit()
            logger.info("Food log added successfully.")
    except Error as e:
        logger.error(f"Error logging food: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
