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

5. **User Authentication:**
   - Implements a simple login system to restrict access to the application to authenticated users.

6. **Alerts:**
   - Users can set price alerts for specific stocks. When a stock reaches the specified price condition (above or below), the user is notified.

7. **Real-time Updates:**
   - Utilizes Socket.IO to provide real-time updates for stock data and alerts.

## Prerequisites

To run this application locally, you need to have Python installed along with the libraries specified in the `requirements.txt` file. Additionally, a MongoDB server must be running on the local machine or on an accessible remote machine.

## Installation and Execution

1. **Clone the repository:**
   ```sh
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

## Tools and Libraries

- **Flask:** Web framework that helps interact with HTML using Python.
  - [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)

- **Flask-SocketIO:** Adds support for real-time communication between the server and clients.
  - [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/en/latest/)

- **Bokeh:** Helps with the creation of images/charts and much more.
  - [Bokeh Documentation](https://docs.bokeh.org/en/latest/index.html)

- **pymongo:** Framework that facilitates the connection between Python and MongoDB.
  - [pymongo Documentation](https://pymongo.readthedocs.io/en/stable/)

- **yfinance:** Yahoo Finance API to assist with bots and more.
  - [yfinance GitHub Repository](https://github.com/ranaroussi/yfinance)

- **pandas:** Data manipulation and analysis library.
  - [pandas Documentation](https://pandas.pydata.org/docs/)

- **datetime:** Library for date manipulation in Python.
  - [datetime Documentation](https://docs.python.org/3/library/datetime.html)

- **SweetAlert:** Library for beautiful, responsive, customizable and accessible (WAI-ARIA) replacement for JavaScript's popup boxes.
  - [SweetAlert Documentation](https://sweetalert.js.org/)

## Alerts System

The application includes a feature where users can set alerts for specific stock prices. When the stock price crosses the set threshold, the user receives a notification.

### Setting Alerts

1. **Navigate to the Alerts Page:**
   - Use the navigation bar to go to the "Alerts" page.

2. **Set a New Alert:**
   - Enter the stock ticker symbol (e.g., AAPL for Apple).
   - Select the condition ("above" or "below").
   - Enter the target price for the alert.
   - Click "Set Alert".

### Viewing and Managing Alerts

- The alerts page displays all the alerts set by the user.
- Users can remove an alert by clicking the "Remove" button next to the respective alert.

### Real-Time Notifications

- The application uses WebSockets to provide real-time notifications when a stock reaches the alert threshold.
- Notifications appear as pop-ups on the top-right corner of the screen.

## Simulating Alerts

For testing purposes, the application includes a feature to simulate stock price changes and trigger alerts.

1. **Simulate a Price Change:**
   - Navigate to the Alerts page.
   - Enter the stock ticker symbol for which you want to simulate a price change.
   - Click the "Simulate Alert" button.
   - The application will generate a random stock price and check against the set alerts.
   - If the simulated price meets any alert conditions, a notification will be displayed.

## Code Structure

- `app.py`: The main application file that initializes the Flask app, sets up the database, and starts the server.
- `routes.py`: Defines the routes for the web application, including fetching stock data, displaying data, setting alerts, and handling user authentication.
- `operations.py`: Contains the core operations for fetching stock data from Yahoo Finance, storing data in MongoDB, generating recommendations, and handling alerts.
- `initdb.py`: Initializes the MongoDB database with the required collections and indexes.
- `insert_data.py`: Inserts initial data into the MongoDB database, including example users and stock data.
- `templates/`: Directory containing HTML templates for the web application.
- `static/`: Directory containing static files such as CSS and JavaScript.

## Future Enhancements

- **Enhanced Security:**
  - Implement password hashing for user authentication.
  - Add role-based access control to restrict certain features to admin users.

- **Advanced Data Analysis:**
  - Include additional technical indicators for more comprehensive investment analysis.
  - Implement machine learning models for stock price prediction.

- **User Interface Improvements:**
  - Enhance the design and usability of the web application.
  - Add more interactive and customizable charts.

- **Notifications:**
  - Implement email or SMS notifications for stock alerts.
  - Provide options for users to customize notification preferences.

## Contribution

Contributions are welcome! If you have any ideas for improvements or new features, please feel free to fork the repository and submit a pull request.