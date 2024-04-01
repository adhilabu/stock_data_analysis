import pandas as pd
from src.stock.schemas import StockDayAnalysisRequest, StockDayAnalysisResponse, FilterData
from src.stock.ml_service import analyse_and_predict_symbol_data
from datetime import datetime, timedelta, date


async def filter_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> pd.DataFrame:
    
    analysis_date = req.analysis_date
    analysis_date: date = analysis_date - timedelta(days=1)
    analysis_date = analysis_date.strftime('%Y-%m-%d')
    symbol_df = symbol_df[(symbol_df.index < analysis_date)]

    start_date = req.filter_data.start_date if req.filter_data else None
    if start_date:
        start_date = start_date.strftime('%Y-%m-%d')
        symbol_df = symbol_df[(symbol_df.index >= start_date)]
    
    return symbol_df

async def analyze_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> StockDayAnalysisResponse:
    symbol_df.index = pd.to_datetime(symbol_df.index)
    del symbol_df["Dividends"]
    del symbol_df["Stock Splits"]
    
    filter_data = req.filter_data
    symbol_df = await filter_symbol_df(req, symbol_df)

    symbol_df["Tomorrow"] = symbol_df["Close"].shift(-1)
    symbol_df["Target"] = (symbol_df["Tomorrow"] > symbol_df["Close"]).astype(int)
    
    response = StockDayAnalysisResponse
    response.symbol = req.symbol
    response.analysis_date = req.analysis_date
    response.stock_analysis = await analyse_and_predict_symbol_data(filter_data, symbol_df)
    return response