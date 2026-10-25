import os
import sys

from dotenv import load_dotenv

load_dotenv()

TOKEN: str = str(os.getenv("TOKEN"))
if TOKEN == 'None':
    print('Токена бота нет, пожалуйста, проверьте .env')
    sys.exit(1)
    
DB_URL = 'sqlite+aiosqlite:///groups_settings.db'