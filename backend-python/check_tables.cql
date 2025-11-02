-- Check if tables exist in subjectplanning keyspace
-- Run this in DataGrip to see what tables you have

USE subjectplanning;

-- List all tables
SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'subjectplanning';

-- Check students table structure (if it exists)
DESCRIBE TABLE students;

-- Check courses table structure (if it exists)
DESCRIBE TABLE courses;

-- Check enrollments table structure (if it exists)
DESCRIBE TABLE enrollments;

-- Check risk_predictions table structure (if it exists)
DESCRIBE TABLE risk_predictions;
