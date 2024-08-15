from datetime import date as dt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd
import yfinance as yf
from src.stock.service import analyze_symbol_df, analyze_symbol_df_v3, get_ticks
from src.stock.schemas import AllSymbolsResponse, StockDayAnalysisOptionRequest, StockDayAnalysisRequest, StockDayAnalysisResponse, StockDayAnalysisV3Response
import os

stock_app = APIRouter(
    prefix="/analyse",
)


@stock_app.post("/symbol/day/", response_model=StockDayAnalysisResponse)
async def get_symbol_analysis_for_next_day(req: StockDayAnalysisRequest):
    symbol = req.symbol
    today_str = dt.today().strftime('%d_%m_%Y')
    file_name = f'temp/{symbol}_{today_str}.csv'
    if os.path.exists(file_name):
        symbol_df = pd.read_csv(file_name, index_col=0)
    else:
        symbol_df = yf.Ticker(symbol)
        symbol_df = symbol_df.history(period="max")
        symbol_df.to_csv(file_name)
    analysis_response: StockDayAnalysisResponse = await analyze_symbol_df(req=req, symbol_df=symbol_df)
    return analysis_response

@stock_app.get("/get/symbols/list/", response_model=AllSymbolsResponse)
async def get_all_symbols():
    return get_ticks()

@stock_app.post("/v3/symbol/day/", response_model=StockDayAnalysisV3Response)
async def get_symbol_analysis_for_next_day(req: StockDayAnalysisRequest):
    symbol = req.symbol
    today_str = dt.today().strftime('%d_%m_%Y')
    file_name = f'temp/{symbol}_{today_str}.csv'
    if os.path.exists(file_name):
        symbol_df = pd.read_csv(file_name, index_col=0)
    else:
        symbol_df = yf.Ticker(symbol)
        symbol_df = symbol_df.history(period="max")
        symbol_df.to_csv(file_name)
    analysis_response: StockDayAnalysisV3Response = await analyze_symbol_df_v3(req=req, symbol_df=symbol_df)
    return analysis_response

@stock_app.post("/v1/option/day/", response_model=None)
async def get_symbol_analysis_for_next_day(req: StockDayAnalysisOptionRequest):
    # Create a ticker object
    ticker = yf.Ticker(req.symbol)

    # Fetch the options chain for nearest expiry date
    options_chain = ticker.option_chain()

    # The options_chain variable is a named tuple with 'calls' and 'puts' DataFrames
    calls = options_chain.calls
    puts = options_chain.puts

    print("Calls:\n", calls)
    print("\nPuts:\n", puts)

    return None
