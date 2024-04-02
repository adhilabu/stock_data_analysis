
from enum import Enum

VALUE_AREA_DATE_RANGE = 30

class SymbolActions(Enum):
    SELL = 'sell' # 0.0 - 0.3
    NEUTRAL = 'neutral' # 0.3 - 0.7
    BUY = 'buy' # 0.7 - 1

class PredictionType(Enum):
    V1 = 'v1'
    V2 = 'v2'