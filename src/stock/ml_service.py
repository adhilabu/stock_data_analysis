from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.metrics import precision_score
from src.stock.schemas import FilterData, StockAnalysis
from src.stock.utils import get_rounded_value, get_start_and_step_from_df
from src.stock.constants import PredictionType

async def analyse_and_predict_symbol_data(
        analysis_date: str,
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
    stock_analysis.normal_precision_score = get_rounded_value(precision_score(test["Target"], preds))
    start, step = get_start_and_step_from_df(symbol_df)

    bt_predictions_v1: pd.DataFrame = await backtest(data=symbol_df, predictors=predictors, p=PredictionType.V1, start=start, step=step)
    stock_analysis.bt_precision_score_v1 = get_rounded_value(precision_score(bt_predictions_v1["Target"], bt_predictions_v1["Predictions"]))
    

    bt_predictions_v2: pd.DataFrame = await backtest(data=symbol_df, predictors=predictors, p=PredictionType.V2, start=start, step=step)
    stock_analysis.bt_precision_score_v2 = get_rounded_value(precision_score(bt_predictions_v2["Target"], bt_predictions_v2["Predictions"]))

    return stock_analysis

async def predict(train: pd.DataFrame, test: pd.DataFrame, predictors: list, model: RandomForestClassifier) -> pd.DataFrame:
    model.fit(train[predictors], train["Target"])
    preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], preds], axis=1)
    return combined

async def get_model_and_set_for_v2(
        data: pd.DataFrame
    ) -> tuple[pd.DataFrame, list]:
    horizons = [2,5,60,250,1000]
    new_predictors = []

    for horizon in horizons:
        rolling_averages = data.rolling(horizon).mean()
        
        ratio_column = f"Close_Ratio_{horizon}"
        data[ratio_column] = data["Close"] / rolling_averages["Close"]
        
        trend_column = f"Trend_{horizon}"
        data[trend_column] = data.shift(1).rolling(horizon).sum()["Target"]
        
        new_predictors+= [ratio_column, trend_column]
    
    data = data.dropna(subset=data.columns[data.columns != "Tomorrow"])

    return data, new_predictors


async def predict_v2(
        train: pd.DataFrame,
        test: pd.DataFrame,
        predictors: list,
        model: RandomForestClassifier,
    ) -> pd.DataFrame:
    model.fit(train[predictors], train["Target"])
    preds = model.predict_proba(test[predictors])[:,1]
    preds[preds >=.6] = 1
    preds[preds <.6] = 0
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], preds], axis=1)
    return combined

async def backtest(
        data: pd.DataFrame,
        predictors: list,
        p: PredictionType = PredictionType.V1,
        start: int = 100,
        step: int = 10
    ) -> pd.DataFrame:

    if p == PredictionType.V2:
        data, predictors = await get_model_and_set_for_v2(data=data)
        
    all_predictions = []
    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        test = data.iloc[i:(i+step)].copy()

        match p:
            case PredictionType.V1:
                model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
                predictions = await predict(train, test, predictors, model)
            case PredictionType.V2:
                model = RandomForestClassifier(n_estimators=200, min_samples_split=50, random_state=1)
                predictions = await predict_v2(train, test, predictors, model)
        all_predictions.append(predictions)
        print(f'Back tested {i} to {i+step} rows of {data.shape[0]} in {p.name}')

    return pd.concat(all_predictions)

