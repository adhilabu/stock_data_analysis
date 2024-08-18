from datetime import date
from enum import Enum
from typing import Dict, List, Optional
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

class YFPeriod(str, Enum):
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YEAR_TO_DATE = "ytd"
    MAX = "max"

    @classmethod
    def list_periods(cls):
        return [period.value for period in cls]

class YFInterval(str, Enum):
    """Enum for valid intervals in Yahoo Finance."""
    ONE_MINUTE = '1m'
    TWO_MINUTES = '2m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'
    THIRTY_MINUTES = '30m'
    SIXTY_MINUTES = '60m'
    NINETY_MINUTES = '90m'
    ONE_HOUR = '1h'
    ONE_DAY = '1d'
    FIVE_DAYS = '5d'
    ONE_WEEK = '1wk'
    ONE_MONTH = '1mo'
    THREE_MONTHS = '3mo'

class GetLevelsRequest(CamelModel):
    symbols: List[str]
    accuracy: int = 2
    period: YFPeriod = YFPeriod.ONE_YEAR
    interval: YFInterval = YFInterval.ONE_DAY

class SupportResistanceResult(CamelModel):
    support_count: int
    resistance_count: int
    is_support: bool
    is_resistance: bool
    support_low: float = 0
    support_high: float = 0
    resistance_low: float = 0
    resistance_high: float = 0

class FindSupportResistanceResponse(CamelModel):
    results: Dict[str, SupportResistanceResult]

class TokenResponse(CamelModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

class StockLevelsContext(CamelModel):
    symbols: list = []
    intervals: dict[str, str]
    periods: dict[str, str]