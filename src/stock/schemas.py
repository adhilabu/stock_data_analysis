from datetime import date
from src.schemas import CamelModel
from src.stock.constants import SymbolActions

class FilterData(CamelModel):
    start_date: date|None
    offset: int = 100

class StockDayAnalysisRequest(CamelModel):
    symbol: str
    analysis_date: date|None
    filter_data: FilterData|None

class StockAnalysis(CamelModel):
    prediction_score: float
    symbol_action: SymbolActions = SymbolActions.NEUTRAL

class StockDayAnalysisResponse(CamelModel):
    symbol: str
    analysis_date: date|None
    stock_analysis: StockAnalysis