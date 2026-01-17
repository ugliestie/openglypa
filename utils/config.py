import os
from dotenv import load_dotenv

load_dotenv()

RANDOM_SEND = True if os.getenv("RANDOM_RULE") == "True" else False
CHANCE = int(os.getenv("CHANCE"))
TOKEN = os.getenv("TOKEN")
USUAL_SYNTAX = True if os.getenv("USUAL_SYNTAX") == "True" else False