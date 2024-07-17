from flask import render_template, request, redirect, session, url_for, flash, jsonify
from flask_socketio import emit
from operations import fetch_and_store_data, get_recommendation, validate_user, add_alert, get_user_alerts, remove_alert, simulate_data_changes, check_alerts_real_time, get_logs_by_type, log_activity, get_all_logs, get_user_preferences, update_user_preferences, load_language_file, fetch_and_store_news, get_news_by_symbol, fetch_sentiment_data
from operations import db
import threading

# Init
def init_routes(app, socketio):
    @app.route('/')
    def index():
        if 'username' not in session:
            flash('Acesso negado: Não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('login'))
        
        return render_template('index.html')

# End Init

# Login system
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = validate_user(username, password)
            if user:
                session['username'] = user['username']
                session['is_admin'] = user.get('is_admin', False)
                log_activity(username, 'login', "User logged in")
                return redirect(url_for('index'))
            else:
                flash('Nome de utilizador ou palavra-passe incorretos', 'danger')
        return render_template('login.html')

# End Login System

# Logout System
    @app.route('/logout')
    def logout():
        if 'username' in session:
            log_activity(session['username'], 'logout', "User logged out")
        session.pop('username', None)
        session.pop('is_admin', None)
        return redirect(url_for('login'))

# End Logout System

# Fetch System

    @app.route('/fetch', methods=['POST'])
    def fetch():
        if 'username' not in session:
            return redirect(url_for('login'))
        ticker_symbol = request.form['ticker']
        fetch_and_store_data(ticker_symbol)
        fetch_and_store_news(ticker_symbol)
        socketio.emit('update_stock', {'ticker': ticker_symbol})
        return redirect('/show?ticker=' + ticker_symbol)

# End Fetch System

# Show system after Fetch

    @app.route('/show')
    def show():
        if 'username' not in session:
            return redirect(url_for('login'))
        ticker_symbol = request.args.get('ticker')
        stock_data = db.stocks.find_one({"symbol": ticker_symbol})
        
        if stock_data:
            data = stock_data['history']
            financials = stock_data.get('financials', {})
            industry = stock_data.get('sector', 'Unknown')
            sentiment = fetch_sentiment_data(ticker_symbol)  # Fetch sentiment data
            recommendation, explanation = get_recommendation(data, financials, sentiment, industry)
            firm_name = stock_data.get('name', 'Unknown Firm') 
            
            # Fetch and store news
            fetch_and_store_news(ticker_symbol)
            news_articles = get_news_by_symbol(ticker_symbol)
            
            return render_template('index.html', data=data, recommendation=recommendation, explanation=explanation,
                                firm_name=firm_name, ticker=ticker_symbol, sentiment=sentiment,
                                news_articles=news_articles)
        else:
            return f"Dados não encontrados para {ticker_symbol}!"

# End Fetch System

# Alert System
    @app.route('/alerts', methods=['GET', 'POST'])
    def alerts():
        if 'username' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            ticker_symbol = request.form['ticker']
            condition = request.form['condition']
            price = float(request.form['price'])
            add_alert(session['username'], ticker_symbol, condition, price)
            log_activity(session['username'], 'alert', f"Alert set for {ticker_symbol} at ${price} ({condition})")
            flash(f"Alerta definido para {ticker_symbol}: {condition} ${price}", 'success')
            socketio.emit('new_alert', {'ticker': ticker_symbol, 'condition': condition, 'price': price})

        alerts = get_user_alerts(session['username'])
        return render_template('alerts.html', alerts=alerts)

    @app.route('/remove_alert/<ticker_symbol>', methods=['POST'])
    def remove_alert_route(ticker_symbol):
        if 'username' not in session:
            return redirect(url_for('login'))

        remove_alert(session['username'], ticker_symbol)
        log_activity(session['username'], 'alert', f"Alert removed for {ticker_symbol}")
        flash(f"Alerta removido para {ticker_symbol}", 'info')
        socketio.emit('remove_alert', {'ticker': ticker_symbol})
        return redirect(url_for('alerts'))

    @app.route('/get_alerts')
    def get_alerts():
        if 'username' not in session:
            return redirect(url_for('login'))

        try:
            alerts = get_user_alerts(session['username'])
            print(f"Alertas para o utilizador {session['username']}: {alerts}")
            return jsonify({'alerts': alerts})
        except Exception as e:
            print(f"Erro ao buscar alertas: {e}")
            return jsonify({'error': str(e)}), 500

# End Alert System

# Log System

    @app.route('/logs')
    def logs():
        if 'username' not in session:
            return redirect(url_for('login'))

        preferences = get_user_preferences(session['username'])
        theme = preferences['theme'] if preferences else 'light'
        language = preferences['language'] if preferences else 'en'
        language_strings = load_language_file(language)

        return render_template('logs.html', logs=get_all_logs(), theme=theme, language=language, lang_strings=language_strings)


    @app.route('/get_logs/<log_type>')
    def get_logs(log_type):
        if 'username' not in session:
            return redirect(url_for('login'))

        try:
            logs = get_logs_by_type(log_type)
            return jsonify({'logs': logs})
        except Exception as e:
            print(f"Erro ao buscar logs: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/change_theme/<theme>', methods=['POST'])
    def change_theme(theme):
        if 'username' in session:
            update_user_preferences(session['username'], 'theme', theme)
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error'}), 401

    @app.route('/change_language/<lang>', methods=['POST'])
    def change_language(lang):
        if 'username' in session:
            update_user_preferences(session['username'], 'language', lang)
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error'}), 401

# End Log System

# Request username for connection

    @app.before_request
    def before_request():
        allowed_routes = ['get_users', 'login', 'get_logs', 'change_theme', 'change_language']
        if 'username' not in session and request.endpoint not in allowed_routes:
            return redirect(url_for('login'))

    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')

# End Request username for connection

# Start Simulation Alert

    @app.route('/simulate_alert', methods=['POST'])
    def simulate_alert():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        ticker_symbol = request.form['ticker']
        simulated_price = simulate_data_changes(socketio, ticker_symbol)
        log_activity(session['username'], 'simulate_alert', f"Simulated alert for {ticker_symbol} at ${simulated_price:.2f}")
        flash(f"Preço simulado para {ticker_symbol}: ${simulated_price:.2f}", 'info')
        return redirect(url_for('alerts'))

# End Simulation Alert

    threading.Thread(target=check_alerts_real_time, args=(socketio,), daemon=True).start()