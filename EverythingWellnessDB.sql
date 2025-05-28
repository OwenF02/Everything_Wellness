USE everything_wellness;

-- Create the users table with all necessary fields
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT,
    gender ENUM('Male', 'Female', 'Prefer not to say', 'Other'),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    fitness_goal VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create other tables with consistent naming
CREATE TABLE IF NOT EXISTS Activities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    duration INT,
    distance DECIMAL(6,2),
    calories_burned DECIMAL(6,2),
    heart_rate INT,
    activity_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS WorkoutLogs ( 
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE,
    exercise VARCHAR(100),
    sets INT,
    reps INT,
    weight DECIMAL(5,2),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Nutrition (
    nutrition_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE,
    calories_intake DECIMAL(6,2),
    carbohydrates DECIMAL(6,2),
    fats DECIMAL(6,2),
    proteins DECIMAL(6,2),
    meal_description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE,
    weight DECIMAL(5,2),
    body_measurements VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    goal_description VARCHAR(255),
    status ENUM('Pending', 'Achieved', 'Failed'),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS SocialConnections (
    connection_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    friend_user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_user_id) REFERENCES users(id) ON DELETE CASCADE
);

SHOW TABLES;


