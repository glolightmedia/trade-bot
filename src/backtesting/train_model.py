import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report
import joblib

def load_and_preprocess_data(file_path):
    """
    Load and preprocess historical data for training.
    :param file_path: Path to the historical data CSV file.
    :return: Preprocessed DataFrame.
    """
    from src.backtesting.prepare_date_range import preprocess_data, load_historical_data

    raw_data = load_historical_data(file_path)
    data = preprocess_data(raw_data)
    data["Target"] = (data["close"].shift(-1) > data["close"]).astype(int)  # 1 = Buy, 0 = Hold/Sell
    return data.dropna()


def train_model(data, output_path="models/trading_model.pkl"):
    """
    Train a machine learning model to predict trading signals.
    :param data: Preprocessed DataFrame with features and target.
    :param output_path: Path to save the trained model.
    :return: Trained model and performance metrics.
    """
    features = data[["SMA_20", "RSI", "Normalized_Close"]]
    target = data["Target"]

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate performance
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="binary")
    recall = recall_score(y_test, y_pred, average="binary")

    print("Model Performance:")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save the model
    joblib.dump(model, output_path)
    print(f"Model saved to {output_path}")

    return model, {"Accuracy": accuracy, "Precision": precision, "Recall": recall}


def recommend_strategy_changes(model, backtest_data, strategy_function):
    """
    Compare model predictions with a strategy and recommend changes.
    :param model: Trained machine learning model.
    :param backtest_data: Historical data for backtesting.
    :param strategy_function: Existing strategy function.
    :return: Recommendations for strategy improvements.
    """
    backtest_data["Model_Signal"] = model.predict(backtest_data[["SMA_20", "RSI", "Normalized_Close"]])
    backtest_data["Strategy_Signal"] = backtest_data.apply(strategy_function, axis=1)

    model_pnl = calculate_pnl(backtest_data, "Model_Signal")
    strategy_pnl = calculate_pnl(backtest_data, "Strategy_Signal")

    print("\nPerformance Comparison:")
    print(f"ML Model PnL: {model_pnl}")
    print(f"Strategy PnL: {strategy_pnl}")

    if model_pnl > strategy_pnl:
        print("Recommendation: Consider using ML model predictions.")
    else:
        print("Recommendation: Stick with the current strategy.")

    return {
        "Model_PnL": model_pnl,
        "Strategy_PnL": strategy_pnl,
        "Recommendation": "ML Model" if model_pnl > strategy_pnl else "Strategy",
    }


def calculate_pnl(data, signal_column):
    """
    Calculate profit and loss (PnL) based on trading signals.
    :param data: DataFrame with market data and signals.
    :param signal_column: Column name with trading signals.
    :return: Total PnL.
    """
    data["Position"] = data[signal_column].shift(1).fillna(0)
    data["PnL"] = data["Position"] * (data["close"].diff().fillna(0))
    return data["PnL"].sum()


if __name__ == "__main__":
    # Load historical data
    file_path = "data/historical/sample_data.csv"
    data = load_and_preprocess_data(file_path)

    # Train the model
    model, metrics = train_model(data)

    # Define an example strategy (e.g., mean reversion)
    def mean_reversion_strategy(row):
        if row["RSI"] < 30:
            return 1  # Buy signal
        elif row["RSI"] > 70:
            return -1  # Sell signal
        else:
            return 0  # Hold signal

    # Recommend strategy changes based on backtesting
    recommendations = recommend_strategy_changes(model, data, mean_reversion_strategy)
    print("Recommendations:", recommendations)
