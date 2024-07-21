import yfinance as yf
import requests

# Your FMP API Key
FMP_API_KEY = '9VUF5Z7WDZY0enSfvMdorG7tncFDEKTQ'

def fetch_from_yahoo_finance(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    data = {
        'market_price': info.get('last_price', 'N/A'),
        'eps': info.get('earningsPerShare', 'N/A'),
        'forward_pe': info.get('forwardEps', 'N/A'),
        'growth_rate': 'N/A',  # Yahoo Finance does not directly provide this
        'net_income': info.get('netIncomeToCommon', 'N/A'),
        'shareholders_equity': info.get('totalStockholderEquity', 'N/A'),
        'total_liabilities': info.get('totalLiabilitiesNetMinorityInterest', 'N/A'),
        'cash_flow': info.get('totalCashFromOperatingActivities', 'N/A'),
        'revenue': info.get('totalRevenue', 'N/A'),
        'profit_margin': info.get('profitMargins', 'N/A'),
        'symbol': symbol
    }
    return data

def fetch_from_fmp(symbol):
    url = f'https://financialmodelingprep.com/api/v3/ratios/{symbol}?apikey={FMP_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            ratios = data[0]
            eps = ratios.get('earningsPerShare', 'N/A')
            stock_price = ratios.get('stockPrice', 'N/A')  # Ensure this is provided or available
            
            # Calculate Forward PE if both EPS and stock price are available
            forward_pe = eps if stock_price == 'N/A' else stock_price / eps
            
            return {
                'market_price': stock_price,
                'eps': eps,
                'forward_pe': forward_pe,
                'growth_rate': 'N/A',
                'net_income': ratios.get('netIncome', 'N/A'),
                'shareholders_equity': 'N/A',
                'total_liabilities': 'N/A',
                'cash_flow': 'N/A',
                'revenue': 'N/A',
                'profit_margin': ratios.get('netProfitMargin', 'N/A'),
                'symbol': symbol
            }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FMP: {e}")
    return None

def main():
    symbol = input("Enter the company symbol (e.g., NVDA, AAPL): ").upper()
    yahoo_data = fetch_from_yahoo_finance(symbol)
    fmp_data = fetch_from_fmp(symbol)
    
    print("\nYahoo Finance Data:")
    for key, value in yahoo_data.items():
        print(f"{key}: {value}")
    
    print("\nFMP Data:")
    if fmp_data:
        for key, value in fmp_data.items():
            print(f"{key}: {value}")
    else:
        print("No data found from FMP.")

if __name__ == "__main__":
    main()
