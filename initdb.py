from pymongo import MongoClient

def init_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client.stock_data
    
    # Define collections and their schemas
    collections = [
        {
            "name": "users",
            "schema": {
                "username": "string",
                "password": "string",
                "email": "string",
                "created_at": "date",
                "updated_at": "date",
                "preferences": {
                    "theme": "string",
                    "default_chart_type": "string"
                }
            }
        },
        {
            "name": "stocks",
            "schema": {
                "symbol": "string",
                "name": "string",
                "sector": "string",
                "exchange": "string",
                "history": [
                    {
                        "Date": "date",
                        "Open": "float",
                        "High": "float",
                        "Low": "float",
                        "Close": "float",
                        "Volume": "int"
                    }
                ]
            }
        },
        {
            "name": "recommendations",
            "schema": {
                "symbol": "string",
                "recommendation": "string",
                "explanation": "string",
                "date": "date"
            }
        },
        {
            "name": "visualization_data",
            "schema": {
                "symbol": "string",
                "data_type": "string",
                "data": {
                    "script": "string",
                    "div": "string",
                    "cdn_js": "string",
                    "cdn_css": "string"
                }
            }
        },
        {
            "name": "user_preferences",
            "schema": {
                "user_id": "string",
                "theme": "string",
                "language": "string",
                "default_chart_type": "string"
            }
        },
        {
            "name": "sessions",
            "schema": {
                "session_id": "string",
                "user_id": "string",
                "login_timestamp": "date",
                "logout_timestamp": "date",
                "ip_address": "string"
            }
        },
        {
            "name": "system_logs",
            "schema": {
                "timestamp": "date",
                "message": "string",
                "severity": "string",
                "user_id": "string",
                "session_id": "string"
            }
        },
        {
            "name": "alerts",
            "schema": {
                "user_id": "string",
                "symbol": "string",
                "condition": "string",
                "threshold": "float",
                "created_at": "date",
                "active": "boolean"
            }
        }
    ]
    
# Create collections and indexes
    for collection_info in collections:
        collection_name = collection_info['name']
        schema = collection_info['schema']
        
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Collection '{collection_name}' created.")
            
            # Create indexes if needed
            if collection_name == "users":
                db.users.create_index([("username", 1)], unique=True)
                db.users.create_index([("email", 1)], unique=True)
            elif collection_name == "stocks":
                db.stocks.create_index([("symbol", 1)], unique=True)
            # Add more indexes as per your application needs
            
            # Insert initial data if needed (example)
            # Note: No data insertion in initdb.py, only collection creation

        else:
            print(f"Collection '{collection_name}' already exists.")

if __name__ == "__main__":
    init_database()