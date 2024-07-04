from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.stock_data

def insert_initial_data():
    users = [
        {
            "username": "admin",
            "password": "admin123",
            "email": "admin@example.com",
            "created_at": None,
            "updated_at": None,
            "is_admin": True,
            "preferences": {
                "theme": "light",
                "default_chart_type": "line"
            }
        },
        {
            "username": "user",
            "password": "user456",
            "email": "user@example.com",
            "created_at": None,
            "updated_at": None,
            "is_admin": False,
            "preferences": {
                "theme": "dark",
                "default_chart_type": "bar"
            }
        }
    ]

    db.users.insert_many(users)
    print("Initial users inserted.")

    stocks = [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "exchange": "NASDAQ",
            "history": [
                {
                    "Date": "2023-01-01",
                    "Open": 140.0,
                    "High": 145.0,
                    "Low": 138.0,
                    "Close": 143.0,
                    "Volume": 1000000
                },
            ]
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "exchange": "NASDAQ",
            "history": [
                {
                    "Date": "2023-01-01",
                    "Open": 200.0,
                    "High": 205.0,
                    "Low": 198.0,
                    "Close": 203.0,
                    "Volume": 800000
                },
            ]
        }
    ]

    db.stocks.insert_many(stocks)
    print("Initial stocks data inserted.")

    recommendations = [
        {
            "symbol": "AAPL",
            "recommendation": "Buy",
            "explanation": "Strong performance and growth potential in the technology sector.",
            "date": None
        },
        {
            "symbol": "MSFT",
            "recommendation": "Hold",
            "explanation": "Stable performance, moderate growth expected.",
            "date": None
        }
    ]

    db.recommendations.insert_many(recommendations)
    print("Initial recommendations inserted.")

    user_preferences = [
        {
            "user_id": "admin",
            "theme": "dark",
            "language": "en",
            "default_chart_type": "line"
        },
        {
            "user_id": "user",
            "theme": "light",
            "language": "en",
            "default_chart_type": "bar"
        }
    ]

    db.user_preferences.insert_many(user_preferences)
    print("Initial user preferences inserted.")

    alerts = [
        {
            "user_id": "admin",
            "symbol": "AAPL",
            "condition": "price_drop",
            "threshold": 130.0,
            "created_at": None,
            "active": True
        },
        {
            "user_id": "user",
            "symbol": "MSFT",
            "condition": "price_rise",
            "threshold": 210.0,
            "created_at": None,
            "active": False
        }
    ]

    db.alerts.insert_many(alerts)
    print("Initial alerts inserted.")

if __name__ == "__main__":
    insert_initial_data()
