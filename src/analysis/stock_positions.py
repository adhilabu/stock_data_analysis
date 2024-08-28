import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from src.service.service import get_ticks
from src.service.service import get_ticks
from src.config.config import TEMP_FOLDER
from src.schemas.schemas import FindSupportResistanceResponse, GetLevelsRequest, StockLevelsContext, SupportResistanceResult, YFPeriod, YFInterval

def round_to_nearest(value, decimal_places):
    if decimal_places == 0:
        return round(value, -1)  # Round to nearest 10
    elif decimal_places == 1:
        return round(value, 0)   # Round to nearest whole number
    elif decimal_places == 2:
        return round(value, 1)   # Round to nearest tenth
    elif decimal_places == 3:
        return round(value, 2)   # Round to nearest hundredth
    else:
        return round(value, decimal_places)  # Keep original precision for higher decimals

def find_support_resistance(request: GetLevelsRequest):
    results = {}
    temp_folder = TEMP_FOLDER
    symbols = request.symbols

    if len(symbols) == 1 and symbols[0] == 'all':
        symbols_data = get_ticks()
        symbols = [s['value'] for s in symbols_data.symbols_map]

    period = request.period.value
    interval = request.interval.value
    date = datetime.now().strftime('%d-%m-%Y').replace('-', '_')

    if not os.path.isdir(temp_folder):
        os.mkdir(temp_folder)

    for index, symbol in enumerate(symbols):
        print(f"Started analysing stock {symbol} and count {index + 1}")
        temp_file = os.path.join(temp_folder, f"{symbol}_{period}_{interval}_{date}.csv")

        if os.path.isfile(temp_file):
            data = pd.read_csv(temp_file, index_col=0, parse_dates=True)
        else:
            data = yf.download(symbol, period=period, interval=interval)
            if not data.empty:
                data.to_csv(temp_file)

        if data.empty or len(data) < 2 or data.iloc[-1]['Close'] < 50:
            continue  # Skip this symbol

        # Calculate support and resistance levels
        data['Support'] = data['Low'].rolling(window=20).min()
        data['Resistance'] = data['High'].rolling(window=20).max()

        # Determine decimal places based on the stock's closing prices
        decimal_places = max(data['Close'].apply(lambda x: len(str(x).split('.')[1]) if '.' in str(x) else 0))

        support_levels = []
        resistance_levels = []

        for i in range(20, len(data)):
            current_support = data['Support'].iloc[i]
            current_resistance = data['Resistance'].iloc[i]
            low = data['Low'].iloc[i]
            high = data['High'].iloc[i]
            close = data['Close'].iloc[i]

            if low <= current_support <= close:
                support_levels.append({
                    "low": round_to_nearest(current_support, decimal_places),
                    "high": round_to_nearest(high, decimal_places)
                })
            if high >= current_resistance >= close:
                resistance_levels.append({
                    "low": round_to_nearest(low, decimal_places),
                    "high": round_to_nearest(current_resistance, decimal_places)
                })

        def create_ranges(levels):
            def get_range_diff(value):
                if value < 50:
                    return 2
                elif value < 100:
                    return 5
                elif value < 1000:
                    return 20
                elif value < 10000:
                    return 50
                else:
                    return 100

            ranges = []
            for level in levels:
                diff = get_range_diff(level)
                ranges.append((round_to_nearest(level - diff, decimal_places), round_to_nearest(level + diff, decimal_places)))
            return ranges

        support_ranges = create_ranges([level['low'] for level in support_levels])
        resistance_ranges = create_ranges([level['high'] for level in resistance_levels])

        def count_ranges(ranges):
            range_counts = {}
            for low, high in ranges:
                key = (low, high)
                range_counts[key] = range_counts.get(key, 0) + 1
            return range_counts

        support_range_counts = count_ranges(support_ranges)
        resistance_range_counts = count_ranges(resistance_ranges)

        filtered_support_ranges = [r for r, count in support_range_counts.items() if count >= request.accuracy]
        filtered_resistance_ranges = [r for r, count in resistance_range_counts.items() if count >= request.accuracy]

        try:
            prev_close = data['Close'].iloc[-2]
        except IndexError:
            continue  # Skip this symbol if there's not enough data to get the previous close price

        # Find specific support and resistance levels
        support_level_details = next(((low, high) for (low, high) in filtered_support_ranges if low <= prev_close <= high), [])
        resistance_level_details = next(((low, high) for (low, high) in filtered_resistance_ranges if low <= prev_close <= high), [])
        
        at_support = bool(support_level_details)
        at_resistance = bool(resistance_level_details)
        
        if at_support or at_resistance:
            if at_support:
                print(f"{symbol} is at support")
            if at_resistance :
                print(f"{symbol} is at resistance")

            results[symbol] = SupportResistanceResult(
                support_count=sum(1 for low, high in filtered_support_ranges if low <= prev_close <= high),
                resistance_count=sum(1 for low, high in filtered_resistance_ranges if low <= prev_close <= high),
                is_support=bool(support_level_details),
                is_resistance=bool(resistance_level_details),
                support_low=round(support_level_details[0], 2) if support_level_details else 0,
                support_high=round(support_level_details[1], 2) if support_level_details else 0,
                resistance_low=round(resistance_level_details[0], 2) if resistance_level_details else 0,
                resistance_high=round(resistance_level_details[1], 2) if resistance_level_details else 0
            )

    return FindSupportResistanceResponse(results=results)


def get_stock_levels_context_details() -> StockLevelsContext:
    intervals = {"Day": YFInterval.ONE_DAY, "Month": YFInterval.ONE_MONTH}
    periods = {"One Year": YFPeriod.ONE_YEAR, "Two Years": YFPeriod.TWO_YEARS}
    symbols_data = get_ticks()
    return StockLevelsContext(
        intervals=intervals,
        periods=periods,
        symbols=symbols_data.symbols_map
    )