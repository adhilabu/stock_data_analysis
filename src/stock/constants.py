
from enum import Enum

VALUE_AREA_DATE_RANGE = 30

class SymbolActions(Enum):
    BUY = 'buy'
    SELL = 'sell'
    NEUTRAL = 'neutral'

class PredictionType(Enum):
    V1 = 'v1'
    V2 = 'v2'