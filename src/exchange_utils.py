import time
import logging
import functools
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Callable, Optional, Dict, Any

class ExchangeUtils:
    def __init__(self, config_path="config/config.json"):
        self.config = self._load_config(config_path)
        self.rate_limits = self.config.get("rate_limits", {})
        self.request_history = defaultdict(deque)
        self.cache = {}
        self.last_error_time = None
        self.error_count = 0
        
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}

    @staticmethod
    def retry(api_call: Callable, retries: int = 5, delay: float = 2, backoff: float = 2):
        """
        Enhanced retry decorator with exponential backoff and error classification.
        """
        @functools.wraps(api_call)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None
            
            while attempt < retries:
                try:
                    return api_call(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    last_exception = e
                    error_type = self.classify_error(e)
                    
                    if error_type == "fatal":
                        logging.error(f"Fatal error encountered: {e}")
                        raise
                        
                    logging.warning(f"Attempt {attempt}/{retries} failed ({error_type}): {e}")
                    
                    if attempt < retries:
                        sleep_time = delay * (backoff ** (attempt - 1))
                        time.sleep(sleep_time)
            
            logging.error(f"Max retries reached. Last error: {last_exception}")
            raise last_exception
            
        return wrapper

    @staticmethod
    def classify_error(error: Exception) -> str:
        """Classify API errors for appropriate handling"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str:
            return "rate_limit"
        elif "timeout" in error_str:
            return "timeout"
        elif "authentication" in error_str:
            return "auth"
        elif "not found" in error_str:
            return "not_found"
        else:
            return "retryable"

    def rate_limit(self, endpoint: str):
        """
        Decorator to enforce rate limits on API calls.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                limit_config = self.rate_limits.get(endpoint, {})
                max_requests = limit_config.get("max_requests", 60)
                period = limit_config.get("period_seconds", 60)
                
                now = time.time()
                history = self.request_history[endpoint]
                
                # Remove old requests
                while history and now - history[0] > period:
                    history.popleft()
                    
                if len(history) >= max_requests:
                    sleep_time = period - (now - history[0])
                    logging.warning(f"Rate limit reached. Sleeping for {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                
                history.append(now)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def cache_response(self, ttl: int = 60):
        """
        Decorator to cache API responses.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._create_cache_key(func, args, kwargs)
                
                if cache_key in self.cache:
                    cached_time, response = self.cache[cache_key]
                    if time.time() - cached_time < ttl:
                        return response
                
                result = func(*args, **kwargs)
                self.cache[cache_key] = (time.time(), result)
                return result
            return wrapper
        return decorator

    def _create_cache_key(self, func, args, kwargs) -> str:
        """Create a unique cache key for function calls"""
        return f"{func.__name__}:{str(args)}:{str(kwargs)}"

    def batch_requests(self, endpoint: str, items: list, batch_size: int = 100):
        """
        Process API requests in batches.
        """
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            try:
                response = self._call_endpoint(endpoint, batch)
                results.extend(response)
            except Exception as e:
                logging.error(f"Batch request failed: {e}")
                raise
                
        return results

    def monitor_api_health(self):
        """Monitor API health and implement circuit breaker pattern"""
        now = datetime.now()
        if self.last_error_time and (now - self.last_error_time) < timedelta(minutes=5):
            self.error_count += 1
        else:
            self.error_count = 0
            
        self.last_error_time = now
        
        if self.error_count > self.config.get("max_errors", 10):
            logging.error("API health critical - entering cooldown period")
            time.sleep(self.config.get("cooldown_period", 300))
            self.error_count = 0

    @staticmethod
    def validate_order(order: Dict[str, Any], market: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive order validation.
        """
        validation = {
            "valid": True,
            "errors": []
        }
        
        # Validate amount
        min_amount = market.get("minimalOrder", {}).get("amount", 0)
        if order["amount"] < min_amount:
            validation["valid"] = False
            validation["errors"].append(f"Amount below minimum: {min_amount}")
            
        # Validate price
        if "price" in order:
            price = order["price"]
            min_price = market.get("minimalOrder", {}).get("price", 0)
            if price < min_price:
                validation["valid"] = False
                validation["errors"].append(f"Price below minimum: {min_price}")
                
            if "isValidPrice" in market and not market["isValidPrice"](price):
                validation["valid"] = False
                validation["errors"].append("Invalid price format")
                
        return validation

    def bind_all(self, target_instance, method_names: Optional[list] = None):
        """
        Enhanced method binding with decorator support.
        """
        methods = method_names or [
            method for method in dir(target_instance)
            if callable(getattr(target_instance, method)) and not method.startswith("_")
        ]
        
        for method_name in methods:
            method = getattr(target_instance, method_name)
            bound_method = method.__get__(target_instance, target_instance.__class__)
            
            # Apply decorators based on method name
            if method_name.startswith("get_"):
                bound_method = self.cache_response(ttl=60)(bound_method)
            elif method_name.startswith("create_"):
                bound_method = self.rate_limit("write")(bound_method)
                
            setattr(target_instance, method_name, bound_method)
