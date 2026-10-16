import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DB_URL = 'sqlite+aiosqlite:///groups_settings.db'