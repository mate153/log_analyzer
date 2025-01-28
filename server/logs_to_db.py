import psycopg2
import json
from datetime import datetime

# PostgreSQL kapcsolat beállítása
DB_CONFIG = {
    'dbname': 'your_database',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}

# Egy log sor feldolgozása
def parse_log_line(line):
    parts = line.split(" - ")
    timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S,%f")
    log_level = parts[1]
    message = parts[2]
    details = {}
    source_ip = None
    endpoint = None

    if "127.0.0.1" in message:
        source_ip = "127.0.0.1"
    if "endpoint hit" in message:
        endpoint = message.split(" ")[1]

    # Ha vannak további részletek, kulcs-érték párok feldolgozása
    if len(parts) > 3:
        try:
            details = dict(item.split("=") for item in parts[3].split(", "))
        except ValueError:
            pass

    return timestamp, log_level, message, json.dumps(details), source_ip, endpoint

# Ellenőrizzük, hogy a source_ip és endpoint létezik-e a log_sources táblában
def get_or_create_source_id(cursor, source_ip, endpoint):
    cursor.execute("""
        SELECT id FROM log_sources WHERE source_ip = %s AND endpoint = %s
    """, (source_ip, endpoint))
    result = cursor.fetchone()

    if result:
        return result[0]  # Már létezik, visszaadjuk az ID-t
    else:
        cursor.execute("""
            INSERT INTO log_sources (source_ip, endpoint) VALUES (%s, %s) RETURNING id
        """, (source_ip, endpoint))
        return cursor.fetchone()[0]  # Új ID-t adunk vissza

# Adatok betöltése az adatbázisba
def load_logs_to_db(log_file):
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    with open(log_file, 'r') as file:
        for line in file:
            try:
                timestamp, log_level, message, details, source_ip, endpoint = parse_log_line(line.strip())

                # Ha van IP és endpoint, keressük meg a source_id-t
                source_id = None
                if source_ip and endpoint:
                    source_id = get_or_create_source_id(cursor, source_ip, endpoint)

                # Log beszúrása
                cursor.execute("""
                    INSERT INTO logs (timestamp, log_level, message, details, source_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (timestamp, log_level, message, details, source_id))
            except Exception as e:
                print(f"Hiba történt a következő sor feldolgozásánál: {line.strip()}")
                print(e)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Logok sikeresen betöltve az adatbázisba.")

# Futtatás
if __name__ == "__main__":
    log_file_path = "example.log"  # Itt add meg a log fájl nevét
    load_logs_to_db(log_file_path)
