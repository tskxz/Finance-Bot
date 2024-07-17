from flask import Flask, jsonify, redirect, request, session, url_for, flash
from flask_socketio import SocketIO
from routes import init_routes
import subprocess
import os
from pymongo import MongoClient

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

# Conectando ao MongoDB
mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/your_database_name')
client = MongoClient(mongo_uri)
db = client.get_database()

@app.route('/users', methods=['GET'])
def get_users():
    users = list(db.users.find())
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
    return jsonify(users)

if __name__ == '__main__':
    def initialize_database():
        try:
            # Run initdb.py
            subprocess.run(['python', 'initdb.py'], check=True)
            print("Database initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Database initialization failed: {e}")

    initialize_database()
    init_routes(app, socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
