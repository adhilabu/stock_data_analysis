from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.metrics import precision_score
from src.stock.schemas import FilterData, StockAnalysis

async def analyse_and_predict_symbol_data(filter_data: FilterData, symbol_df: pd.DataFrame) -> StockAnalysis:

    model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)

    offset = filter_data.offset
    train = symbol_df.iloc[:-offset]
    test = symbol_df.iloc[-offset:]

    predictors = ["Close", "Volume", "Open", "High", "Low"]
    model.fit(train[predictors], train["Target"])

    preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index)
    
    stock_analysis = StockAnalysis
    stock_analysis.prediction_score = round(precision_score(test["Target"], preds), 3)
    
    return stock_analysis


# async def predict(train, test, predictors, model):
#     model.fit(train[predictors], train["Target"])
#     preds = model.predict(test[predictors])
#     preds = pd.Series(preds, index=test.index, name="Predictions")
#     combined = pd.concat([test["Target"], preds], axis=1)
#     return combined


# async def backtest(data, model, predictors, start=2500, step=250):
#     all_predictions = []

#     for i in range(start, data.shape[0], step):
#         train = data.iloc[0:i].copy()
#         test = data.iloc[i:(i+step)].copy()
#         predictions = predict(train, test, predictors, model)
#         all_predictions.append(predictions)
    
#     return pd.concat(all_predictions)

# def predict_v2(train, test, predictors, model):
#     model.fit(train[predictors], train["Target"])
#     preds = model.predict_proba(test[predictors])[:,1]
#     preds[preds >=.6] = 1
#     preds[preds <.6] = 0
#     preds = pd.Series(preds, index=test.index, name="Predictions")
#     combined = pd.concat([test["Target"], preds], axis=1)
#     return combined
