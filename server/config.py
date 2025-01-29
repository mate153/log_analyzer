import os
from dotenv import load_dotenv

load_dotenv()

# LOG FILE LOCATION
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# LOG FILE PATH
LOG_FILE_PATH = "log/example.log"

# DB CONNECTION STRING
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

# OPENAI API KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env file")