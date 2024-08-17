
from enum import Enum

class SymbolActions(str, Enum):
    SELL = 'sell'
    NEUTRAL = 'neutral'
    BUY = 'buy'

class PredictionType(str, Enum):
    V1 = 'v1'
    V2 = 'v2'