from fastapi import FastAPI
from src.stock.router import stock_app
from fastapi.middleware.cors import CORSMiddleware


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

@app.get("/")
async def root():
    return {"message": "Hello World"}
