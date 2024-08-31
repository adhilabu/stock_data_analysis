from datetime import datetime
from src.schemas.schemas import TokenResponse
from src.router.router import stock_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from urllib.parse import urlencode
from src.config.config import set_env
# Setting env
set_env()
from src.config.config import ENV_FILE_PATH, LOG_FILE_PATH, UPSTOX_AUTH_URL, UPSTOX_CLIENT_ID, UPSTOX_CLIENT_SECRET, UPSTOX_REDIRECT_URI, UPSTOX_TOKEN_URL


app = FastAPI()
app.include_router(stock_app)
# Allow requests from specific origins (e.g., http://localhost:8080)
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://www.aksyo.in"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/login")
async def login():
    # Construct the authorization URL
    query_params = {
        "response_type": "code",
        "client_id": UPSTOX_CLIENT_ID,
        "redirect_uri": UPSTOX_REDIRECT_URI
    }
    url = f"{UPSTOX_AUTH_URL}?{urlencode(query_params)}"
    return RedirectResponse(url)

@app.get("/callback")
async def callback(code: str):
    # Exchange the authorization code for an access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            UPSTOX_TOKEN_URL,
            data={
                "code": code,
                "client_id": UPSTOX_CLIENT_ID,
                "client_secret": UPSTOX_CLIENT_SECRET,
                "redirect_uri": UPSTOX_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to exchange code for token")
        
        token_response = response.json()
        token_data = TokenResponse(**token_response)

        # Update ACCESS_TOKEN in env.sh file
        update_env_sh(ENV_FILE_PATH, token_data.access_token)

        # Log the token and timestamp to a file
        with open(LOG_FILE_PATH, 'a') as log_file:
            timestamp = datetime.now().isoformat()
            log_file.write(f"{timestamp} - ACCESS_TOKEN: {token_data.access_token}\n")

        return token_data

@app.get("/hello")
async def hello():
    return {"message": "Hello trader"}


@app.get("/")
async def forecast_message():
    return "Forecasting Soon ..."

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