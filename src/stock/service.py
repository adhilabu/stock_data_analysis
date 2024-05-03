import pandas as pd
from src.stock.schemas import AllSymbolsResponse, StockDayAnalysisRequest, StockDayAnalysisResponse, FilterData
from src.stock.ml_service import analyse_and_predict_symbol_data
import os
import requests

async def filter_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> pd.DataFrame:
    """
    method to filter symbol dataframe based on the filter data
    """
    analysis_date = req.analysis_date
    analysis_date = analysis_date.strftime('%Y-%m-%d')
    symbol_df = symbol_df[(symbol_df.index < analysis_date)]

    start_date = req.filter_data.start_date if req.filter_data else None
    if start_date:
        start_date = start_date.strftime('%Y-%m-%d')
        symbol_df = symbol_df[(symbol_df.index >= start_date)]

    # Add a new row with the index as analysis_date and set all other values to null
    analysis_date_obj = pd.to_datetime(analysis_date).tz_localize('Asia/Kolkata')
    new_row = pd.DataFrame(index=[analysis_date_obj], columns=symbol_df.columns)
    new_row['Open'] = symbol_df.iloc[-1]['Close']
    new_row = new_row.infer_objects(copy=False)  # Inference to downcast object types
    symbol_df = pd.concat([symbol_df, new_row])

    return symbol_df

async def analyze_symbol_df(req: StockDayAnalysisRequest, symbol_df: pd.DataFrame) -> StockDayAnalysisResponse:
    """
    method to filter symbol dataframe and create stock analysis response
    """
    symbol_df.index = pd.to_datetime(symbol_df.index)
    del symbol_df["Dividends"]
    del symbol_df["Stock Splits"]
    
    filter_data = req.filter_data
    symbol_df = await filter_symbol_df(req, symbol_df)

    symbol_df["Tomorrow"] = symbol_df["Close"].shift(-1)
    symbol_df["Target"] = (symbol_df["Tomorrow"] > symbol_df["Close"]).astype(int)
    
    response = StockDayAnalysisResponse
    response.symbol = req.symbol
    response.analysis_date = req.analysis_date
    response.stock_analysis = await analyse_and_predict_symbol_data(filter_data, symbol_df)
    return response

def get_ticks(
) -> AllSymbolsResponse:
    """
    Function for fetching tick data
    """
    if not os.path.isdir("yf_data"):
        os.mkdir("yf_data")

    symbols_file = r"nse_equities.csv"
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    # Downloads scripts csv if it's not there you can delete the nse_equities.csv
    # file after new IPOs to update the file
    if not os.path.isfile(symbols_file):
        response = requests.get(url)
        with open(symbols_file, "wb") as f:
            f.write(response.content)
    equities = pd.read_csv(symbols_file)
    equities["SYMBOL_NS"] = equities["SYMBOL"].apply(lambda x: x + ".NS")
    symbols_map = dict(zip(equities['SYMBOL_NS'], equities['NAME OF COMPANY']))


    # YF adds a .NS suffix to NSE scripts
    extras = {
        # indices
        '^NSEI': 'Nifty 50',
        '^NSEBANK': 'Nifty Bank',
        '^NSMIDCP': 'Nifty Midcap 50',
        '^NSEMDCP50': 'Nifty Midcap 150',
        'NIFTYSMLCAP50.NS': 'Nifty Smallcap 50',
        # sector
        '^CNXIT': 'CNX IT',
        '^CNXAUTO': 'CNX Auto',
        '^CNXFIN': 'CNX Finance',
        '^CNXPHARMA': 'CNX Pharma',
        '^CNXFMCG': 'CNX FMCG',
        '^CNXMETAL': 'CNX Metal',
        '^CNXREALTY': 'CNX Realty',
        '^CNXENERGY': 'CNX Energy',
        '^CNXINFRA': 'CNX Infra',
        # etfs
        'GOLDBEES.NS': 'Gold ETF',
        'MINDSPACE-RR.NS': 'Mindspace Business Parks REIT',
        'N100.NS': 'Nifty 100',
        'NIFTYBEES.NS': 'Nifty ETF',
        'BANKBEES.NS': 'Bank ETF'
    }
    
    symbols_map.update(extras)
    all_symbols_response = AllSymbolsResponse(
        symbols_map=symbols_map
    )
    return all_symbols_response