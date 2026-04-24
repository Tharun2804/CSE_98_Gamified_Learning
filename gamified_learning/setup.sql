DROP DATABASE IF EXISTS gamified_learning;
CREATE DATABASE gamified_learning;
USE gamified_learning;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'parent', 'admin') NOT NULL,
    full_name VARCHAR(255),
    student_id VARCHAR(50),
    employee_id VARCHAR(50),
    email VARCHAR(255),
    school_name VARCHAR(255),
    class_grade VARCHAR(50),
    department VARCHAR(255),
    parent_contact VARCHAR(255),
    relationship VARCHAR(50),
    linked_student_id VARCHAR(50),
    dob DATE,
    points INT DEFAULT 0,
    level INT DEFAULT 1,
    approved BOOLEAN DEFAULT FALSE,
    UNIQUE KEY unique_user (username, role)
);

CREATE TABLE lessons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    points INT DEFAULT 10
);

CREATE TABLE quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    title VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    option_a VARCHAR(255),
    option_b VARCHAR(255),
    option_c VARCHAR(255),
    option_d VARCHAR(255),
    correct_answer CHAR(1),
    points INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

CREATE TABLE videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    title VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

CREATE TABLE presentations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    title VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

CREATE TABLE quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    quiz_id INT,
    answer CHAR(1),
    is_correct BOOLEAN,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);

CREATE TABLE progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    lesson_id INT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);

INSERT INTO users (username, password, role, full_name, points, level, approved) VALUES 
('john', 'pass123', 'student', 'John Doe', 0, 1, TRUE),
('mary', 'pass123', 'student', 'Mary Smith', 0, 1, TRUE),
('mr_smith', 'pass123', 'teacher', 'Mr. Smith', 0, 1, TRUE),
('mrs_johnson', 'pass123', 'parent', 'Mrs. Johnson', 0, 1, TRUE),
('Raja', '123456789', 'admin', 'Raja', 0, 1, TRUE);

INSERT INTO lessons (title, description, points) VALUES 
('Introduction to Python', 'Learn Python basics', 10),
('Variables and Data Types', 'Understanding variables', 10),
('Control Flow', 'If statements and loops', 15),
('Functions', 'Creating reusable code', 15);
