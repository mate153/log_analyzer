from flask import Blueprint, jsonify
import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from db.database import get_db_config
from config import DATABASE_URL

logs_bp = Blueprint('logs', __name__)
logger = logging.getLogger(__name__)

# DB CONNECT
def get_connection():
    try:
        db_config = get_db_config(DATABASE_URL)
        connection = psycopg2.connect(**db_config)
        logger.debug("Database connection successfully established.")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

# GET ALL LOGS
@logs_bp.route('/', methods=['GET'])
def get_logs():
    logger.debug("Get all logs endpoint hit.")
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                logs.id, 
                logs.timestamp, 
                logs.log_level, 
                logs.message, 
                logs.details, 
                log_sources.source_ip, 
                log_sources.endpoint
            FROM logs
            LEFT JOIN log_sources ON logs.source_id = log_sources.id
            ORDER BY logs.timestamp DESC;
        """)
        
        logs = cursor.fetchall()
        cursor.close()
        connection.close()

        logger.info(f"{len(logs)} log read.")
        return jsonify(logs), 200
    except Exception as e:
        logger.error(f"An error occurred while retrieving the logs: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
