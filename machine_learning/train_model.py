import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler

class TrainModel:
    """
    Handles training of machine learning models for the trading bot.
    """

    def __init__(self):
        self.scaler = StandardScaler()

    def train_random_forest(self, data, target_column, output_path="models/random_forest.pkl"):
        """
        Train a Random Forest model.
        :param data: DataFrame containing features and target column.
        :param target_column: Name of the target column.
        :param output_path: Path to save the trained model.
        :return: Trained Random Forest model and performance metrics.
        """
        X = data.drop(columns=[target_column])
        y = data[target_column]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = self.evaluate_model(y_test, y_pred)
        print("Random Forest Metrics:", metrics)

        joblib.dump(model, output_path)
        print(f"Random Forest model saved to {output_path}")
        return model, metrics

    def train_lstm(self, data, target_column, sequence_length=30, output_path="models/lstm_model.h5"):
        """
        Train an LSTM model.
        :param data: DataFrame containing features and target column.
        :param target_column: Name of the target column.
        :param sequence_length: Length of input sequences.
        :param output_path: Path to save the trained model.
        :return: Trained LSTM model and performance metrics.
        """
        data = self.prepare_lstm_data(data, target_column, sequence_length)

        X_train, X_test, y_train, y_test = train_test_split(data["X"], data["y"], test_size=0.2, random_state=42)

        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1, activation="sigmoid"),
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss="binary_crossentropy", metrics=["accuracy"])

        model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

        y_pred = model.predict(X_test).flatten()
        y_pred = (y_pred > 0.5).astype(int)
        metrics = self.evaluate_model(y_test, y_pred)
        print("LSTM Metrics:", metrics)

        model.save(output_path)
        print(f"LSTM model saved to {output_path}")
        return model, metrics

    def prepare_lstm_data(self, data, target_column, sequence_length):
        """
        Prepare data for LSTM training.
        :param data: DataFrame containing features and target column.
        :param target_column: Name of the target column.
        :param sequence_length: Length of input sequences.
        :return: Dictionary with X (features) and y (target).
        """
        data = self.scaler.fit_transform(data)
        X, y = [], []

        for i in range(sequence_length, len(data)):
            X.append(data[i-sequence_length:i, :-1])
            y.append(data[i, -1])

        return {"X": np.array(X), "y": np.array(y)}

    @staticmethod
    def evaluate_model(y_true, y_pred):
        """
        Evaluate model performance.
        :param y_true: True labels.
        :param y_pred: Predicted labels.
        :return: Dictionary of performance metrics.
        """
        return {
            "Accuracy": accuracy_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred),
            "Recall": recall_score(y_true, y_pred),
            "Classification Report": classification_report(y_true, y_pred, output_dict=True),
        }


if __name__ == "__main__":
    # Example usage
    # Sample data for training
    data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        "target": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    })

    trainer = TrainModel()

    # Train Random Forest
    rf_model, rf_metrics = trainer.train_random_forest(data, "target")

    # Train LSTM
    lstm_model, lstm_metrics = trainer.train_lstm(data, "target")
