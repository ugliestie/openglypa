import os
from dotenv import load_dotenv

load_dotenv()

RANDOM_SEND = True if os.getenv("RANDOM_RULE") == "True" else False
TOKEN = os.getenv("TOKEN")
USUAL_SYNTAX = True if os.getenv("USUAL_SYNTAX") == "True" else False