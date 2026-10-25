import os
import sys

from dotenv import load_dotenv
from rich import print

load_dotenv()

TOKEN: str = str(os.getenv("TOKEN"))
if TOKEN == 'None':
    print('[red][b]Токена бота нет, пожалуйста, проверьте .env[/b][/red]')
    sys.exit(1)
    
DB_URL = 'sqlite+aiosqlite:///groups_settings.db'