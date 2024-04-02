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
    normal_precision_score: float
    bt_precision_score_v1: float
    bt_precision_score_v2: float
    normal_symbol_action: SymbolActions = SymbolActions.NEUTRAL
    bt_v1_symbol_action: SymbolActions = SymbolActions.NEUTRAL
    bt_v2_symbol_action: SymbolActions = SymbolActions.NEUTRAL

class StockDayAnalysisResponse(CamelModel):
    symbol: str
    analysis_date: date|None
    stock_analysis: StockAnalysis