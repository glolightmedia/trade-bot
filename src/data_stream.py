import logging
import threading
from time import sleep
from datetime import datetime
import websocket

class DataStream:
    """
    Manages real-time market data streaming.
    Supports subscribing to market data and dispatching updates to consumers.
    """

    def __init__(self, api_url, symbols, interval=1):
        """
        Initialize the DataStream.
        :param api_url: WebSocket API URL for market data.
        :param symbols: List of market symbols to subscribe to.
        :param interval: Update interval in seconds.
        """
        self.api_url = api_url
        self.symbols = symbols
        self.interval = interval
        self.ws = None
        self.running = False
        self.consumers = []

    def connect(self):
        """
        Connect to the WebSocket server.
        """
        self.ws = websocket.WebSocketApp(
            self.api_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_open(self):
        """
        Callback when the WebSocket connection is opened.
        Subscribes to the specified symbols.
        """
        logging.info("WebSocket connection opened.")
        subscription_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": self.symbols}]
        }
        self.ws.send(str(subscription_message))

    def on_message(self, message):
        """
        Callback for handling incoming messages.
        :param message: The incoming WebSocket message.
        """
        logging.info(f"Received message: {message}")
        for consumer in self.consumers:
            consumer(message)

    def on_error(self, error):
        """
        Callback for handling errors.
        :param error: The WebSocket error.
        """
        logging.error(f"WebSocket error: {error}")

    def on_close(self):
        """
        Callback for handling connection closure.
        """
        logging.info("WebSocket connection closed.")

    def add_consumer(self, consumer):
        """
        Add a consumer function to process incoming data.
        :param consumer: Callable to process data.
        """
        self.consumers.append(consumer)

    def stop(self):
        """
        Stop the WebSocket connection.
        """
        self.running = False
        if self.ws:
            self.ws.close()

if __name__ == "__main__":
    # Example usage
    def process_data(message):
        print(f"Processing message: {message}")

    stream = DataStream(
        api_url="wss://ws-feed.exchange.example.com",
        symbols=["BTC-USD", "ETH-USD"],
        interval=1
    )
    stream.add_consumer(process_data)
    stream.connect()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        stream.stop()
        print("Data stream stopped.")
