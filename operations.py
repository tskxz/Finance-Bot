import yfinance as yf
import pandas as pd
from pymongo import MongoClient
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.resources import CDN

client = MongoClient("mongodb://localhost:27017/")
db = client.stock_data

# Function to fetch and store data in MongoDB
def fetch_and_store_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="6mo")
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

    plot_height = 400 
    num_records = len(df)
    
    num_visible_points = 50
    if num_records > num_visible_points:
        start_index = num_records - num_visible_points
    else:
        start_index = 0
    
    p = figure(x_axis_type="datetime", title="Stock Price Movement", width=800, height=plot_height)
    p.line(df['Date'], df['Close'], color='navy', legend_label='Close Price')
    p.line(df['Date'], df['Close'].rolling(window=20).mean(), color='orange', legend_label='20-Day MA')
    p.line(df['Date'], df['Close'].rolling(window=50).mean(), color='green', legend_label='50-Day MA')
    
    tooltips = [
        ("Date", "@x{%F}"),
        ("Close", "@y{0.2f}")
    ]
    
    hover_tool = HoverTool(tooltips=tooltips, formatters={'@x': 'datetime'})
    p.add_tools(hover_tool)
    
    p.legend.location = "top_left"
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price (USD)"
    
    script, div = components(p)
    cdn_js = CDN.js_files[0] if CDN.js_files else None
    cdn_css = CDN.css_files[0] if CDN.css_files else None
    
    return script, div, cdn_css, cdn_js

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