from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("LIME_API_KEY")
API_SECRET = os.getenv("LIME_API_SECRET")
ACCOUNT_ID = os.getenv("LIME_ACCOUNT_ID") 