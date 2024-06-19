from flask import Flask, render_template, request
from pymongo import MongoClient
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.stock_data

# Function to fetch and store data from Yahoo Finance
def fetch_and_store_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="1mo")
    db.stocks.update_one(
        {"symbol": ticker_symbol},
        {"$set": {"history": hist.to_dict(orient="records")}},
        upsert=True
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    ticker_symbol = request.form['ticker']
    fetch_and_store_data(ticker_symbol)
    return f"Data for {ticker_symbol} fetched and stored!"

@app.route('/show', methods=['POST'])
def show():
    ticker_symbol = request.form['ticker']
    stock_data = db.stocks.find_one({"symbol": ticker_symbol})
    if stock_data:
        return render_template('index.html', data=stock_data['history'])
    else:
        return f"No data found for {ticker_symbol}!"

if __name__ == '__main__':
    app.run(debug=True)