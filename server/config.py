import os
from dotenv import load_dotenv

load_dotenv()

# DB CONNECTION STRING
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")