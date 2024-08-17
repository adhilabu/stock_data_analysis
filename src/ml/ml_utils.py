import pandas as pd

from src.schemas.constants import SymbolActions

async def get_stock_movt_prediction_from_analysis_data(
    analysis_data: int,
) -> SymbolActions:
    """
    method to fetch action based on the analysis data
    """
    match(analysis_data):
        case 0:
            symbol_action = SymbolActions.SELL
        case 1:
            symbol_action = SymbolActions.BUY
        case _:
            symbol_action = SymbolActions.NEUTRAL
    
    return symbol_action