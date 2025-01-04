# Machine Learning Module Documentation

## Overview

The `machine_learning` folder provides tools to enhance the trading bot with machine learning capabilities. These tools include model training, sentiment analysis, and time-series predictions. The ML module aims to improve decision-making, predict market trends, and incorporate real-time sentiment data.

---

## Key Files and Their Roles

### **1. `train_model.py`**
- **Purpose**: Centralized script for training ML models.
- **Role**:
  - Supports training of Random Forest, LSTM, and other models.
  - Saves trained models to the `models/` directory for deployment.
- **Example Usage**:
  ```python
  from src.machine_learning.train_model import TrainModel

  data = ...  # Load your dataset
  trainer = TrainModel()

  # Train Random Forest
  rf_model, rf_metrics = trainer.train_random_forest(data, "target")

  # Train LSTM
  lstm_model, lstm_metrics = trainer.train_lstm(data, "target")
