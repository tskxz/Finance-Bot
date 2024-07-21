import yfinance as yf
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from flask_socketio import SocketIO
import threading
import time
import random
import requests
from bson import ObjectId
from flask import session
from industry_thresholds import get_thresholds
import json
import numpy as np

# Initialize SocketIO
socketio = SocketIO()

# MongoDB Connection
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client.stock_data
    print("MongoDB connection established successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

# Add your API keys here
API_KEY_MARKETAUX = 'wWequqmAWjushPoSlxtLiXY1hrWcx6EsmXyf0Q0f'
API_KEY_FMP = '9VUF5Z7WDZY0enSfvMdorG7tncFDEKTQ'

# Fetch Financial Modeling Prep data
def fetch_fmp_data(ticker_symbol):
    try:
        balance_sheet_url = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker_symbol}?apikey={API_KEY_FMP}'
        income_statement_url = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker_symbol}?apikey={API_KEY_FMP}'
        cash_flow_url = f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker_symbol}?apikey={API_KEY_FMP}'
        
        balance_sheet_response = requests.get(balance_sheet_url)
        income_statement_response = requests.get(income_statement_url)
        cash_flow_response = requests.get(cash_flow_url)
        
        balance_sheet_data = balance_sheet_response.json()[0] if balance_sheet_response.status_code == 200 else {}
        income_statement_data = income_statement_response.json()[0] if income_statement_response.status_code == 200 else {}
        cash_flow_data = cash_flow_response.json()[0] if cash_flow_response.status_code == 200 else {}
        
        return {
            "balance_sheet": balance_sheet_data,
            "income_statement": income_statement_data,
            "cash_flow": cash_flow_data
        }
    except Exception as e:
        print(f"Error fetching FMP data for {ticker_symbol}: {e}")
        return None

# Convert numpy types to Python native types
def convert_numpy_types(data):
    if isinstance(data, np.generic):
        return data.item()
    elif isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, str):
        try:
            return float(data.replace(',', ''))
        except ValueError:
            return data
    return data

# Fetch Metrics and Store Data
def fetch_and_store_data(ticker_symbol, period='6mo'):
    # Fetch primary data from FMP
    fmp_data = fetch_fmp_data(ticker_symbol)
    financials = {
        'market_price': 0,
        'eps': 0,
        'forward_pe': 0,
        'growth_rate': 0,
        'net_income': 0,
        'shareholders_equity': 0,
        'total_liabilities': 0,
        'cash_flow': 0,
        'revenue': 0,
        'profit_margin': 0,
        'symbol': ticker_symbol
    }

    if fmp_data:
        balance_sheet = fmp_data.get("balance_sheet", {})
        income_statement = fmp_data.get("income_statement", {})
        cash_flow = fmp_data.get("cash_flow", {})

        financials.update({
            'eps': income_statement.get('eps', 0),
            'forward_pe': income_statement.get('peRatio', 0),
            'growth_rate': income_statement.get('growthRate', 0),
            'net_income': income_statement.get('netIncome', 0),
            'shareholders_equity': balance_sheet.get('totalStockholdersEquity', 0),
            'total_liabilities': balance_sheet.get('totalLiabilities', 0),
            'cash_flow': cash_flow.get('operatingCashFlow', 0),
            'revenue': income_statement.get('revenue', 0),
            'profit_margin': income_statement.get('profitMargin', 0)
        })

    # Fetch secondary data from Yahoo Finance
    ticker = yf.Ticker(ticker_symbol)
    ticker_info = ticker.info

    if ticker_info:
        financials.update({
            'market_price': ticker_info.get('currentPrice', financials['market_price']),
            'eps': ticker_info.get('trailingEps', financials['eps']),
            'forward_pe': ticker_info.get('forwardPE', financials['forward_pe']),
            'growth_rate': ticker_info.get('earningsGrowth', financials['growth_rate']),
            'net_income': ticker_info.get('netIncomeToCommon', financials['net_income']),
            'shareholders_equity': ticker_info.get('totalStockholderEquity', financials['shareholders_equity']),
            'total_liabilities': ticker_info.get('totalDebt', financials['total_liabilities']),
            'cash_flow': ticker_info.get('operatingCashflow', financials['cash_flow']),
            'revenue': ticker_info.get('totalRevenue', financials['revenue']),
            'profit_margin': ticker_info.get('profitMargins', financials['profit_margin'])
        })

    # Convert numpy types to Python native types
    financials = convert_numpy_types(financials)

    # Print financials to debug
    print(f"Financials for {ticker_symbol}: {financials}")

    # Fetch historical data from yfinance
    hist = ticker.history(period=period)
    hist.reset_index(inplace=True)
    hist_dict = hist.to_dict(orient="records")

    company_name = ticker_info.get('shortName', 'Unknown Firm')
    
    stocks_collection = db.stocks
    stocks_collection.update_one(
        {"symbol": ticker_symbol},
        {"$set": {"history": hist_dict, "name": company_name, "financials": financials, "sector": ticker_info.get('sector', 'Unknown')}},
        upsert=True
    )

    sentiment = fetch_sentiment_data(ticker_symbol)
    store_sentiment_data(ticker_symbol, sentiment)

    log_activity(session.get('username', 'system'), 'fetch_and_store_data', f"Fetched data for {ticker_symbol}")

# Calculations for Financial Ratios and Intrinsic Value
def calculate_ratios_and_intrinsic_value(financials):
    market_price = financials.get('market_price', 0)
    eps = financials.get('eps', 0)
    forward_pe = financials.get('forward_pe', 0)
    growth_rate = financials.get('growth_rate', 0)
    net_income = financials.get('net_income', 0)
    shareholders_equity = financials.get('shareholders_equity', 0)
    total_liabilities = financials.get('total_liabilities', 0)
    cash_flow = financials.get('cash_flow', 0)
    revenue = financials.get('revenue', 0)
    profit_margin = financials.get('profit_margin', 0)

    # Print statements to see the data
    print(f"Market Price: {market_price}")
    print(f"EPS: {eps}")
    print(f"Forward PE: {forward_pe}")
    print(f"Growth Rate: {growth_rate}")
    print(f"Net Income: {net_income}")
    print(f"Shareholders' Equity: {shareholders_equity}")
    print(f"Total Liabilities: {total_liabilities}")
    print(f"Cash Flow: {cash_flow}")
    print(f"Revenue: {revenue}")
    print(f"Profit Margin: {profit_margin}")

    # Calculate Price to Earnings Ratio (P/E)
    price_to_earnings_ratio = market_price / eps if eps else float('inf')
    
    # Calculate Debt to Equity Ratio (D/E)
    debt_to_equity_ratio = total_liabilities / shareholders_equity if shareholders_equity else float('inf')
    
    # Calculate Return on Equity (ROE)
    return_on_equity = net_income / shareholders_equity if shareholders_equity else 0
    
    # Calculate Current Ratio
    # Note: Current Ratio calculation requires Current Assets and Current Liabilities which are not provided in the initial data
    current_ratio = cash_flow / total_liabilities if total_liabilities else float('inf')
    
    # Calculate Price to Earnings to Growth Ratio (PEG)
    price_to_earnings_to_growth_ratio = forward_pe / (growth_rate * 100) if growth_rate else float('inf')
    
    # Calculate Profit Margin to Revenue
    profit_margin_to_revenue = (net_income / revenue) * 100 if revenue else 0
    
    # Calculate Intrinsic Value
    intrinsic_value = (eps * (1 + 0.05) / 0.10) if eps else 0
    
    return (price_to_earnings_ratio, debt_to_equity_ratio, return_on_equity, current_ratio, 
            intrinsic_value, price_to_earnings_to_growth_ratio, profit_margin_to_revenue, 
            growth_rate)

# Momentum Indicators Calculations
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(df, short_period=12, long_period=26, signal_period=9):
    short_ema = df['Close'].ewm(span=short_period, adjust=False).mean()
    long_ema = df['Close'].ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]

def calculate_bollinger_bands(df, period=20):
    sma = df['Close'].rolling(window=period).mean()
    std = df['Close'].rolling(window=period).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band.iloc[-1], lower_band.iloc[-1]

# Fetch News and Store
def fetch_and_store_news(ticker_symbol):
    url = f'https://api.marketaux.com/v1/news/all?symbols={ticker_symbol}&filter_entities=true&language=en&api_token={API_KEY_MARKETAUX}'
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        if 'data' in news_data:
            articles = news_data['data']
            for article in articles:
                published_at = article.get('published_at')
                existing_article = db.news.find_one({"symbol": ticker_symbol, "url": article.get('url')})

                if existing_article:
                    existing_published_at = existing_article.get('publishedAt')
                    if existing_published_at == published_at:
                        continue  # Skip updating if the article was not updated

                news_entry = {
                    'symbol': ticker_symbol,
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'url': article.get('url'),
                    'publishedAt': published_at
                }
                db.news.update_one(
                    {"symbol": ticker_symbol, "url": article.get('url')},
                    {"$set": news_entry},
                    upsert=True
                )
            log_activity(session.get('username', 'system'), 'fetch_and_store_news', f"Fetched news for {ticker_symbol}")
    else:
        print(f"Error fetching news for {ticker_symbol}: {response.status_code}")

# Get News by Symbol
def get_news_by_symbol(ticker_symbol):
    news_collection = db.news
    news_articles = list(news_collection.find({"symbol": ticker_symbol}).sort("publishedAt", -1))
    for article in news_articles:
        article['_id'] = str(article['_id'])
    return news_articles

# Load Language files
def load_language_file(language):
    with open(f'translations/translations_{language}.json', 'r') as lang_file:
        return json.load(lang_file)

# Fetch Sentiment Data
def fetch_sentiment_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    sentiment = ticker.info.get('recommendationKey', 'Neutral')  # Example, replace with actual sentiment data if available
    return sentiment

# Store Sentiment Data
def store_sentiment_data(ticker_symbol, sentiment):
    sentiment_collection = db.sentiment_analysis
    sentiment_data = {
        "symbol": ticker_symbol,
        "sentiment": sentiment,
        "timestamp": datetime.utcnow()
    }
    sentiment_collection.update_one(
        {"symbol": ticker_symbol},
        {"$set": sentiment_data},
        upsert=True
    )

# Save Recommendation to Database
def save_recommendation(ticker_symbol, recommendation, explanation, sentiment):
    recommendations_collection = db.recommendations
    recommendation_data = {
        "symbol": ticker_symbol,
        "recommendation": recommendation,
        "explanation": explanation,
        "sentiment": sentiment,
        "timestamp": datetime.utcnow()
    }
    recommendations_collection.update_one(
        {"symbol": ticker_symbol},
        {"$set": recommendation_data},
        upsert=True
    )

# New Evaluation Function
def evaluate_metric(value, threshold, higher_is_better=True):
    """Evaluates a single metric against a threshold."""
    return 1 if (value >= threshold if higher_is_better else value <= threshold) else 0

# Analysis and Recommendation
def get_recommendation(data, financials, sentiment, industry):
    df = pd.DataFrame(data)
    
    # Calculate moving averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    ma20_latest = df['MA20'].iloc[-1]
    ma50_latest = df['MA50'].iloc[-1]
    
    # Calculate momentum indicators
    rsi = calculate_rsi(df)
    macd, signal = calculate_macd(df)
    upper_band, lower_band = calculate_bollinger_bands(df)
    
    (pe_ratio, de_ratio, roe, current_ratio, intrinsic_value, peg_ratio, profit_margin_to_revenue, revenue_growth) = calculate_ratios_and_intrinsic_value(financials)
    
    market_price = financials['market_price']
    
    thresholds = get_thresholds(industry)
    pe_threshold = thresholds.get('pe_threshold', 25)
    de_threshold = thresholds.get('de_threshold', 1.5)
    current_ratio_threshold = thresholds.get('current_ratio_threshold', 1.5)
    peg_threshold = thresholds.get('peg_threshold', 1.0)
    profit_margin_threshold = thresholds.get('profit_margin_threshold', 10)
    revenue_growth_threshold = thresholds.get('revenue_growth_threshold', 0.1)
    
    # Initialize score
    score = 0
    
    # Evaluate each metric and add to the score
    score += evaluate_metric(ma20_latest, ma50_latest, higher_is_better=True)  # MA20 > MA50
    score += evaluate_metric(market_price, intrinsic_value, higher_is_better=False)  # Market price < Intrinsic value
    score += evaluate_metric(rsi, 70, higher_is_better=False)  # RSI < 70
    score += evaluate_metric(macd, signal, higher_is_better=True)  # MACD > Signal
    score += evaluate_metric(market_price, upper_band, higher_is_better=False)  # Market price < Upper Bollinger Band
    score += evaluate_metric(pe_ratio, pe_threshold, higher_is_better=False)  # PE < Threshold
    score += evaluate_metric(de_ratio, de_threshold, higher_is_better=False)  # DE < Threshold
    score += evaluate_metric(current_ratio, current_ratio_threshold, higher_is_better=True)  # Current ratio > Threshold
    score += evaluate_metric(peg_ratio, peg_threshold, higher_is_better=False)  # PEG < Threshold
    score += evaluate_metric(profit_margin_to_revenue, profit_margin_threshold, higher_is_better=True)  # Profit margin > Threshold
    score += evaluate_metric(revenue_growth, revenue_growth_threshold, higher_is_better=True)  # Revenue growth > Threshold
    
    # Determine the recommendation based on the overall score
    if score >= 9:  # Adjust this threshold based on desired flexibility
        recommendation = "Buy"
        explanation = (
            f"**Buy Recommendation:**\n"
            f"The 20-day moving average (MA20: {ma20_latest:.2f}) is above the 50-day moving average (MA50: {ma50_latest:.2f}), indicating an upward trend in the stock price.\n"
            f"The stock is undervalued, with an intrinsic value (${intrinsic_value:.2f}) higher than the current market price (${market_price:.2f}).\n"
            f"RSI is {rsi:.2f}, which is below 70, indicating that the stock is not overbought.\n"
            f"MACD ({macd:.2f}) is above the signal line ({signal:.2f}), indicating a positive momentum.\n"
            f"The current price (${market_price:.2f}) is below the upper Bollinger Band (${upper_band:.2f}).\n"
            f"Financial ratios support this recommendation:\n"
            f"- Price to Earnings Ratio (P/E): {pe_ratio:.2f} (below the threshold of {pe_threshold})\n"
            f"- Debt to Equity Ratio (D/E): {de_ratio:.2f} (below the threshold of {de_threshold})\n"
            f"- Return on Equity (ROE): {roe:.2f}\n"
            f"- Current Ratio: {current_ratio:.2f} (above the threshold of {current_ratio_threshold})\n"
            f"- Price to Earnings to Growth Ratio (PEG): {peg_ratio:.2f} (below the threshold of {peg_threshold})\n"
            f"- Profit Margin to Revenue: {profit_margin_to_revenue:.2f}% (above the threshold of {profit_margin_threshold}%)\n"
            f"- Revenue Growth: {revenue_growth:.2f}% (above the threshold of {revenue_growth_threshold}%)\n"
            f"These indicators suggest that the stock is reasonably priced and financially stable, making it a good buy opportunity."
        )
    elif score <= 4:  # Adjust this threshold based on desired flexibility
        recommendation = "Sell"
        explanation = (
            f"**Sell Recommendation:**\n"
            f"The 20-day moving average (MA20: {ma20_latest:.2f}) is below the 50-day moving average (MA50: {ma50_latest:.2f}), indicating a downward trend in the stock price.\n"
            f"The stock is overvalued, with an intrinsic value (${intrinsic_value:.2f}) lower than the current market price (${market_price:.2f}).\n"
            f"RSI is {rsi:.2f}, which is above 70, indicating that the stock is overbought.\n"
            f"MACD ({macd:.2f}) is below the signal line ({signal:.2f}), indicating a negative momentum.\n"
            f"The current price (${market_price:.2f}) is above the upper Bollinger Band (${upper_band:.2f}).\n"
            f"Financial ratios support this recommendation:\n"
            f"- Price to Earnings Ratio (P/E): {pe_ratio:.2f} (above the threshold of {pe_threshold})\n"
            f"- Debt to Equity Ratio (D/E): {de_ratio:.2f} (above the threshold of {de_threshold})\n"
            f"- Return on Equity (ROE): {roe:.2f}\n"
            f"- Current Ratio: {current_ratio:.2f} (below the threshold of {current_ratio_threshold})\n"
            f"- Price to Earnings to Growth Ratio (PEG): {peg_ratio:.2f} (above the threshold of {peg_threshold})\n"
            f"- Profit Margin to Revenue: {profit_margin_to_revenue:.2f}% (below the threshold of {profit_margin_threshold}%)\n"
            f"- Revenue Growth: {revenue_growth:.2f}% (below the threshold of {revenue_growth_threshold}%)\n"
            f"These indicators suggest that the stock is overpriced and may face financial instability, making it a good sell opportunity."
        )
    else:
        recommendation = "Hold"
        explanation = (
            f"**Hold Recommendation:**\n"
            f"The 20-day moving average (MA20: {ma20_latest:.2f}) is close to the 50-day moving average (MA50: {ma50_latest:.2f}), indicating no significant trend.\n"
            f"The stock's market price (${market_price:.2f}) is within the intrinsic value (${intrinsic_value:.2f}).\n"
            f"RSI is {rsi:.2f}, which is below 70, indicating that the stock is not overbought.\n"
            f"MACD ({macd:.2f}) is close to the signal line ({signal:.2f}), indicating no significant momentum.\n"
            f"The current price (${market_price:.2f}) is close to the upper Bollinger Band (${upper_band:.2f}).\n"
            f"Financial ratios support a hold decision:\n"
            f"- Price to Earnings Ratio (P/E): {pe_ratio:.2f} (below the threshold of {pe_threshold})\n"
            f"- Debt to Equity Ratio (D/E): {de_ratio:.2f} (below the threshold of {de_threshold})\n"
            f"- Return on Equity (ROE): {roe:.2f}\n"
            f"- Current Ratio: {current_ratio:.2f} (above the threshold of {current_ratio_threshold})\n"
            f"- Price to Earnings to Growth Ratio (PEG): {peg_ratio:.2f} (below the threshold of {peg_threshold})\n"
            f"- Profit Margin to Revenue: {profit_margin_to_revenue:.2f}% (above the threshold of {profit_margin_threshold}%)\n"
            f"- Revenue Growth: {revenue_growth:.2f}% (above the threshold of {revenue_growth_threshold}%)\n"
            f"These indicators suggest that the stock is fairly priced and financially stable, making it a hold opportunity."
        )
    
    # Save the recommendation to the database
    save_recommendation(financials['symbol'], recommendation, explanation, sentiment)
    
    return recommendation, explanation

# Log Activity
def log_activity(username, action, details=""):
    logs_collection = db.system_logs
    log_entry = {
        "username": username,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow()
    }
    logs_collection.insert_one(log_entry)

def get_all_logs():
    logs_collection = db.system_logs
    logs = list(logs_collection.find().sort("timestamp", -1))
    return logs

def get_logs_by_type(log_type):
    logs_collection = db.system_logs
    logs = list(logs_collection.find({"action": {"$regex": log_type, "$options": "i"}}).sort("timestamp", -1))
    for log in logs:
        log['_id'] = str(log['_id'])
    return logs

# User Preferences
def get_user_preferences(username):
    preferences_collection = db.user_preferences
    preferences = preferences_collection.find_one({"user_id": username})
    if preferences:
        preferences['_id'] = str(preferences['_id'])
    return preferences

def update_user_preferences(username, key, value):
    preferences_collection = db.user_preferences
    preferences = preferences_collection.find_one({"user_id": username})
    if not preferences:
        preferences = {"user_id": username, "theme": "light", "language": "en"}
    
    preferences[key] = value
    preferences_collection.update_one(
        {"user_id": username},
        {"$set": preferences},
        upsert=True
    )
    log_activity(username, 'update_preferences', f"Updated {key} to {value}")

# Validation
def validate_user(username, password):
    user = db.users.find_one({"username": username, "password": password})
    if user:
        log_activity(username, 'login', "User logged in")
    return user

# Alerts
def add_alert(username, ticker_symbol, condition, price):
    alerts_collection = db.alerts
    alert = {
        "username": username,
        "ticker_symbol": ticker_symbol,
        "condition": condition,
        "price": price
    }
    alerts_collection.update_one(
        {"username": username, "ticker_symbol": ticker_symbol},
        {"$set": alert},
        upsert=True
    )
    log_activity(username, 'add_alert', f"Added alert for {ticker_symbol} at ${price} {condition}")

def get_user_alerts(username):
    try:
        alerts_collection = db.alerts
        alerts = list(alerts_collection.find({"username": username}))
        
        for alert in alerts:
            if '_id' in alert:
                alert['_id'] = str(alert['_id'])
        
        print(f"Fetched alerts for {username}: {alerts}")
        return alerts
    except Exception as e:
        print(f"Error in get_user_alerts: {e}")
        raise

def remove_alert(username, ticker_symbol):
    alerts_collection = db.alerts
    alerts_collection.delete_one({"username": username, "ticker_symbol": ticker_symbol})
    log_activity(username, 'remove_alert', f"Removed alert for {ticker_symbol}")

def check_alerts_real_time(socketio):
    while True:
        alerts_collection = db.alerts
        alerts = list(alerts_collection.find())
        
        for alert in alerts:
            if 'ticker_symbol' in alert:
                ticker = yf.Ticker(alert['ticker_symbol'])
                current_price = ticker.history(period='1d')['Close'].iloc[-1]
                condition = alert['condition']
                price = alert['price']
                
                if (condition == "above" and current_price > price) or (condition == "below" and current_price < price):
                    message = f"Alert: {alert['ticker_symbol']} has {condition} {price}. Current price is {current_price}."
                    socketio.emit('price_alert', {
                        'message': message,
                        'ticker': alert['ticker_symbol'],
                        'condition': condition,
                        'price': price,
                        'current_price': current_price
                    })
                    alerts_collection.delete_one({"_id": ObjectId(alert['_id'])})
                    log_activity(alert['username'], 'alert_triggered', f"Alert for {alert['ticker_symbol']} triggered at ${current_price} ({condition})")
        
        time.sleep(300)  # Check every 5 minutes

def check_alerts_simulated(socketio, ticker_symbol, simulated_price):
    alerts_collection = db.alerts
    alerts = list(alerts_collection.find({"ticker_symbol": ticker_symbol}))

    for alert in alerts:
        condition = alert['condition']
        price = alert['price']
        if (condition == "above" and simulated_price > price) or (condition == "below" and simulated_price < price):
            message = f"Simulated Alert: {ticker_symbol} has {condition} {price}. Simulated price is {simulated_price}."
            socketio.emit('price_alert', {
                'message': message,
                'ticker': ticker_symbol,
                'condition': condition,
                'price': price,
                'current_price': simulated_price
            })
            alerts_collection.delete_one({"_id": ObjectId(alert['_id'])})
            log_activity(alert['username'], 'alert_triggered', f"Simulated alert for {ticker_symbol} triggered at ${simulated_price} ({condition})")

def simulate_data_changes(socketio, ticker_symbol):
    simulated_price = random.uniform(75, 76)
    check_alerts_simulated(socketio, ticker_symbol, simulated_price)
    return simulated_price

# Start the real-time check in a separate thread
threading.Thread(target=check_alerts_real_time, args=(socketio,), daemon=True).start()