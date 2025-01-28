import importlib
import os
import toml

class StrategyLoader:
    """
    Dynamically loads and manages trading strategies from the strategies directory.
    """

    def __init__(self, strategies_dir="src/strategies", config_dir="config/strategies"):
        self.strategies_dir = strategies_dir
        self.config_dir = config_dir
        self.strategies = {}

    def load_strategies(self):
        """Load strategies dynamically using CamelCase class naming convention."""
        for file in os.listdir(self.strategies_dir):
            if file.endswith(".py") and file not in ["__init__.py", "strategy_loader.py"]:
                strategy_name = file[:-3]  # Remove '.py'
                module_path = f"src.strategies.{strategy_name}"
                
                try:
                    # Import strategy module
                    module = importlib.import_module(module_path)
                    
                    # Generate CamelCase class name (e.g., 'hft' -> 'HFTStrategy')
                    class_name = (
                        strategy_name.upper() + "Strategy"  # For acronyms like HFT
                        if "_" not in strategy_name
                        else "".join([part.capitalize() for part in strategy_name.split("_")]) + "Strategy"
                    )
                    
                    # Get strategy class
                    strategy_class = getattr(module, class_name)
                    
                    # Load configuration
                    config_path = os.path.join(self.config_dir, f"{strategy_name}.toml")
                    config = toml.load(config_path) if os.path.exists(config_path) else {}
                    
                    # Instantiate and store
                    self.strategies[strategy_name] = strategy_class(config, None, None)  # Adjust args as needed
                    
                except AttributeError:
                    print(f"Class {class_name} not found in {file}")
                except Exception as e:
                    print(f"Error loading {strategy_name}: {str(e)}")

    def get_strategy(self, name):
        return self.strategies.get(name)

    def list_strategies(self):
        return list(self.strategies.keys())


if __name__ == "__main__":
    loader = StrategyLoader()
    loader.load_strategies()
    print("Loaded strategies:", loader.list_strategies())
