# Stock Analysis Project

This project leverages machine learning techniques to analyze and predict stock movements based on historical data. It includes functionalities for data analysis, predictive modeling, and backtesting to evaluate the effectiveness of the predictive models.

## Features
- Analysis and Prediction: The project provides methods to analyze stock data and predict stock movements using machine learning models, specifically the Random Forest Classifier.
- Backtesting: It includes backtesting capabilities to assess the performance of the predictive models over historical data, allowing for iterative improvements.
- Prediction Types: The project supports different prediction types, enabling comparison and evaluation of various prediction strategies.
- Asynchronous Processing: Certain tasks in the project are designed to run asynchronously, enhancing performance and scalability.

## Technology Stack
- Python: The project is developed using Python, leveraging libraries such as scikit-learn for machine learning tasks and Pandas for data manipulation.
- Machine Learning: Machine learning techniques, particularly classification using the Random Forest algorithm, are utilized for stock movement prediction.
- Asynchronous Programming: Asynchronous programming paradigms are employed for efficient task handling and scalability.

## Endpoint

The project exposes an endpoint for performing stock analysis.

`{{hostname}}/analyse/symbol/day/`

## Request

```json
{
  "Symbol": "string",
  "AnalysisDate": "2024-04-03",
  "FilterData": {
    "StartDate": "2024-04-03",
    "Offset": 100
  }
}
```

- Symbol: The stock symbol for which analysis is to be performed.
- AnalysisDate: The date on which the analysis is requested.
- FilterData: Additional data for filtering the stock data.
  - StartDate: The start date for the analysis period.
  - Offset: The offset value for the analysis.

## Response
The endpoint returns a JSON response with the following structure:

```json
{
  "Symbol": "string",
  "AnalysisDate": "2024-04-03",
  "StockAnalysis": {
    "NormalPrecisionScore": 0,
    "BtPrecisionScoreV1": 0,
    "BtPrecisionScoreV2": 0,
    "NormalSymbolAction": "neutral",
    "BtV1SymbolAction": "neutral",
    "BtV2SymbolAction": "neutral"
  }
}
```

- Symbol: The stock symbol for which the analysis was performed.
- AnalysisDate: The date on which the analysis was performed. The AnalysisDate should be set to the maximum date up to the next day.
  - StockAnalysis: Analysis results with the following metrics:
  - NormalPrecisionScore: Precision score for normal analysis.
  - BtPrecisionScoreV1: Precision score for analysis version 1.
  - BtPrecisionScoreV2: Precision score for analysis version 2.
  - NormalSymbolAction: Action recommendation based on normal analysis (e.g., "buy", "sell", "neutral").
  - BtV1SymbolAction: Action recommendation based on analysis version 1 (e.g., "buy", "sell", "neutral").
  - BtV2SymbolAction: Action recommendation based on analysis version 2 (e.g., "buy", "sell", "neutral").

## Installation

- To install the required dependencies for this project, run the following command:

```console
pip install -r requirements.txt
```

## Resources

- Special thanks to the tutorials and resources that contributed to the development of this project!
- Special thanks to dataquest tutorials on stock market data anaylsis.

`https://www.youtube.com/@Dataquestio`
