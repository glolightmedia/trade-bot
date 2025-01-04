import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report
from src.backtesting.prepare_date_range import preprocess_data


def load_and_preprocess_data(file_path):
    """
    Load and preprocess historical data for training.
    :param file_path: Path to the historical data CSV file.
    :return: Preprocessed DataFrame.
    """
    raw_data = pd.read_csv(file_path, parse_dates=["timestamp"])
    data = preprocess_data(raw_data)
    data["Target"] = (data["close"].shift(-1) > data["close"]).astype(int)  # Binary classification target
    return data.dropna()


def train_random_forest(data, output_path="models/pre_trained/random_forest.pkl"):
    """
    Train a Random Forest model to predict trading signals.
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


if __name__ == "__main__":
    # Load and preprocess data
    file_path = "data/historical/sample_data.csv"
    data = load_and_preprocess_data(file_path)

    # Train Random Forest model
    model, metrics = train_random_forest(data)
    print("Trained model and saved successfully.")
