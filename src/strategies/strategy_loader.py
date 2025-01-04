import importlib
import os
import toml

class StrategyLoader:
    """
    Dynamically loads and manages trading strategies from the strategies directory.
    """

    def __init__(self, strategies_dir="src/strategies", config_dir="config/strategies"):
        """
        Initialize the StrategyLoader.
        :param strategies_dir: Directory containing strategy implementations.
        :param config_dir: Directory containing strategy configurations.
        """
        self.strategies_dir = strategies_dir
        self.config_dir = config_dir
        self.strategies = {}

    def load_strategies(self):
        """
        Load all strategies dynamically from the strategies directory.
        """
        for file in os.listdir(self.strategies_dir):
            if file.endswith(".py") and file != "strategy_loader.py" and file != "__init__.py":
                strategy_name = file.replace(".py", "")
                try:
                    module = importlib.import_module(f"src.strategies.{strategy_name}")
                    config_path = os.path.join(self.config_dir, f"{strategy_name.upper()}.toml")
                    if os.path.exists(config_path):
                        config = toml.load(config_path)
                        self.strategies[strategy_name] = module.Strategy(config)
                    else:
                        print(f"Warning: No configuration found for {strategy_name}. Skipping.")
                except Exception as e:
                    print(f"Error loading strategy {strategy_name}: {e}")

    def get_strategy(self, name):
        """
        Retrieve a loaded strategy by name.
        :param name: Name of the strategy.
        :return: Strategy instance or None.
        """
        return self.strategies.get(name)

    def list_strategies(self):
        """
        List all loaded strategies.
        :return: List of strategy names.
        """
        return list(self.strategies.keys())


if __name__ == "__main__":
    loader = StrategyLoader()
    loader.load_strategies()

    print("Loaded strategies:", loader.list_strategies())
    for strategy_name in loader.list_strategies():
        strategy = loader.get_strategy(strategy_name)
        print(f"Loaded strategy: {strategy_name}, Config: {strategy}")
