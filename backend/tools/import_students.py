#!/usr/bin/env python3
"""
Import students CSV into Cassandra, hashing plain-text passwords with bcrypt.
Usage:
  python import_students.py --csv C:\path\to\students.csv --host localhost --port 9042 --keyspace subjectplanning

CSV should have headers: student_id,name,email,password,gpa,semester

This script writes rows into the students table. It assumes the table exists. If not, run the CREATE TABLE CQL first.
"""
import argparse
import csv
import uuid
from datetime import datetime
from passlib.hash import bcrypt
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def connect(host, port, username=None, password=None):
    if username and password:
        auth = PlainTextAuthProvider(username=username, password=password)
        cluster = Cluster([host], port=port, auth_provider=auth)
    else:
        cluster = Cluster([host], port=port)
    session = cluster.connect()
    return cluster, session


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=9042)
    p.add_argument("--keyspace", default="subjectplanning")
    p.add_argument("--username", default=None)
    p.add_argument("--password", default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cluster, session = connect(args.host, args.port, args.username, args.password)
    try:
        session.set_keyspace(args.keyspace)
    except Exception as e:
        print("Failed to set keyspace:", e)
        cluster.shutdown()
        return

    insert_cql = """
    INSERT INTO students (id, student_id, name, email, password_hash, gpa, semester, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    prepared = session.prepare(insert_cql)

    with open(args.csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            sid = uuid.uuid4()
            student_id = row.get('student_id') or row.get('studentId') or ''
            name = row.get('name') or ''
            email = row.get('email') or ''
            plain_password = row.get('password') or ''
            gpa = float(row.get('gpa')) if row.get('gpa') else 0.0
            semester = int(row.get('semester')) if row.get('semester') else 1

            password_hash = bcrypt.hash(plain_password) if plain_password else ''

            now = datetime.utcnow()
            if not args.dry_run:
                session.execute(prepared, (sid, student_id, name, email, password_hash, gpa, semester, now, now))
            count += 1
            print(f"Prepared insert for {email}")

    print(f"Processed {count} rows")
    cluster.shutdown()


if __name__ == '__main__':
    main()
