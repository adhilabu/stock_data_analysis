from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.metrics import precision_score
from src.stock.schemas import FilterData, StockAnalysis
from src.stock.utils import get_rounded_value, get_start_and_step_from_df
from src.stock.constants import PredictionType

async def analyse_and_predict_symbol_data(
        filter_data: FilterData,
        symbol_df: pd.DataFrame
    ) -> StockAnalysis:

    model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)

    offset = filter_data.offset
    train = symbol_df.iloc[:-offset]
    test = symbol_df.iloc[-offset:]

    predictors = ["Close", "Volume", "Open", "High", "Low"]
    model.fit(train[predictors], train["Target"])

    preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index)
    
    stock_analysis = StockAnalysis
    stock_analysis.precision_score = get_rounded_value(precision_score(test["Target"], preds))

    start, step = get_start_and_step_from_df(symbol_df)

    predictions: pd.DataFrame = await backtest(symbol_df, model, predictors, start, step)
    stock_analysis.bt_precision_score = get_rounded_value(precision_score(predictions["Target"], predictions["Predictions"]))

    return stock_analysis


async def get_predict_v2(filter_data: FilterData, symbol_df: pd.DataFrame):
    horizons = [2,5,60,250,1000]
    new_predictors = []

    for horizon in horizons:
        rolling_averages = symbol_df.rolling(horizon).mean()
        
        ratio_column = f"Close_Ratio_{horizon}"
        symbol_df[ratio_column] = symbol_df["Close"] / rolling_averages["Close"]
        
        trend_column = f"Trend_{horizon}"
        symbol_df[trend_column] = symbol_df.shift(1).rolling(horizon).sum()["Target"]
        
        new_predictors+= [ratio_column, trend_column]
    
    symbol_df = symbol_df.dropna(subset=symbol_df.columns[symbol_df.columns != "Tomorrow"])



async def predict(train: pd.DataFrame, test: pd.DataFrame, predictors: list, model: RandomForestClassifier) -> pd.DataFrame:
    model.fit(train[predictors], train["Target"])
    preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], preds], axis=1)
    return combined


async def backtest(
        data: pd.DataFrame,
        model: RandomForestClassifier,
        predictors: list,
        p: PredictionType = PredictionType.V1,
        start: int = 100,
        step: int = 10
    ) -> pd.DataFrame:

    all_predictions = []

    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        test = data.iloc[i:(i+step)].copy()
        
        match p:
            case PredictionType.V1:
                predictions = await predict(train, test, predictors, model)
            case PredictionType.V2:
                predictions = await predict_v2(train, test, predictors, model)
        all_predictions.append(predictions)
        print(f'Back tested {i} to {i+step} rows of {data.shape[0]}')

    return pd.concat(all_predictions)

async def predict_v2(train, test, predictors, model):
    model.fit(train[predictors], train["Target"])
    preds = model.predict_proba(test[predictors])[:,1]
    preds[preds >=.6] = 1
    preds[preds <.6] = 0
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], preds], axis=1)
    return combined
