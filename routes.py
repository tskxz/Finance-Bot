from flask import render_template, request, redirect, session, url_for, flash, jsonify
from flask_socketio import SocketIO, emit
from operations import fetch_and_store_data, get_recommendation, create_detailed_plot, validate_user, add_alert, get_user_alerts, remove_alert
from operations import db

def init_routes(app, socketio):
    @app.route('/')
    def index():
        if 'username' not in session or session['username'] != 'admin':
            flash('Access denied: You do not have permission to access this page.', 'error')
            return redirect(url_for('login'))
        
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = validate_user(username, password)
            if user:
                session['username'] = user['username']
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect(url_for('login'))

    @app.route('/fetch', methods=['POST'])
    def fetch():
        if 'username' not in session:
            return redirect(url_for('login'))
        ticker_symbol = request.form['ticker']
        fetch_and_store_data(ticker_symbol)
        socketio.emit('update_stock', {'ticker': ticker_symbol})
        return redirect('/show?ticker=' + ticker_symbol)

    @app.route('/show')
    def show():
        if 'username' not in session:
            return redirect(url_for('login'))
        ticker_symbol = request.args.get('ticker')
        stock_data = db.stocks.find_one({"symbol": ticker_symbol})
        
        if stock_data:
            data = stock_data['history']
            recommendation, explanation = get_recommendation(data)
            plot_script, plot_div, cdn_css, cdn_js = create_detailed_plot(data)
            firm_name = stock_data.get('name', 'Unknown Firm') 
            return render_template('index.html', data=data, recommendation=recommendation, explanation=explanation,
            plot_script=plot_script, plot_div=plot_div, firm_name=firm_name, ticker=ticker_symbol, cdn_css=cdn_css, cdn_js=cdn_js)
        else:
            return f"Data not found for {ticker_symbol}!"

    @app.route('/alerts', methods=['GET', 'POST'])
    def alerts():
        if 'username' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            ticker_symbol = request.form['ticker']
            condition = request.form['condition']
            price = float(request.form['price'])
            add_alert(session['username'], ticker_symbol, condition, price)
            flash(f"Alert set for {ticker_symbol}: {condition} ${price}", 'success')
            socketio.emit('new_alert', {'ticker': ticker_symbol, 'condition': condition, 'price': price})

        alerts = get_user_alerts(session['username'])
        return render_template('alerts.html', alerts=alerts)

    @app.route('/remove_alert/<ticker_symbol>', methods=['POST'])
    def remove_alert_route(ticker_symbol):
        if 'username' not in session:
            return redirect(url_for('login'))

        remove_alert(session['username'], ticker_symbol)
        flash(f"Alert removed for {ticker_symbol}", 'info')
        socketio.emit('remove_alert', {'ticker': ticker_symbol})
        return redirect(url_for('alerts'))
    
    @app.route('/get_alerts')
    def get_alerts():
        if 'username' not in session:
            return redirect(url_for('login'))

        alerts = get_user_alerts(session['username'])
        return jsonify({'alerts': alerts})

    @app.before_request
    def before_request():
        allowed_routes = ['login']
        if 'username' not in session and request.endpoint not in allowed_routes:
            return redirect(url_for('login'))
        

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')