# Development tools: Local Cassandra + data import

This folder contains lightweight helpers to run a local Cassandra instance and import CSV datasets for development.

## Start a local Cassandra (Docker)

Requires Docker Desktop or Docker Engine.

```powershell
cd backend\tools
docker compose -f docker-compose.cassandra.yml up -d
# wait a minute for Cassandra to initialise
docker logs -f cassandra-local
```

The container exposes CQL on port 9042.

## Create keyspace and table (cqlsh)

You can use the `cqlsh` helper container included in the compose or run `docker exec` into the cassandra container:

```powershell
# create keyspace
docker exec -it cassandra-local cqlsh -e "CREATE KEYSPACE IF NOT EXISTS subjectplanning WITH replication = {'class':'SimpleStrategy','replication_factor':1};"

# create the students table (if not already created by your app)
docker exec -it cassandra-local cqlsh -e "CREATE TABLE IF NOT EXISTS subjectplanning.students (id uuid PRIMARY KEY, student_id text, name text, email text, password_hash text, gpa double, semester int, created_at timestamp, updated_at timestamp);"
```

## Import CSV (recommended: use the Python importer)

If your CSV includes plain-text passwords, use the Python importer to hash passwords before inserting:

```powershell
# create venv and install deps
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
pip install cassandra-driver passlib pandas

# run importer (adjust path to your CSV)
python ..\import_students.py --csv C:\path\to\students.csv --host localhost --port 9042 --keyspace subjectplanning
```

If your CSV already contains bcrypt password hashes, you can COPY it into the container and use `cqlsh COPY`:

```powershell
# copy CSV into container
docker cp C:\path\to\students.csv cassandra-local:/tmp/students.csv
# run COPY (must match column order)
docker exec -it cassandra-local cqlsh -e "COPY subjectplanning.students (id, student_id, name, email, password_hash, gpa, semester, created_at, updated_at) FROM '/tmp/students.csv' WITH HEADER = TRUE;"
```

## Pointing your application at the local Cassandra

Set environment variables before starting the backend (PowerShell):

```powershell
$env:CASSANDRA_USERNAME=''
$env:CASSANDRA_PASSWORD=''
# or set to your test user if you created one
cd C:\DieAndCry\backend
sbt run
```

The app will try to create keyspace/tables automatically on startup if needed.

## Notes
- The docker image uses the default Cassandra config (no auth). If you enable auth, update `backend/conf/application.conf` or set environment variables accordingly.
- For CI or tests, consider Testcontainers instead of a local docker compose.
