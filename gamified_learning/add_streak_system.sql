USE gamified_learning;

-- Add streak columns to users table
ALTER TABLE users 
ADD COLUMN current_streak INT DEFAULT 0,
ADD COLUMN longest_streak INT DEFAULT 0,
ADD COLUMN last_activity_date DATE;

-- Create daily_activity table to track daily engagement
CREATE TABLE daily_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    activity_date DATE NOT NULL,
    lessons_completed INT DEFAULT 0,
    quizzes_attempted INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES users(id),
    UNIQUE KEY unique_daily_activity (student_id, activity_date)
);
