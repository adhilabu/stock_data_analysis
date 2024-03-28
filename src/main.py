from fastapi import FastAPI
from src.stock.router import stock_app

app = FastAPI()
app.include_router(stock_app)

@app.get("/")
async def root():
    return {"message": "Hello World"}
