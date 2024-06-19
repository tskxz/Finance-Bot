from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
import yfinance as yf
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.layouts import column
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.stock_data  # Database name

# Function to fetch and store data from Yahoo Finance
def fetch_and_store_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="1mo")
    hist.reset_index(inplace=True)
    hist_dict = hist.to_dict(orient="records")
    db.stocks.update_one(
        {"symbol": ticker_symbol},
        {"$set": {"history": hist_dict}},
        upsert=True
    )

# Simple buy/sell recommendation based on moving average
def get_recommendation(data):
    df = pd.DataFrame(data)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    ma20_latest = df['MA20'].iloc[-1]
    ma50_latest = df['MA50'].iloc[-1]
    close_latest = df['Close'].iloc[-1]

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

# Create Bokeh plot
def create_plot(data):
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    p = figure(x_axis_type="datetime", title="Stock Closing Prices", height=350, width=800)
    p.line(df['Date'], df['Close'], color='navy', legend_label='Close Price')
    p.line(df['Date'], df['Close'].rolling(window=20).mean(), color='orange', legend_label='20-Day MA')
    p.line(df['Date'], df['Close'].rolling(window=50).mean(), color='green', legend_label='50-Day MA')
    p.legend.location = "top_left"
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    return p

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    ticker_symbol = request.form['ticker']
    fetch_and_store_data(ticker_symbol)
    return redirect('/show?ticker=' + ticker_symbol)

@app.route('/show')
def show():
    ticker_symbol = request.args.get('ticker')
    stock_data = db.stocks.find_one({"symbol": ticker_symbol})
    if stock_data:
        data = stock_data['history']
        recommendation, explanation = get_recommendation(data)
        plot = create_plot(data)
        script, div = components(plot)
        cdn_js = CDN.js_files[0] if CDN.js_files else ''
        cdn_css = CDN.css_files[0] if CDN.css_files else ''
        return render_template('index.html', data=data, recommendation=recommendation, explanation=explanation, script=script, div=div, cdn_js=cdn_js, cdn_css=cdn_css)
    else:
        return f"No data found for {ticker_symbol}!"

if __name__ == '__main__':
    app.run(debug=True)
