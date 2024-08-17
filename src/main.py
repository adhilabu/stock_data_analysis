from datetime import datetime
from dotenv import load_dotenv
from src.router.router import stock_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
from urllib.parse import urlencode
import os
from taipy.gui import Gui

app = FastAPI()
app.include_router(stock_app)
# Allow requests from specific origins (e.g., http://localhost:8080)
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# # Load environment variables from .env file
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
auth_url = os.getenv("AUTH_URL")
token_url = os.getenv("TOKEN_URL")
env_file_path = 'env.sh'  # Path to your env.sh file
log_file_path = 'token_log.txt'  # Path to your log file

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

@app.get("/login")
async def login():
    # Construct the authorization URL
    query_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri
    }
    url = f"{auth_url}?{urlencode(query_params)}"
    return RedirectResponse(url)

@app.get("/callback")
async def callback(code: str):
    # Exchange the authorization code for an access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to exchange code for token")
        
        token_response = response.json()
        token_data = TokenResponse(**token_response)

        # Update ACCESS_TOKEN in env.sh file
        update_env_sh(env_file_path, token_data.access_token)

        # Log the token and timestamp to a file
        with open(log_file_path, 'a') as log_file:
            timestamp = datetime.now().isoformat()
            log_file.write(f"{timestamp} - ACCESS_TOKEN: {token_data.access_token}\n")

        return token_data

@app.get("/hello")
async def hello():
    return {"message": "Hello trader"}

def update_env_sh(file_path: str, access_token: str):
    # Read the existing content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Update the ACCESS_TOKEN line
    with open(file_path, 'w') as file:
        for line in lines:
            if line.startswith('export ACCESS_TOKEN='):
                file.write(f'export ACCESS_TOKEN="{access_token}"\n')
            else:
                file.write(line)

