import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import joblib

class SentimentModel:
    """
    Implements sentiment analysis for market data using NLP.
    """

    def __init__(self, vectorizer_type="tfidf"):
        """
        Initialize the SentimentModel with the specified vectorizer type.
        :param vectorizer_type: "count" for CountVectorizer or "tfidf" for TfidfVectorizer.
        """
        if vectorizer_type == "count":
            self.vectorizer = CountVectorizer()
        elif vectorizer_type == "tfidf":
            self.vectorizer = TfidfVectorizer()
        else:
            raise ValueError("Invalid vectorizer type. Choose 'count' or 'tfidf'.")
        self.model = MultinomialNB()

    def train(self, data, text_column, target_column, test_size=0.2):
        """
        Train the sentiment analysis model.
        :param data: DataFrame containing text and target columns.
        :param text_column: Name of the text column.
        :param target_column: Name of the target column.
        :param test_size: Proportion of data to use for testing.
        :return: Dictionary with training metrics.
        """
        X = data[text_column]
        y = data[target_column]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        self.model.fit(X_train_vec, y_train)

        y_pred = self.model.predict(X_test_vec)
        metrics = self.evaluate_model(y_test, y_pred)

        print("Training Complete. Metrics:")
        print(metrics)
        return metrics

    def predict(self, text_data):
        """
        Predict sentiment for given text data.
        :param text_data: List or Series of text inputs.
        :return: Array of predicted sentiment labels.
        """
        text_vec = self.vectorizer.transform(text_data)
        return self.model.predict(text_vec)

    def save_model(self, vectorizer_path="models/vectorizer.pkl", model_path="models/sentiment_model.pkl"):
        """
        Save the trained model and vectorizer to files.
        :param vectorizer_path: Path to save the vectorizer.
        :param model_path: Path to save the model.
        """
        joblib.dump(self.vectorizer, vectorizer_path)
        joblib.dump(self.model, model_path)
        print(f"Vectorizer saved to {vectorizer_path}")
        print(f"Model saved to {model_path}")

    def load_model(self, vectorizer_path="models/vectorizer.pkl", model_path="models/sentiment_model.pkl"):
        """
        Load a trained model and vectorizer from files.
        :param vectorizer_path: Path to the vectorizer file.
        :param model_path: Path to the model file.
        """
        self.vectorizer = joblib.load(vectorizer_path)
        self.model = joblib.load(model_path)
        print(f"Vectorizer loaded from {vectorizer_path}")
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
            "Classification Report": classification_report(y_true, y_pred, output_dict=True),
        }


if __name__ == "__main__":
    data = pd.DataFrame({
        "text": [
            "Stock prices are surging today!",
            "Market crashes, investors are worried.",
            "Earnings report exceeds expectations.",
            "Economic slowdown predicted by analysts.",
            "Strong demand boosts company revenue."
        ],
        "sentiment": [1, 0, 1, 0, 1]  # 1 = Positive, 0 = Negative
    })

    sentiment_model = SentimentModel(vectorizer_type="tfidf")

    # Train the model
    metrics = sentiment_model.train(data, text_column="text", target_column="sentiment")
    print("Training Metrics:", metrics)

    # Save and load the model
    sentiment_model.save_model()
    sentiment_model.load_model()

    # Predict sentiment
    predictions = sentiment_model.predict(["Great results from the stock market!", "Major losses reported today."])
    print("Predictions:", predictions)
