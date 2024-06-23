from flask import Flask
from routes import init_routes
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Add a secret key for session management

if __name__ == '__main__':
    # Function to initialize database (runs initdb.py)
    def initialize_database():
        try:
            subprocess.run(['python', 'initdb.py'], check=True)
            print("Database initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Database initialization failed: {e}")

    # Initialize database when app starts
    initialize_database()
    
    # Import and initialize routes
    init_routes(app)
    
    app.run(debug=True)
