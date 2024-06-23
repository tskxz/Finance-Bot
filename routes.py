from flask import render_template, request, redirect, session, url_for, flash
from operations import fetch_and_store_data, get_recommendation, create_detailed_plot, validate_user
from operations import db 

def init_routes(app):
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
            plot_script, plot_div = create_detailed_plot(data)
            firm_name = stock_data.get('name', 'Unknown Firm') 
            return render_template('index.html', data=data, recommendation=recommendation, explanation=explanation,
            plot_script=plot_script, plot_div=plot_div, firm_name=firm_name, ticker=ticker_symbol)
        else:
            return f"Data not found for {ticker_symbol}!"

    @app.before_request
    def before_request():
        allowed_routes = ['login']
        if 'username' not in session and request.endpoint not in allowed_routes:
            return redirect(url_for('login'))
