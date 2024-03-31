import pandas as pd
from src.stock.schemas import StockDayAnalysisRequest, StockDayAnalysisResponse
from src.stock.ml_service import analyse_and_predict_symbol_data

async def analyze_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> StockDayAnalysisResponse:
    symbol_df.index = pd.to_datetime(symbol_df.index)
    del symbol_df["Dividends"]
    del symbol_df["Stock Splits"]
    
    if req.start_date:
        symbol_df = symbol_df[req.start_date:].copy()
    if req.end_date:
        symbol_df = symbol_df[:req.end_date].copy()

    symbol_df["Tomorrow"] = symbol_df["Close"].shift(-1)
    symbol_df["Target"] = (symbol_df["Tomorrow"] > symbol_df["Close"]).astype(int)

    response = await analyse_and_predict_symbol_data(req, symbol_df)
    return response