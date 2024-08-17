import yfinance as yf
import pandas as pd
import numpy as np

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

def find_support_resistance(symbols):
    results = {}

    for symbol in symbols:
        # Fetch historical data
        data = yf.download(symbol, period='5y', interval='1d')
        
        if data.empty:
            continue

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

            # Determine if stock has reversed from support or resistance
            if low <= current_support <= close:
                support_levels.append(round_to_nearest(current_support, decimal_places))
            if high >= current_resistance >= close:
                resistance_levels.append(round_to_nearest(current_resistance, decimal_places))

        # Count occurrences and determine ranges
        support_counts = pd.Series(support_levels).value_counts()
        print(symbol, len(support_counts))
        resistance_counts = pd.Series(resistance_levels).value_counts()
        print(symbol, len(resistance_counts))

        # Filter support and resistance ranges that occur more than twice
        support_ranges = []
        for support, count in support_counts.items():
            if count > 2:
                support_ranges.append({
                    "low": round_to_nearest(support - 5, decimal_places),
                    "high": round_to_nearest(support + 5, decimal_places),
                    "count": count
                })

        resistance_ranges = []
        for resistance, count in resistance_counts.items():
            if count > 2:
                resistance_ranges.append({
                    "low": round_to_nearest(resistance - 5, decimal_places),
                    "high": round_to_nearest(resistance + 5, decimal_places),
                    "count": count
                })

        # Determine if the previous day's closing value is at support or resistance
        prev_close = data['Close'].iloc[-2]
        is_support = any(range['low'] <= prev_close <= range['high'] for range in support_ranges)
        is_resistance = any(range['low'] <= prev_close <= range['high'] for range in resistance_ranges)

        # Store results
        results[symbol] = {
            "support": sorted(support_ranges, key=lambda x: x['count'], reverse=True),
            "resistance": sorted(resistance_ranges, key=lambda x: x['count'], reverse=True),
            "is_support": is_support,
            "is_resistance": is_resistance
        }

    return results

# Example usage
symbols = ['TATAMOTORS.NS', 'RELIANCE.NS', 'INFY.NS']
support_resistance = find_support_resistance(symbols)
print(support_resistance)
