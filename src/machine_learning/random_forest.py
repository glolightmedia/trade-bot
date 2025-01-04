import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report
import pandas as pd

class RandomForestModel:
    """
    Implements a Random Forest model for trading decision-making.
    """

    def __init__(self, n_estimators=100, max_depth=None, random_state=42):
        """
        Initialize the Random Forest model.
        :param n_estimators: Number of trees in the forest.
        :param max_depth: Maximum depth of the trees.
        :param random_state: Random state for reproducibility.
        """
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)

    def train(self, data, target_column, test_size=0.2):
        """
        Train the Random Forest model.
        :param data: DataFrame containing features and target column.
        :param target_column: Name of the target column.
        :param test_size: Proportion of data to use for testing.
        :return: Dictionary with training metrics.
        """
        X = data.drop(columns=[target_column])
        y = data[target_column]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        metrics = self.evaluate_model(y_test, y_pred)

        print("Training Complete. Metrics:")
        print(metrics)
        return metrics

    def predict(self, data):
        """
        Predict trading signals using the trained model.
        :param data: DataFrame with feature columns.
        :return: Array of predictions.
        """
        return self.model.predict(data)

    def feature_importance(self):
        """
        Get feature importance from the trained model.
        :return: Series with feature importance values.
        """
        return pd.Series(self.model.feature_importances_, name="Importance")

    def save_model(self, output_path="models/random_forest.pkl"):
        """
        Save the trained model to a file.
        :param output_path: Path to save the model.
        """
        joblib.dump(self.model, output_path)
        print(f"Model saved to {output_path}")

    def load_model(self, model_path):
        """
        Load a trained model from a file.
        :param model_path: Path to the model file.
        """
        self.model = joblib.load(model_path)
        print(f"Model loaded from {model_path}")

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
    # Sample data
    data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        "target": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    })

    # Initialize and train model
    rf_model = RandomForestModel()
    metrics = rf_model.train(data, target_column="target")

    # Save and load model
    rf_model.save_model()
    rf_model.load_model("models/random_forest.pkl")

    # Make predictions
    predictions = rf_model.predict(data.drop(columns=["target"]))
    print("Predictions:", predictions)

    # Feature importance
    importance = rf_model.feature_importance()
    print("Feature Importance:")
    print(importance)
