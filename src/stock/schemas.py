from datetime import date
from src.schemas import CamelModel
from src.stock.constants import symbolActions

class StockDayAnalysisRequest(CamelModel):
    symbol: str
    analysis_date: date|None
    start_date: date|None
    end_date: date|None

class StockDayAnalysisResponse(CamelModel):
    symbol: str
    analysis_date: date|None
    symbol_action: symbolActions = symbolActions.NEUTRAL