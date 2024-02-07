from dotenv import load_dotenv
import os

load_dotenv(".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")