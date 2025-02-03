import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
from alpaca_trade_api import REST
from src.machine_learning.sentiment_model import SentimentModel
from src.machine_learning.lstm_model import LSTMModel
from src.machine_learning.random_forest import RandomForestModel
from src.plugins import sentiment_plugin, hft_plugin
from src.portfolio_manager import Portfolio

# Load Configuration
@st.cache_resource
def load_config():
    try:
        with open("config/config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Configuration file missing")
        st.stop()

config = load_config()

# Initialize Core Components
@st.cache_resource
def initialize_components():
    try:
        api = REST(config["API_KEY"], config["SECRET_KEY"], config["BASE_URL"])
        portfolio = Portfolio(config, api)
        hft = hft_plugin.HFTPlugin(config, api)
        
        # Initialize ML Models
        sentiment_model = SentimentModel()
        sentiment_model.load_model("models/pre_trained/vectorizer.pkl", 
                                 config["MACHINE_LEARNING"]["models"]["sentiment_model"]["path"])
        
        rf_model = RandomForestModel()
        rf_model.load_model(config["MACHINE_LEARNING"]["models"]["random_forest"]["path"])
        
        lstm_model = LSTMModel(sequence_length=30)
        lstm_model.load_model(config["MACHINE_LEARNING"]["models"]["lstm_model"]["path"])
        
        return api, portfolio, hft, sentiment_model, rf_model, lstm_model
        
    except Exception as e:
        st.error(f"Initialization failed: {e}")
        st.stop()

api, portfolio, hft_plugin, sentiment_model, rf_model, lstm_model = initialize_components()

# Real-Time Data Processing
@st.cache_data(ttl=10)
def get_realtime_data():
    """Fetch and process real-time trading data"""
    try:
        # Portfolio Metrics
        account = api.get_account()
        positions = api.list_positions()
        
        # Strategy Performance
        strategy_metrics = hft_plugin.performance_metrics
        
        # Market Data
        symbols = [pos.symbol for pos in positions][:5]  # Top 5 positions
        bars = {sym: api.get_latest_bar(sym) for sym in symbols}
        
        return {
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "positions": positions,
            "strategy_metrics": strategy_metrics,
            "market_data": bars,
            "hft_stats": {
                "trade_count": hft_plugin.trade_count,
                "volatility": hft_plugin.volatility_data
            }
        }
    except Exception as e:
        st.error(f"Data fetch error: {e}")
        return {}

# Visualization Components
def display_strategy_performance(metrics):
    """Interactive strategy performance visualization"""
    df = pd.DataFrame.from_dict(metrics, orient='index')
    df.reset_index(inplace=True)
    df.columns = ['Strategy', 'Success Rate']
    
    fig = px.bar(df, x='Strategy', y='Success Rate', 
                title='Strategy Performance (24h Success Rate)',
                color='Success Rate', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

def display_volatility_heatmap(data):
    """Volatility visualization for current positions"""
    df = pd.DataFrame([{
        'Symbol': sym,
        'ATR': data[sym]['atr'],
        'Price': data[sym]['last_price']
    } for sym in data])
    
    fig = px.scatter(df, x='Symbol', y='ATR', size='Price',
                    title='Volatility Analysis (ATR vs Price)',
                    color='ATR', hover_data=['Price'])
    st.plotly_chart(fig, use_container_width=True)

def display_ml_insights():
    """Machine learning model insights"""
    # Model accuracy data (example - integrate real metrics)
    accuracy_data = {
        'Model': ['Random Forest', 'LSTM', 'Sentiment'],
        'Accuracy': [0.82, 0.78, 0.75],
        'Last Retrained': [datetime.now() - timedelta(hours=12),
                          datetime.now() - timedelta(hours=6),
                          datetime.now() - timedelta(days=1)]
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Model Performance")
        st.dataframe(pd.DataFrame(accuracy_data), hide_index=True)
    
    with col2:
        st.subheader("Feature Importance")
        features = rf_model.get_feature_importance()  # Requires method in model class
        fig = px.pie(names=features.index, values=features.values)
        st.plotly_chart(fig, use_container_width=True)

# Dashboard Layout
st.set_page_config(
    page_title="Next-Gen Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Controls
with st.sidebar:
    st.header("Trading Controls")
    auto_trading = st.toggle("Auto Trading", value=True)
    risk_level = st.slider("Risk Level", 1, 5, 3)
    st.write(f"Current Mode: {'HFT' if hft_plugin.hft_settings['enabled'] else 'Standard'}")
    st.progress(hft_plugin.trade_count / hft_plugin.trade_limit, 
               text=f"HFT Trades: {hft_plugin.trade_count}/{hft_plugin.trade_limit}")

# Main Dashboard Sections
tab1, tab2, tab3 = st.tabs(["Portfolio Overview", "Strategy Analysis", "ML Insights"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Equity Curve")
        equity_history = portfolio.get_equity_history()  # Requires method in Portfolio
        st.line_chart(equency_history.set_index('timestamp'))
        
    with col2:
        st.subheader("Quick Stats")
        data = get_realtime_data()
        st.metric("Total Equity", f"${data.get('equity', 0):,.2f}")
        st.metric("Available Liquidity", f"${data.get('buying_power', 0):,.2f}")
        st.metric("Active Positions", len(data.get('positions', [])))

with tab2:
    st.subheader("Strategy Performance")
    display_strategy_performance(data.get('strategy_metrics', {}))
    
    st.subheader("Market Analysis")
    display_volatility_heatmap(data.get('hft_stats', {}).get('volatility', {}))
    
    st.subheader("Position Breakdown")
    pos_df = pd.DataFrame([{
        'Symbol': pos.symbol,
        'Shares': int(pos.qty),
        'Entry Price': float(pos.avg_entry_price),
        'Current Price': float(pos.current_price),
        'P/L%': (float(pos.current_price) - float(pos.avg_entry_price)) / float(pos.avg_entry_price) * 100
    } for pos in data.get('positions', [])])
    st.dataframe(pos_df.style.format({'P/L%': '{:.2f}%'}), use_container_width=True)

with tab3:
    display_ml_insights()
    st.subheader("Sentiment Analysis")
    symbol = st.selectbox("Select Symbol", [pos.symbol for pos in data.get('positions', [])])
    if symbol:
        sentiment = sentiment_plugin.analyze_sentiment(symbol)
        st.write(f"Sentiment Score: {sentiment:.2f}")
        st.progress(sentiment, text="Market Sentiment")

# Real-Time Updates
st.sidebar.header("System Health")
with st.sidebar:
    st.write(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("Force Refresh"):
        st.rerun()
    st.write("API Status: ✔️ Connected" if api.get_clock().is_open else "❌ Disconnected")
    st.write(f"Model Versions: LSTM v{lstm_model.version} | RF v{rf_model.version}")

# Error Handling
if 'error' in data:
    st.error(f"Data Error: {data['error']}")
