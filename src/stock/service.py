import pandas as pd
from src.stock.schemas import StockDayAnalysisRequest, StockDayAnalysisResponse, FilterData
from src.stock.ml_service import analyse_and_predict_symbol_data

async def filter_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> pd.DataFrame:
    """
    method to filter symbol dataframe based on the filter data
    """
    analysis_date = req.analysis_date
    analysis_date = analysis_date.strftime('%Y-%m-%d')
    symbol_df = symbol_df[(symbol_df.index < analysis_date)]

    start_date = req.filter_data.start_date if req.filter_data else None
    if start_date:
        start_date = start_date.strftime('%Y-%m-%d')
        symbol_df = symbol_df[(symbol_df.index >= start_date)]

    # Add a new row with the index as analysis_date and set all other values to null
    analysis_date_obj = pd.to_datetime(analysis_date).tz_localize('Asia/Kolkata')
    new_row = pd.DataFrame(index=[analysis_date_obj], columns=symbol_df.columns)
    new_row['Open'] = symbol_df.iloc[-1]['Close']
    new_row = new_row.infer_objects(copy=False)  # Inference to downcast object types
    symbol_df = pd.concat([symbol_df, new_row])

    return symbol_df

async def analyze_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> StockDayAnalysisResponse:
    """
    method to filter symbol dataframe and create stock analysis response
    """
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