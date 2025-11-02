-- PathFinder Academic Dashboard - Cassandra Schema
-- Run this in DataGrip or cqlsh to create all required tables
-- Make sure you're connected to keyspace: subjectplanning

USE subjectplanning;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY,
    student_id TEXT,
    name TEXT,
    email TEXT,
    password_hash TEXT,
    gpa DOUBLE,
    semester INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY,
    course_code TEXT,
    course_name TEXT,
    credits INT,
    difficulty DOUBLE,
    prerequisites LIST<TEXT>,
    description TEXT,
    created_at TIMESTAMP
);

-- Enrollments table
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY,
    student_id UUID,
    course_id UUID,
    semester INT,
    grade TEXT,
    status TEXT,
    attendance_rate DOUBLE,
    enrolled_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Risk predictions table
CREATE TABLE IF NOT EXISTS risk_predictions (
    id UUID PRIMARY KEY,
    student_id UUID,
    course_id UUID,
    risk_level TEXT,
    confidence DOUBLE,
    factors MAP<TEXT, DOUBLE>,
    recommendations LIST<TEXT>,
    predicted_grade TEXT,
    created_at TIMESTAMP
);

-- Create indexes for common queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_risk_student ON risk_predictions(student_id);
