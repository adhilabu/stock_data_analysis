from datetime import date as dt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd
import yfinance as yf
from src.stock.service import analyze_symbol_df
from src.stock.schemas import StockDayAnalysisRequest, StockDayAnalysisResponse
import os

stock_app = APIRouter(
    prefix="/analyse",
)


@stock_app.post("/symbol/day/", response_model=StockDayAnalysisResponse)
async def get_symbol_analysis_for_next_day(req: StockDayAnalysisRequest):
    symbol = req.symbol
    analysis_date = req.analysis_date if req.analysis_date else dt.today()
    analysis_date_str = analysis_date.strftime('%d_%m_%Y')
    file_name = f'{symbol}_{analysis_date_str}.csv'
    if os.path.exists(file_name):
        symbol_df = pd.read_csv(file_name, index_col=0)
    else:
        symbol_df = yf.Ticker(symbol)
        symbol_df = symbol_df.history(period="max")
        symbol_df.to_csv(file_name)
    analysis_response: StockDayAnalysisResponse = await analyze_symbol_df(req=req, symbol_df=symbol_df)
    return analysis_response