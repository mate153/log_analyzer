import os
from openai import OpenAI
import logging
from flask import Blueprint, jsonify
from db.database import get_connection

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)

# OpenAI API Key (tárold az .env fájlban!)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# AI elemzés végpont
@ai_bp.route('/analyze', methods=['GET'])
def analyze_logs():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Az utolsó 100 logot küldjük az AI-nak
        cursor.execute("""
            SELECT timestamp, log_level, message FROM logs
            ORDER BY timestamp DESC LIMIT 100
        """)
        logs = cursor.fetchall()
        cursor.close()
        connection.close()

        # Logokat formázzuk promptként
        log_text = "\n".join([f"{row[0]} [{row[1]}] {row[2]}" for row in logs])

        # OpenAI API új verzió szerint
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a log analysis AI and speak in Hungarian."},
                {"role": "user", "content": f"Analyze these logs and summarize key issues:\n{log_text}"}
            ]
        )

        ai_response = response.choices[0].message.content

        logger.info("AI log analysis completed.")
        return jsonify({"analysis": ai_response}), 200

    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return jsonify({"error": "AI analysis failed"}), 500
