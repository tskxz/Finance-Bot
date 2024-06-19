# Personal Financial Project

This project aims to create a web application for financial data analysis using Flask, MongoDB, and Bokeh. The application connects to Yahoo Finance to retrieve historical stock data, stores this data in MongoDB (a NoSQL database), and displays graphical visualizations of this data along with buy, sell, or hold recommendations based on simple moving averages.

## Features

1. **Connection to Yahoo Finance:**
- The application connects to the Yahoo Finance API to retrieve historical stock data based on the user-provided symbol.

2. **Storage in MongoDB:**
- The data retrieved from Yahoo Finance is stored in MongoDB. Each stock is stored as a document in the `stocks` collection in the `stock_data` database.

3. **Investment Analysis and Recommendation:**
- Based on the historical stock data, the application calculates 20-day and 50-day moving averages.
- A "Buy" recommendation is made if the 20-day moving average is above the 50-day moving average.
- A "Sell" recommendation is made if the 20-day moving average is below the 50-day moving average.
- A "Hold" recommendation is made if the moving averages do not show a clear pattern.

4. **Graphical Visualization with Bokeh:**
- Uses the Bokeh library to create interactive charts of stock closing prices and their moving averages.
- The charts are embedded in the web page for easy viewing and understanding of the data.

## Prerequisites

To run this application locally, you need to have Python installed along with the libraries specified in the `requirements.txt` file. Additionally, a MongoDB server must be running on the local machine or on an accessible remote machine.

## Installation and Execution

1. **Clone the repository:**
git clone https://github.com/Dark1nessss/Finance-Bot
cd Finance-Bot

2. **Install the dependencies:**
pip install -r requirements.txt

3. **Configure MongoDB:**
- Ensure that the MongoDB server is running.

4. **Run the application:**
python app.py

5. **Access the application:**
- Open the browser and go to `http://localhost:5000`.

## Usage

1. **Fetch stock data:**
- On the homepage, enter the symbol of a stock (e.g., AAPL for Apple) and click on "Fetch Data".
- This will fetch the latest stock data from Yahoo Finance and store it in MongoDB.

2. **View data and recommendation:**
- After fetching the data, you can click on "Show Data" to view the historical stock data, a chart with moving averages, and an investment recommendation.

## Bibliography

- **Flask:** Web framework that helps interact with HTML using Python.
  - [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)

- **Bokeh:** Helps with the creation of images/charts and much more.
  - [Bokeh Documentation](https://docs.bokeh.org/en/latest/index.html)

- **pymongo**: Framework that facilitates the connection between Python and MongoDB.
  - [pymongo Documentation](https://pymongo.readthedocs.io/en/stable/)

- **yfinance**: Yahoo Finance API to assist with bots and more.
  - [yfinance GitHub Repository](https://github.com/ranaroussi/yfinance)

- **pandas**: Data manipulation and analysis library.
  - [pandas Documentation](https://pandas.pydata.org/docs/)

- **datetime**: Library for date manipulation in Python.
  - [datetime Documentation](https://docs.python.org/3/library/datetime.html)