from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.metrics import precision_score
from src.stock.schemas import FilterData, StockAnalysis
from src.stock.utils import get_rounded_value, get_start_and_step_from_df
from src.stock.ml_utils import get_stock_movt_prediction_from_analysis_data
from src.stock.constants import PredictionType

async def analyse_and_predict_symbol_data(
    filter_data: FilterData,
    symbol_df: pd.DataFrame
) -> StockAnalysis:

    stock_analysis = StockAnalysis
    model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
    start, step = get_start_and_step_from_df(symbol_df)

    offset = filter_data.offset
    train = symbol_df.iloc[:-offset]
    test = symbol_df.iloc[-offset:]

    predictors = ["Close", "Volume", "Open", "High", "Low"]
    model.fit(train[predictors], train["Target"])

    preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index)

    stock_analysis.normal_precision_score = get_rounded_value(precision_score(test["Target"], preds))
    stock_analysis.normal_symbol_action = await get_stock_movt_prediction_from_analysis_data(preds.iloc[-1])

    bt_predictions_v1: pd.DataFrame = await backtest(data=symbol_df, predictors=predictors, p=PredictionType.V1, start=start, step=step)
    
    if bt_predictions_v1 is not None:
        stock_analysis.bt_precision_score_v1 = get_rounded_value(precision_score(bt_predictions_v1["Target"], bt_predictions_v1["Predictions"]))
        stock_analysis.bt_v1_symbol_action = await get_stock_movt_prediction_from_analysis_data(bt_predictions_v1.iloc[-1]['Predictions'])

    bt_predictions_v2: pd.DataFrame = await backtest(data=symbol_df, predictors=predictors, p=PredictionType.V2, start=start, step=step)
    if bt_predictions_v2 is not None:
        stock_analysis.bt_precision_score_v2 = get_rounded_value(precision_score(bt_predictions_v2["Target"], bt_predictions_v2["Predictions"]))
        stock_analysis.bt_v2_symbol_action = await get_stock_movt_prediction_from_analysis_data(bt_predictions_v2.iloc[-1]['Predictions'])

    return stock_analysis

async def predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    predictors: list,
    model: RandomForestClassifier
) -> pd.DataFrame:
    
    model.fit(train[predictors], train["Target"])
    preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], preds], axis=1)
    return combined

async def get_model_and_set_for_v2(
    data: pd.DataFrame
) -> tuple[pd.DataFrame, list]:

    max_horizon = data.shape[0]  # Limit max horizon to half the data length and 1000 (adjustable)
    horizons = [h for h in [2, 5, 60, 250, 1000] if 2 * h <= max_horizon]  # Select horizons less than or equal to half of max_horizon
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
) -> pd.DataFrame|None:

    if p == PredictionType.V2:
        data, predictors = await get_model_and_set_for_v2(data=data)
        model = RandomForestClassifier(n_estimators=200, min_samples_split=50, random_state=1)
    else:
        model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
    
    if data.shape[0] < start:
        return None
    
    all_predictions = []
    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        
        remaining_data = data.iloc[i:]
        if len(remaining_data) < step:
            test = remaining_data.copy()
            next_len = len(remaining_data)
        else:
            test = data.iloc[i:(i + step)].copy()
            next_len = step

        match p:
            case PredictionType.V1:
                predictions = await predict(train, test, predictors, model)
            case PredictionType.V2:
                predictions = await predict_v2(train, test, predictors, model)
        all_predictions.append(predictions)
        print(f'Back tested {i} to {i + next_len} rows of {data.shape[0]} in {p.name}')

    return pd.concat(all_predictions)

