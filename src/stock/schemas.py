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

    # @classmethod
    # def get_response(cls):
    #     response = {
    #         'symbol': cls.symbol,
    #         'analysis_date': cls.analysis_date,
    #         'symbol_action': cls.symbol_action,
    #     }
    #     return response
