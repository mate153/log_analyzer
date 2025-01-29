import psycopg2
import logging
from urllib.parse import urlparse
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

# DB CONFIG
def get_db_config(database_url):
    if not database_url:
        logger.critical("DATABASE_URL is not set in .env file")
        raise ValueError("DATABASE_URL is missing")

    result = urlparse(database_url)
    return {
        "dbname": result.path[1:],  # Path a /inventory_db formátumból "inventory_db"-re konvertálva
        "user": result.username,
        "password": result.password,
        "host": result.hostname,
        "port": result.port
    }

# GET DATABASE CONNECTION
def get_connection():
    try:
        db_config = get_db_config(os.getenv("DATABASE_URL"))
        connection = psycopg2.connect(**db_config)
        logger.debug("Database connection successfully established.")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

# INITIALIZE DB AND INSERT LOGS IF TABLES DON'T EXIST
def init_db_with_logs(database_url, log_file_path):
    try:
        db_config = get_db_config(database_url)
        with psycopg2.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_sources (
                    id SERIAL PRIMARY KEY,
                    source_ip INET,
                    endpoint TEXT,
                    UNIQUE (source_ip, endpoint)
                );
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    log_level VARCHAR(10) NOT NULL,
                    message TEXT NOT NULL,
                    details JSONB,
                    source_id INT REFERENCES log_sources(id) ON DELETE CASCADE
                );
                """)

                # Check if there is data in the `logs` table
                cursor.execute("SELECT COUNT(*) FROM logs;")
                log_count = cursor.fetchone()[0]

                # If there is no data, upload the logs
                if log_count == 0: 
                    logger.info("No logs found in database. Loading from log file...")
                    load_logs_from_file(cursor, log_file_path, connection)

                connection.commit()
                logger.info("Database initialization and log import successful.")

    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
    except psycopg2.Error as e:
        logger.error(f"Database error during initialization: {e}")
    except Exception as e:
        logger.critical(f"An unknown error occurred during database initialization: {e}")


# LOAD LOGS FROM FILE INTO DATABASE
def load_logs_from_file(cursor, log_file_path, connection):
    """Log fájl feldolgozása és adatok beszúrása az adatbázisba."""
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                timestamp, log_level, message, details, source_ip, endpoint = parse_log_line(line.strip())

                if not timestamp:
                    logger.warning(f"Skipped invalid log line: {line.strip()}")
                    continue

                # Log source beszúrása vagy lekérdezése
                cursor.execute("""
                INSERT INTO log_sources (source_ip, endpoint)
                VALUES (%s, %s)
                ON CONFLICT (source_ip, endpoint) DO NOTHING
                RETURNING id
                """, (source_ip, endpoint))
                result = cursor.fetchone()

                source_id = result[0] if result else None
                if not source_id:
                    cursor.execute("""
                    SELECT id FROM log_sources WHERE source_ip = %s AND endpoint = %s
                    """, (source_ip, endpoint))
                    source_id = cursor.fetchone()[0]

                # Log beszúrása
                cursor.execute("""
                INSERT INTO logs (timestamp, log_level, message, details, source_id)
                VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, log_level, message, details, source_id))

        logger.info(f"Log file '{log_file_path}' successfully processed.")

    except FileNotFoundError:
        logger.error(f"Log file '{log_file_path}' not found.")
    except Exception as e:
        logger.error(f"An error occurred while processing log file: {e}")

# PROCESS LOG FILE
def parse_log_line(line):
    try:
        # Splitting the log line along " - "
        parts = line.split(" - ", 2)

        if len(parts) < 3:
            raise ValueError(f"Invalid log line format: {line}")

        # Timestamp, log level, message
        timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S,%f")
        log_level = parts[1]
        message = parts[2]
        details = {}

        # Extract IP address and endpoint (if available)
        source_ip = None
        endpoint = None
        if "127.0.0.1" in message:
            source_ip = "127.0.0.1"
        if "endpoint hit" in message:
            endpoint = message.split(" ")[1]

        return timestamp, log_level, message, json.dumps(details), source_ip, endpoint

    except Exception as e:
        logger.error(f"Error parsing log line: {line.strip()} - {e}")
        return None, None, None, None, None, None
