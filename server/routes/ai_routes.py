from openai import OpenAI
import logging
from flask import Blueprint, jsonify
from db.database import get_connection
from config import OPENAI_API_KEY

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

# AI ANALYSIS ENDPOINT
@ai_bp.route('/analyze', methods=['GET'])
def analyze_logs():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # LAST 100 LOG SEND TO AI
        cursor.execute("""
            SELECT timestamp, log_level, message FROM logs
            ORDER BY timestamp DESC LIMIT 100
        """)
        logs = cursor.fetchall()
        cursor.close()
        connection.close()

        if not logs:
            return jsonify({"analysis": "Nincs elérhető log adat az AI elemzéshez."})

        # LOGS FORMATTED AS PROMPTS
        log_text = "\n".join([f"{row[0]} [{row[1]}] {row[2]}" for row in logs])

        # OPENAI API & PROMT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a log analysis AI and speak in Hungarian. Provide structured insights like this: \n\n - 🔴 Kritikus hibák: \n - ⚠️ Figyelmeztetések: \n - ℹ️ Információk: \n\n"},
                {"role": "user", "content": f"Analyze these logs and summarize key issues:\n{log_text}"}
            ]
        )

        ai_response = response.choices[0].message.content

        logger.info("AI log analysis completed.")
        return jsonify({"analysis": ai_response}), 200

    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return jsonify({"error": "AI analysis failed"}), 500
