import yfinance as yf
import pandas as pd
import datetime as dt

def get_stock_price(ticker):
    S = ticker.history(period="1mo")["Close"].iloc[-1]
    return S

def get_risk_free_rate():
    r = yf.Ticker("^IRX").history(period="1mo")["Close"].iloc[-1] / 100
    return r

def get_call_data(ticker):
    expiration_dates = ticker.options
    first_expiry = expiration_dates[0]
    ticker_chain = ticker.option_chain(first_expiry)

    calls = ticker_chain.calls
    return calls

def get_strike_price(calls):
    K = float(input("What strike price would you like to us: "))
    idx = (calls["strike"] - K).abs().argmin()              #grab idx of closest strike to K
    K = calls.iloc[idx]["strike"] 
    
    return K

def get_volatility(calls, strike_price):
    idx = (calls["strike"] - strike_price).abs().argmin()   
    sigma = calls.iloc[idx]["impliedVolatility"] / 100
    
    return sigma

def get_dividend_yield(ticker):
    q = ticker.info.get("dividendYield")/100 or 0.0          #ensure some dividend specified (0 if no dividend for that option)
    if q < 0.01:
        q = 0.0
    
    return q

def find_expiry(ticker):
    now = dt.datetime.now()
    
    # find the next valid expiry date
    first_expiry = None
    for expiry in ticker.options:
        expiry_dt = dt.datetime.strptime(expiry, "%Y-%m-%d").replace(hour=16)
        if expiry_dt > now + dt.timedelta(days=30):
            first_expiry = expiry
            break
    
    if first_expiry is None:
        raise ValueError("No valid future expirations")        
    
    expiry_dt = dt.datetime.strptime(first_expiry, "%Y-%m-%d").replace(hour=16)     
    T = (expiry_dt - now).total_seconds() / (365.25 * 24 * 3600)
    
    return T