from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging


load_dotenv()

app = Flask(__name__)
CORS(app)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

model = None
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY is missing.")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    logger.info(" Gemini model initialized with models/gemini-1.5-pro-latest")

except Exception as e:
    logger.error(f" Gemini API initialization failed: {str(e)}")
    model = None

def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not model:
            return jsonify({"answer": "AI service is not available. Please try again later."})

        question = request.json.get('question', '').strip()
        if not question:
            return jsonify({"answer": "Please provide a question."})

        logger.info(f" Received question: {question}")


        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("DESCRIBE users")
            schema = cursor.fetchall()
            cursor.execute("SELECT * FROM users LIMIT 5")
            sample_data = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as db_error:
            logger.error(f" Database error: {str(db_error)}")
            return jsonify({"answer": "Database connection failed."})

        prompt = f"""
You are a helpful assistant. Answer questions about the 'users' table.

TABLE SCHEMA:
{schema}

SAMPLE DATA:
{sample_data}

USER QUESTION:
"{question}"

Respond in a clear, user-friendly way without showing SQL code.
        """

        # Generate content with Gemini
        try:
            logger.info(" Sending prompt to Gemini...")
            response = model.generate_content(prompt)
            return jsonify({"answer": response.text})
        except Exception as ai_error:
            logger.error(f" Gemini API error: {str(ai_error)}")
            return jsonify({"answer": "AI failed to generate a response. Please try again."})

    except Exception as e:
        logger.error(f" Unexpected error: {str(e)}")
        return jsonify({"answer": "An unexpected error occurred. Please try again."})

# Start Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
