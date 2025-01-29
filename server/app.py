import logging
import os
from flask import Flask
from flask_cors import CORS
from db.database import init_db_with_logs
from routes.logs_routes import logs_bp
from routes.ai_routes import ai_bp
from config import LOG_DIR, LOG_FILE

app = Flask(__name__)

# CREATE FOLDER IF NOT EXIST
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# SETUP LOGGING
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# FILE LOG HANDLER
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')
file_handler.setFormatter(file_formatter)

# CONSOLE LOG HANDLER
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# ADD LOG SETUP
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Flask application started...")

# CORS POLICY
CORS(app)

# INITIALIZE DB
try:
    init_db_with_logs()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# REGISTER BLUEPRINT
app.register_blueprint(logs_bp, url_prefix='/api/logs')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

if __name__ == '__main__':
    app.run(debug=True)
