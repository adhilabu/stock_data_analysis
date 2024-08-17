import os
import requests
from taipy.gui import Gui, Page, notify
import taipy.gui.builder as tgb

from datetime import date
import yfinance as yf
from prophet import Prophet
import pandas as pd
from plotly import graph_objects as go

def get_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    ticker_data = yf.download(ticker, start, end)  # downloading the stock data from START to TODAY
    ticker_data.reset_index(inplace=True)  # put date in the first column
    ticker_data['Date'] = pd.to_datetime(ticker_data['Date']).dt.tz_localize(None)
    return ticker_data

def create_candlestick_chart(data: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data['Date'],
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Candlestick'))
    fig.update_layout(margin=dict(l=30, r=30, b=30, t=30), xaxis_rangeslider_visible=False)
    return fig

def generate_forecast_data(data: pd.DataFrame, n_years: int) -> pd.DataFrame:
    # FORECASTING
    df_train = data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})  # This is the format that Prophet accepts

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=n_years * 365)
    fc = m.predict(future)[['ds', 'yhat_lower', 'yhat_upper']].rename(columns={"ds": "Date", "yhat_lower": "Lower", "yhat_upper": "Upper"})
    print("Process Completed!")
    return fc

def get_all_symbols() -> list:
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
    symbol_list = [key for key, value in symbols_map.items()]
    return symbol_list


class StockVisualization(Page):
    # --------- State Initialization  --------- #
    def __init__(self):
        self.start_date: str = "2015-01-01"
        self.end_date: str = date.today().strftime("%Y-%m-%d")
        self.selected_stock: str = 'AAPL'
        self.n_years: int = 1
        self.data: pd.DataFrame = get_stock_data(self.selected_stock, self.start_date, self.end_date)
        self.forecast: pd.DataFrame = generate_forecast_data(self.data, self.n_years)
        self.symbols = get_all_symbols()

        super().__init__()

    # --------- Callbacks --------- #
    def forecast_display(self):
        notify(self, 'i', 'Predicting...')
        self.forecast = generate_forecast_data(self.data, self.n_years)
        notify(self, 's', 'Prediction done! Forecast data has been updated!')

    def get_data_range(self):
        """Get data from the selected date range"""
        print("GENERATING HIST DATA")
        start_date = self.start_date if type(self.start_date)==str else self.start_date.strftime("%Y-%m-%d")
        end_date = self.end_date if type(self.end_date)==str else self.end_date.strftime("%Y-%m-%d")

        self.data = get_stock_data(self.selected_stock, start_date, end_date)
        if len(self.data) == 0:
            notify(self, "error", f"Not able to download data {self.selected_stock} from {start_date} to {end_date}")
            return
        notify(self, 's', 'Historical data has been updated!')
        notify(self, 'w', 'Deleting previous predictions...')
        self.forecast = pd.DataFrame(columns=['Date', 'Lower', 'Upper'])

    def on_filter(self, selected_symbols):
        """Handle the filtering and selection of symbols."""
        if not selected_symbols:
            notify(self, 'w', 'No symbol selected!')
            return
        
        self.selected_stock = selected_symbols[0]  # assuming single selection; modify for multiple selections if needed
        notify(self, 'i', f'Selected stock: {self.selected_stock}')
        
        self.get_data_range()  # Refresh the data based on the new selection

    # --------- Page Definition --------- #
    ## ------- Parts of Page ------- ##
    def input_part(self):
        with tgb.layout("1 2 1", gap="40px", class_name="card"):
            with tgb.part():
                tgb.text("#### Selected Period", mode="md")
                tgb.text("From:")
                tgb.date("{start_date}", on_change=self.get_data_range)
                tgb.text("To:")
                tgb.date("{end_date}", on_change=self.get_data_range)
            with tgb.part():
                # lov = ["MSFT", "GOOG", "AAPL", "AMZN", "META", "COIN", "AMC", "PYPL"]
                lov = ['^NSEI', '^NSEBANK', '^NSMIDCP', 'N100.NS', 'NIFTYBEES.NS']
                tgb.text("#### Selected Ticker", mode="md")
                tgb.selector(
                    "{selected_stock}",
                    lov=self.symbols,
                    multiple=False,
                    label="Select the Stock",
                    filter=True,
                    dropdown=True,
                    on_change=self.get_data_range,
                    class_name="fullwidth",
                )
                # tgb.input(value="{selected_stock}", label="Stock", on_action=self.get_data_range)

                tgb.text("or choose a popular one")
                tgb.toggle(value="{selected_stock}", lov=lov, on_change=self.get_data_range)
            with tgb.part():
                tgb.text("#### Prediction years", mode="md")
                tgb.text("Select number of prediction years: {n_years}")
                tgb.slider("{n_years}", min=1, max=5)

                tgb.button("Predict", on_action=self.forecast_display, class_name="{'plain' if len(forecast)==0 else ''}")
        
    def historical_data_part(self):
        with tgb.layout("1 1"):
            with tgb.part():
                tgb.text("### Historical Closing price", mode="md")
                tgb.chart("{data}", mode="line", x="Date", y__1="Open", y__2="Close")

            with tgb.part():
                tgb.text("### Historical Daily Trading Volume", mode="md")
                tgb.chart("{data}", mode="line", x="Date", y="Volume")

        tgb.text("### Whole Historical Data {selected_stock}", mode="md")
        tgb.table("{data}")

    def prediction_part(self):
        with tgb.layout("1 1", class_name="text-center"):
            tgb.text("Pessimistic Forecast {int((forecast.loc[len(forecast)-1, 'Lower'] - forecast.loc[len(data), 'Lower'])/forecast.loc[len(data), 'Lower']*100)}%", class_name="h4 card", )

            tgb.text("Optimistic Forecast {int((forecast.loc[len(forecast)-1, 'Upper'] - forecast.loc[len(data), 'Upper'])/forecast.loc[len(data), 'Upper']*100)}%", class_name="h4 card")

        tgb.chart("{forecast}", mode="line", x="Date", y__1="Lower", y__2="Upper")

    ## ------- Page Creation ------- ##
    def create_page(self):
        with tgb.Page() as page:
            tgb.toggle(theme=True)

            with tgb.part("container"):
                tgb.text("# Aksyo Stock Price Analysis Dashboard", mode="md")

                self.input_part()

                tgb.html("br")

                tgb.chart(figure="{create_candlestick_chart(data)}")

                with tgb.expandable(title="Historical Data", value="Historical Data", expanded=False):
                    self.historical_data_part()

                tgb.text("### Forecast Data", mode="md")

                self.prediction_part()
        return page

if __name__ == "__main__":
    Gui(page=StockVisualization()).run()