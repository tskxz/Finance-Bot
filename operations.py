import yfinance as yf
import pandas as pd
from pymongo import MongoClient
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.resources import CDN
from flask_socketio import emit
import random

client = MongoClient("mongodb://localhost:27017/")
db = client.stock_data

# Function to fetch and store data in MongoDB
def fetch_and_store_data(ticker_symbol, period='6mo'):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)
    hist.reset_index(inplace=True)
    hist_dict = hist.to_dict(orient="records")
    
    company_name = ticker.info.get('shortName', 'Unknown Firm')
    
    # Store data in MongoDB
    stocks_collection = db.stocks
    stocks_collection.update_one(
        {"symbol": ticker_symbol},
        {"$set": {"history": hist_dict, "name": company_name}},
        upsert=True
    )

# Function to get recommendation based on data
def get_recommendation(data):
    df = pd.DataFrame(data)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    ma20_latest = df['MA20'].iloc[-1]
    ma50_latest = df['MA50'].iloc[-1]
    
    if ma20_latest > ma50_latest:
        recommendation = "Buy"
        explanation = f"The 20-day moving average ({ma20_latest:.2f}) is higher than the 50-day moving average ({ma50_latest:.2f}), indicating an upward trend."
    elif ma20_latest < ma50_latest:
        recommendation = "Sell"
        explanation = f"The 20-day moving average ({ma20_latest:.2f}) is lower than the 50-day moving average ({ma50_latest:.2f}), indicating a downward trend."
    else:
        recommendation = "Hold"
        explanation = f"The 20-day moving average ({ma20_latest:.2f}) is equal to the 50-day moving average ({ma50_latest:.2f}), indicating no significant trend."
    
    return recommendation, explanation

# Function to create detailed plot using Bokeh
def create_detailed_plot(data):
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    p = figure(x_axis_type="datetime", title="Stock Price Movement", width=800, height=400)
    source = ColumnDataSource(df)
    
    p.line('Date', 'Close', color='navy', legend_label='Close Price', source=source)
    p.line('Date', 'MA20', color='orange', legend_label='20-Day MA', source=source)
    p.line('Date', 'MA50', color='green', legend_label='50-Day MA', source=source)
    
    tooltips = [("Date", "@Date{%F}"), ("Close", "@Close{0.2f}")]
    
    hover_tool = HoverTool(tooltips=tooltips, formatters={'@Date': 'datetime'})
    p.add_tools(hover_tool)
    
    p.legend.location = "top_left"
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price (USD)"
    
    script, div = components(p)
    cdn_js = CDN.js_files[0] if CDN.js_files else None
    cdn_css = CDN.css_files[0] if CDN.css_files else None
    
    return script, div, cdn_js, cdn_css

# Function to validate user credentials
def validate_user(username, password):
    user = db.users.find_one({"username": username, "password": password})
    return user

# Function to add or update an alert
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

# Function to get alerts for a specific user
def get_user_alerts(username):
    alerts_collection = db.alerts
    alerts = list(alerts_collection.find({"username": username}))
    return alerts

# Function to remove an alert
def remove_alert(username, ticker_symbol):
    alerts_collection = db.alerts
    alerts_collection.delete_one({"username": username, "ticker_symbol": ticker_symbol})

# Function to check for triggered alerts based on simulated price changes
def check_alerts_simulated(socketio, ticker_symbol, simulated_price):
    alerts_collection = db.alerts
    alerts = list(alerts_collection.find({"ticker_symbol": ticker_symbol}))

    for alert in alerts:
        condition = alert['condition']
        price = alert['price']
        if (condition == "above" and simulated_price > price) or (condition == "below" and simulated_price < price):
            # Notify the user
            socketio.emit('price_alert', {
                'ticker': ticker_symbol,
                'condition': condition,
                'price': price,
                'current_price': simulated_price
            })

# Function to simulate data changes and check alerts
def simulate_data_changes(socketio, ticker_symbol):
    # Simulate a price for testing purposes
    simulated_price = random.uniform(75, 76)  # Change this range as needed
    check_alerts_simulated(socketio, ticker_symbol, simulated_price)
    return simulated_price