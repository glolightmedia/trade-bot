# Strategy Configurations

## Overview

This folder contains configuration files for each trading strategy used by the bot. Each file is designed to store parameters and settings specific to a strategy, allowing you to easily adjust and optimize without modifying the core codebase.

---

## Files and Their Purpose

### **1. `DEMA.toml`**
- **Purpose**: Configures the Double Exponential Moving Average (DEMA) strategy.
- **Contents**:
  - `weight`: The period for calculating DEMA.
  - `thresholds`: Buy/sell thresholds based on DEMA divergence.

### **2. `MACD.toml`**
- **Purpose**: Configures the Moving Average Convergence Divergence (MACD) strategy.
- **Contents**:
  - `short`: Short EMA period.
  - `long`: Long EMA period.
  - `signal`: Signal line period.
  - `thresholds`: Buy/sell thresholds based on the MACD histogram.

### **3. `PPO.toml`**
- **Purpose**: Configures the Percentage Price Oscillator (PPO) strategy.
- **Contents**:
  - Similar to MACD but with percentage-based thresholds.

### **4. `CCI.toml`**
- **Purpose**: Configures the Commodity Channel Index (CCI) strategy.
- **Contents**:
  - `constant`: Multiplier for typical price deviation.
  - `history`: Number of periods for calculation.
  - `thresholds`: Overbought/oversold thresholds for buy/sell signals.

### **5. `breakout.toml`**
- **Purpose**: Configures the Breakout strategy.
- **Contents**:
  - `lookback_period`: Number of periods for calculating resistance/support levels.
  - `thresholds`: Multiplier thresholds for buy/sell triggers.

### **6. `ensemble.toml`**
- **Purpose**: Configures the Ensemble strategy, which combines multiple strategies.
- **Contents**:
  - `weights`: Defines the influence of each strategy in the ensemble.

---

## Adding or Modifying Configurations

### **Adding a New Strategy**
1. Create a new `.toml` file in this folder.
2. Define parameters required for the strategy.
3. Update the bot's main script to load the new configuration.

### **Modifying Existing Strategies**
1. Open the corresponding `.toml` file.
2. Adjust parameters like `thresholds` or `lookback_period` to test new configurations.
3. Save the file and restart the bot to apply changes.

---

## Example Configuration File

Below is an example of a configuration file for a hypothetical strategy:

```toml
[parameters]
lookback_period = 10
thresholds = { up = 1.05, down = 0.95 }
