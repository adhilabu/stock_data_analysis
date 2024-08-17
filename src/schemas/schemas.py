from datetime import date
from src.schemas.constants import SymbolActions

from datetime import date, time as time_only
from pydantic import BaseModel, Field, validator

def convert_time_to_hh_mm_ss(dt: time_only) -> str:
    return dt.strftime('%H:%M:%S')

def convert_date_to_iso_format(dt: date) -> str:
    return dt.isoformat()

def to_camel(string: str):
    return string.title().replace("_", "")

class RootModel(BaseModel):
    pass

class CamelModel(RootModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {
            time_only: convert_time_to_hh_mm_ss,
            date: convert_date_to_iso_format
        }

class FilterData(CamelModel):
    start_date: date|None
    offset: int = 100

class StockDayAnalysisRequest(CamelModel):
    symbol: str
    analysis_date: date|None
    filter_data: FilterData|None

class StockAnalysis(CamelModel):
    normal_precision_score: float = 0.0
    bt_precision_score_v1: float = 0.0
    bt_precision_score_v2: float = 0.0
    normal_symbol_action: SymbolActions = SymbolActions.NEUTRAL
    bt_v1_symbol_action: SymbolActions = SymbolActions.NEUTRAL
    bt_v2_symbol_action: SymbolActions = SymbolActions.NEUTRAL
    
    class Config:  
        use_enum_values = True

class StockDayAnalysisResponse(CamelModel):
    symbol: str
    analysis_date: date|None
    stock_analysis: StockAnalysis

class AllSymbolsResponse(CamelModel):
    symbols_map: list = []

class StockDayAnalysisV3Response(CamelModel):
    symbol: str
    analysis_date: date|None
    accuracy: float

class StockDayAnalysisOptionRequest(CamelModel):
    symbol: str
