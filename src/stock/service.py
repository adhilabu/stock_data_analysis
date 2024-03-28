import pandas as pd
from src.stock.schemas import StockDayAnalysisRequest, StockDayAnalysisResponse

async def analyze_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> StockDayAnalysisResponse:
    symbol_df.index = pd.to_datetime(symbol_df.index)
    response = StockDayAnalysisResponse
    response.symbol = req.symbol
    response.analysis_date = req.analysis_date
    return response