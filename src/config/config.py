
import os
from dotenv import load_dotenv

ENV_FILE_PATH = '.env'  # Path to your .env file
LOG_FILE_PATH = 'token_log.txt'  # Path to your log file
TEMP_FOLDER = 'temp'

def set_env():
    # Load environment variables from the .env file
    if os.path.isfile(ENV_FILE_PATH):
        load_dotenv(ENV_FILE_PATH)
    else:
        print(f"Warning: {ENV_FILE_PATH} does not exist. Ensure the file is present.")
    
    global UPSTOX_CLIENT_ID, UPSTOX_CLIENT_SECRET, UPSTOX_REDIRECT_URI, UPSTOX_AUTH_URL, UPSTOX_TOKEN_URL, UPSTOX_ACCESS_TOKEN
    
    UPSTOX_CLIENT_ID = os.getenv("UPSTOX_CLIENT_ID")
    UPSTOX_CLIENT_SECRET = os.getenv("UPSTOX_CLIENT_SECRET")
    UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")
    UPSTOX_AUTH_URL = os.getenv("UPSTOX_AUTH_URL")
    UPSTOX_TOKEN_URL = os.getenv("UPSTOX_TOKEN_URL")
    UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
