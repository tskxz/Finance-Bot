import yfinance as yf

def fetch_from_yahoo_finance(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    # Extracting data
    data = {
        'market_price': info.get('currentPrice', 'N/A'),  # Check if last_price is available, otherwise use another field
        'eps': info.get('earningsPerShare', 'N/A'),
        'forward_pe': info.get('forwardEps', 'N/A'),
        'growth_rate': 'N/A',  # Yahoo Finance does not directly provide this
        'net_income': info.get('netIncome', 'N/A'),
        'shareholders_equity': info.get('totalStockholderEquity', 'N/A'),
        'total_liabilities': info.get('totalLiabilitiesNetMinorityInterest', 'N/A'),
        'cash_flow': info.get('totalCashFromOperatingActivities', 'N/A'),
        'revenue': info.get('totalRevenue', 'N/A'),
        'profit_margin': info.get('profitMargins', 'N/A'),
        'dividend_yield': info.get('dividendYield', 'N/A'),
        'pe_ratio': info.get('trailingPE', 'N/A'),
        'beta': info.get('beta', 'N/A'),
        'market_cap': info.get('marketCap', 'N/A'),
        'enterprise_value': info.get('enterpriseValue', 'N/A'),
        'price_to_book': info.get('priceToBook', 'N/A'),
        'quick_ratio': info.get('quickRatio', 'N/A'),
        'current_ratio': info.get('currentRatio', 'N/A'),
        'return_on_assets': info.get('returnOnAssets', 'N/A'),
        'return_on_equity': info.get('returnOnEquity', 'N/A'),
        'debt_to_equity': info.get('debtToEquity', 'N/A'),
        'symbol': symbol
    }
    
    # Additional calculations if needed
    # Example: Calculating forward PE if not available directly
    if data['forward_pe'] == 'N/A':
        eps = data.get('eps')
        market_price = data.get('market_price')
        if eps != 'N/A' and market_price != 'N/A':
            try:
                data['forward_pe'] = round(float(market_price) / float(eps), 2)
            except ZeroDivisionError:
                data['forward_pe'] = 'N/A'
    
    return data

def main():
    symbol = input("Enter the company symbol (e.g., NVDA, AAPL): ").upper()
    yahoo_data = fetch_from_yahoo_finance(symbol)
    
    print("\nYahoo Finance Data:")
    for key, value in yahoo_data.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
