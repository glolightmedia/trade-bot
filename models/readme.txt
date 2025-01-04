# Models Directory

This directory is used to store machine learning models used by the trading bot.

## Purpose
1. **Pre-Trained Models**: Store models that have been trained on historical stock and sentiment data.
2. **Model Checkpoints**: Save intermediate checkpoints for retraining or testing purposes.
3. **Serialized Models**: Keep serialized models (e.g., TensorFlow SavedModels, Pickle, or Joblib files) for deployment.

## File Types
- **HDF5 or SavedModel Format**: TensorFlow/Keras models for neural networks.
- **Joblib/Pickle Files**: Serialized models for simpler ML algorithms.
- **Text Files**: Metadata about models, such as training parameters or accuracy.

## Usage Notes
- Ensure proper versioning of models for reproducibility.
- Maintain metadata files to track the origin and performance of models.
- Do not store large model files directly in repositories; use storage services if needed.

