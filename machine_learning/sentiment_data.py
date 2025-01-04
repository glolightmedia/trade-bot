import pandas as pd
import requests
from datetime import datetime
from textblob import TextBlob

class SentimentData:
    """
    Handles sentiment data collection and preprocessing for trading decisions.
    """

    def __init__(self, twitter_api_key=None, reddit_client_id=None, reddit_client_secret=None):
        """
        Initialize the SentimentData class with API credentials.
        :param twitter_api_key: API key for Twitter (optional).
        :param reddit_client_id: Client ID for Reddit API (optional).
        :param reddit_client_secret: Client Secret for Reddit API (optional).
        """
        self.twitter_api_key = twitter_api_key
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret

    def fetch_twitter_data(self, query, count=100):
        """
        Fetch tweets using Twitter API.
        :param query: Search query (e.g., stock ticker).
        :param count: Number of tweets to fetch.
        :return: DataFrame with tweet text and sentiment score.
        """
        # Placeholder for real Twitter API call
        print(f"Fetching {count} tweets for query: {query}")
        tweets = [
            {"text": "Stock prices are surging today!", "timestamp": datetime.now()},
            {"text": "Market crashes, investors are worried.", "timestamp": datetime.now()},
        ]
        return self.process_sentiment(pd.DataFrame(tweets))

    def fetch_reddit_data(self, subreddit, limit=100):
        """
        Fetch Reddit posts using Reddit API.
        :param subreddit: Subreddit to fetch posts from (e.g., WallStreetBets).
        :param limit: Number of posts to fetch.
        :return: DataFrame with post text and sentiment score.
        """
        # Placeholder for real Reddit API call
        print(f"Fetching {limit} posts from subreddit: {subreddit}")
        posts = [
            {"text": "Earnings report exceeds expectations!", "timestamp": datetime.now()},
            {"text": "Economic slowdown predicted by analysts.", "timestamp": datetime.now()},
        ]
        return self.process_sentiment(pd.DataFrame(posts))

    @staticmethod
    def process_sentiment(data):
        """
        Analyze sentiment of text data using TextBlob.
        :param data: DataFrame with 'text' column.
        :return: DataFrame with added 'sentiment' column.
        """
        data["sentiment"] = data["text"].apply(lambda x: TextBlob(x).sentiment.polarity)
        data["sentiment_label"] = data["sentiment"].apply(lambda x: 1 if x > 0 else (0 if x == 0 else -1))
        return data

    def save_to_csv(self, data, output_path):
        """
        Save processed sentiment data to a CSV file.
        :param data: DataFrame to save.
        :param output_path: File path for the CSV file.
        """
        data.to_csv(output_path, index=False)
        print(f"Sentiment data saved to {output_path}")


if __name__ == "__main__":
    sentiment_data = SentimentData()

    # Fetch Twitter data
    twitter_data = sentiment_data.fetch_twitter_data(query="AAPL", count=5)
    print("Twitter Data:")
    print(twitter_data)

    # Fetch Reddit data
    reddit_data = sentiment_data.fetch_reddit_data(subreddit="WallStreetBets", limit=5)
    print("\nReddit Data:")
    print(reddit_data)

    # Save to CSV
    sentiment_data.save_to_csv(twitter_data, "twitter_sentiment.csv")
    sentiment_data.save_to_csv(reddit_data, "reddit_sentiment.csv")
