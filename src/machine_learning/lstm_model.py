import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class LSTMModel:
    """
    Implements an LSTM model for predicting future price movements using time-series data.
    """

    def __init__(self, sequence_length=30):
        """
        Initialize the LSTM model.
        :param sequence_length: Number of time steps for input sequences.
        """
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        self.model = None

    def prepare_data(self, data, target_column):
        """
        Prepare data for LSTM training.
        :param data: DataFrame containing features and target column.
        :param target_column: Name of the target column.
        :return: Scaled data and sequences for training/testing.
        """
        data_scaled = self.scaler.fit_transform(data)
        X, y = [], []

        for i in range(self.sequence_length, len(data_scaled)):
            X.append(data_scaled[i - self.sequence_length:i, :-1])
            y.append(data_scaled[i, -1])

        return np.array(X), np.array(y)

    def build_model(self, input_shape):
        """
        Build the LSTM model architecture.
        :param input_shape: Shape of the input data (timesteps, features).
        """
        self.model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1)
        ])
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")
        print("LSTM model built.")

    def train(self, data, target_column, epochs=10, batch_size=32, test_size=0.2):
        """
        Train the LSTM model.
        :param data: DataFrame containing features and target column.
        :param target_column: Name of the target column.
        :param epochs: Number of training epochs.
        :param batch_size: Batch size for training.
        :param test_size: Proportion of data to use for testing.
        :return: Training history and performance metrics.
        """
        X, y = self.prepare_data(data.values, target_column)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        history = self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test))

        y_pred = self.model.predict(X_test).flatten()
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error (MSE): {mse}")

        return history, {"MSE": mse}

    def predict(self, data):
        """
        Predict future values using the trained LSTM model.
        :param data: DataFrame or array containing input features.
        :return: Predicted values.
        """
        data_scaled = self.scaler.transform(data)
        X = np.array([data_scaled[-self.sequence_length:]])
        predictions = self.model.predict(X)
        return predictions.flatten()

    def save_model(self, output_path="models/lstm_model.h5"):
        """
        Save the trained LSTM model to a file.
        :param output_path: Path to save the model.
        """
        self.model.save(output_path)
        print(f"LSTM model saved to {output_path}")

    def load_model(self, model_path):
        """
        Load a trained LSTM model from a file.
        :param model_path: Path to the model file.
        """
        from tensorflow.keras.models import load_model
        self.model = load_model(model_path)
        print(f"LSTM model loaded from {model_path}")


if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        "feature1": np.random.uniform(100, 200, 100),
        "feature2": np.random.uniform(50, 150, 100),
        "target": np.random.uniform(100, 200, 100),
    })

    lstm_model = LSTMModel(sequence_length=30)

    # Train the model
    history, metrics = lstm_model.train(data, target_column="target", epochs=5, batch_size=16)
    print("Training Metrics:", metrics)

    # Save and load the model
    lstm_model.save_model()
    lstm_model.load_model("models/lstm_model.h5")

    # Predict future values
    predictions = lstm_model.predict(data)
    print("Predictions:", predictions)
