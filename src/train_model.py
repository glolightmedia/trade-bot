import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, classification_report)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from src.backtesting.prepare_date_range import preprocess_data
from src.config.logging_config import setup_logging

# Initialize logging
setup_logging()

class ModelTrainer:
    def __init__(self, config_path="config/config.json"):
        self.config = self._load_config(config_path)
        self.feature_columns = self.config.get("feature_columns", [
            "SMA_20", "RSI", "MACD", "Normalized_Close", "Volume_Change"
        ])
        self.target_column = "Target"
        self.model_params = self.config.get("model_params", {
            "n_estimators": 100,
            "max_depth": None,
            "min_samples_split": 2,
            "random_state": 42
        })
        self.test_size = self.config.get("test_size", 0.2)
        self.random_state = self.config.get("random_state", 42)

    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}

    def load_and_preprocess_data(self, file_path):
        """
        Load and preprocess historical data for training.
        :param file_path: Path to the historical data CSV file.
        :return: Preprocessed DataFrame.
        """
        try:
            raw_data = pd.read_csv(file_path, parse_dates=["timestamp"])
            data = preprocess_data(raw_data)
            
            # Feature Engineering
            data["Volume_Change"] = data["volume"].pct_change()
            data["Price_Change"] = data["close"].pct_change()
            data["Target"] = (data["close"].shift(-1) > data["close"]).astype(int)
            
            return data.dropna()
        except Exception as e:
            logging.error(f"Error loading and preprocessing data: {e}")
            raise

    def create_feature_pipeline(self):
        """Create feature engineering and preprocessing pipeline"""
        return Pipeline([
            ('scaler', StandardScaler())
        ])

    def train_model(self, data, model_type="random_forest"):
        """
        Train a machine learning model.
        :param data: Preprocessed DataFrame with features and target.
        :param model_type: Type of model to train (default: random_forest).
        :return: Trained model and performance metrics.
        """
        try:
            # Prepare features and target
            X = data[self.feature_columns]
            y = data[self.target_column]
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )
            
            # Feature pipeline
            feature_pipeline = self.create_feature_pipeline()
            X_train = feature_pipeline.fit_transform(X_train)
            X_test = feature_pipeline.transform(X_test)
            
            # Model training
            if model_type == "random_forest":
                model = self._train_random_forest(X_train, y_train)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Model evaluation
            metrics = self.evaluate_model(model, X_test, y_test)
            
            # Save artifacts
            self.save_model_artifacts(model, feature_pipeline, metrics)
            
            return model, metrics
            
        except Exception as e:
            logging.error(f"Error during model training: {e}")
            raise

    def _train_random_forest(self, X_train, y_train):
        """Train Random Forest model with hyperparameter tuning"""
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        }
        
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=self.random_state),
            param_grid,
            cv=3,
            scoring='accuracy',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        logging.info(f"Best parameters: {grid_search.best_params_}")
        return grid_search.best_estimator_

    def evaluate_model(self, model, X_test, y_test):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
            "classification_report": classification_report(y_test, y_pred)
        }
        
        logging.info("Model Evaluation Metrics:")
        for metric, value in metrics.items():
            if metric != "classification_report":
                logging.info(f"{metric.capitalize()}: {value:.4f}")
        
        return metrics

    def save_model_artifacts(self, model, feature_pipeline, metrics):
        """Save model and related artifacts"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"models/random_forest_{timestamp}.pkl"
        pipeline_path = f"models/feature_pipeline_{timestamp}.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(feature_pipeline, pipeline_path)
        
        # Save metrics
        with open(f"models/metrics_{timestamp}.json", "w") as f:
            json.dump(metrics, f)
        
        logging.info(f"Model saved to {model_path}")
        logging.info(f"Feature pipeline saved to {pipeline_path}")

    def retrain_model(self, new_data_path):
        """Retrain model with new data"""
        try:
            new_data = self.load_and_preprocess_data(new_data_path)
            return self.train_model(new_data)
        except Exception as e:
            logging.error(f"Error during model retraining: {e}")
            raise


if __name__ == "__main__":
    trainer = ModelTrainer()
    
    try:
        # Load and preprocess data
        file_path = "data/historical/sample_data.csv"
        data = trainer.load_and_preprocess_data(file_path)
        
        # Train model
        model, metrics = trainer.train_model(data)
        
        # Save final model
        joblib.dump(model, "models/pre_trained/random_forest.pkl")
        logging.info("Model training completed successfully")
        
    except Exception as e:
        logging.error(f"Model training failed: {e}")
        raiseimport pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, classification_report)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from src.backtesting.prepare_date_range import preprocess_data
from src.config.logging_config import setup_logging

# Initialize logging
setup_logging()

class ModelTrainer:
    def __init__(self, config_path="config/config.json"):
        self.config = self._load_config(config_path)
        self.feature_columns = self.config.get("feature_columns", [
            "SMA_20", "RSI", "MACD", "Normalized_Close", "Volume_Change"
        ])
        self.target_column = "Target"
        self.model_params = self.config.get("model_params", {
            "n_estimators": 100,
            "max_depth": None,
            "min_samples_split": 2,
            "random_state": 42
        })
        self.test_size = self.config.get("test_size", 0.2)
        self.random_state = self.config.get("random_state", 42)

    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}

    def load_and_preprocess_data(self, file_path):
        """
        Load and preprocess historical data for training.
        :param file_path: Path to the historical data CSV file.
        :return: Preprocessed DataFrame.
        """
        try:
            raw_data = pd.read_csv(file_path, parse_dates=["timestamp"])
            data = preprocess_data(raw_data)
            
            # Feature Engineering
            data["Volume_Change"] = data["volume"].pct_change()
            data["Price_Change"] = data["close"].pct_change()
            data["Target"] = (data["close"].shift(-1) > data["close"]).astype(int)
            
            return data.dropna()
        except Exception as e:
            logging.error(f"Error loading and preprocessing data: {e}")
            raise

    def create_feature_pipeline(self):
        """Create feature engineering and preprocessing pipeline"""
        return Pipeline([
            ('scaler', StandardScaler())
        ])

    def train_model(self, data, model_type="random_forest"):
        """
        Train a machine learning model.
        :param data: Preprocessed DataFrame with features and target.
        :param model_type: Type of model to train (default: random_forest).
        :return: Trained model and performance metrics.
        """
        try:
            # Prepare features and target
            X = data[self.feature_columns]
            y = data[self.target_column]
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )
            
            # Feature pipeline
            feature_pipeline = self.create_feature_pipeline()
            X_train = feature_pipeline.fit_transform(X_train)
            X_test = feature_pipeline.transform(X_test)
            
            # Model training
            if model_type == "random_forest":
                model = self._train_random_forest(X_train, y_train)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Model evaluation
            metrics = self.evaluate_model(model, X_test, y_test)
            
            # Save artifacts
            self.save_model_artifacts(model, feature_pipeline, metrics)
            
            return model, metrics
            
        except Exception as e:
            logging.error(f"Error during model training: {e}")
            raise

    def _train_random_forest(self, X_train, y_train):
        """Train Random Forest model with hyperparameter tuning"""
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        }
        
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=self.random_state),
            param_grid,
            cv=3,
            scoring='accuracy',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        logging.info(f"Best parameters: {grid_search.best_params_}")
        return grid_search.best_estimator_

    def evaluate_model(self, model, X_test, y_test):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
            "classification_report": classification_report(y_test, y_pred)
        }
        
        logging.info("Model Evaluation Metrics:")
        for metric, value in metrics.items():
            if metric != "classification_report":
                logging.info(f"{metric.capitalize()}: {value:.4f}")
        
        return metrics

    def save_model_artifacts(self, model, feature_pipeline, metrics):
        """Save model and related artifacts"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"models/random_forest_{timestamp}.pkl"
        pipeline_path = f"models/feature_pipeline_{timestamp}.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(feature_pipeline, pipeline_path)
        
        # Save metrics
        with open(f"models/metrics_{timestamp}.json", "w") as f:
            json.dump(metrics, f)
        
        logging.info(f"Model saved to {model_path}")
        logging.info(f"Feature pipeline saved to {pipeline_path}")

    def retrain_model(self, new_data_path):
        """Retrain model with new data"""
        try:
            new_data = self.load_and_preprocess_data(new_data_path)
            return self.train_model(new_data)
        except Exception as e:
            logging.error(f"Error during model retraining: {e}")
            raise


if __name__ == "__main__":
    trainer = ModelTrainer()
    
    try:
        # Load and preprocess data
        file_path = "data/historical/sample_data.csv"
        data = trainer.load_and_preprocess_data(file_path)
        
        # Train model
        model, metrics = trainer.train_model(data)
        
        # Save final model
        joblib.dump(model, "models/pre_trained/random_forest.pkl")
        logging.info("Model training completed successfully")
        
    except Exception as e:
        logging.error(f"Model training failed: {e}")
        raise
