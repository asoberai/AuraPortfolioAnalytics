from dotenv import load_dotenv
import os

load_dotenv()

# LimeTrader SDK Configuration (based on official documentation)
LIME_USERNAME = os.getenv("LIME_SDK_USERNAME")
LIME_PASSWORD = os.getenv("LIME_SDK_PASSWORD")
LIME_CLIENT_ID = os.getenv("LIME_SDK_CLIENT_ID")
LIME_CLIENT_SECRET = os.getenv("LIME_SDK_CLIENT_SECRET")
LIME_GRANT_TYPE = os.getenv("LIME_SDK_GRANT_TYPE", "password")
LIME_BASE_URL = os.getenv("LIME_SDK_BASE_URL", "https://api.lime.co")
LIME_AUTH_URL = os.getenv("LIME_SDK_AUTH_URL", "https://auth.lime.co") 