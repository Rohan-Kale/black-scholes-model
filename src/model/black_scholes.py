import yfinance as yf
import pandas as pd
import scipy.stats as stats
import numpy as np
import datetime as dt


def generate_greeks(ticker):
    # Get Ticker object and expires
    ticker = yf.Ticker(ticker)

    q = ticker.info.get("dividendYield")/100 or 0.0 # ensure some dividend specified (0 if no dividend for that option)

    # Current stock price
    S = ticker.history(period="5d")["Close"].iloc[-1]
    
    # 13-week T-bill ( risk-free rate )
    r = yf.Ticker("^IRX").history(period="5d")["Close"].iloc[-1] / 100

    expiration_dates = ticker.options
    first_expiry = expiration_dates[0]
    ticker_chain = ticker.option_chain(first_expiry)

    calls = ticker_chain.calls
    
    ''' Using a specific strike price and the atm IV for that strike price'''
    
    ### atm_call = calls.iloc[(calls["strike"]-S).abs().argmin()]       
    ### sigma = atm_call["impliedVolatility"]       # ATM volatility
    
    # K = atm_call["strike"]            !! atm strike price !!
    
    ''' User defined strike price and finding IV for that value'''
    K = float(input("What strike price would you like to us: "))
    
    idx = (calls["strike"] - K).abs().argmin()       # grab idx of closest strike to K
    K = calls.iloc[idx]["strike"] 
    sigma = calls.iloc[idx]["impliedVolatility"] / 100
    
    # Cap/floor IV for robustness
    if sigma < 0.05:
        sigma = 0.2  # 20% for deep ITM
    if sigma > 1.0:
        sigma = 0.5  # 50% for extreme OTM
    
    
    # Find first expiry strictly in the future
    now = dt.datetime.now()
    first_expiry = None
    for expiry in ticker.options:
        expiry_dt = dt.datetime.strptime(expiry, "%Y-%m-%d").replace(hour=16)
        if expiry_dt > now + dt.timedelta(hours=1):
            first_expiry = expiry
            break

    if first_expiry is None:
        raise ValueError("No valid future expirations")        
    
    expiry_dt = dt.datetime.strptime(first_expiry, "%Y-%m-%d").replace(hour=16)
    T = (expiry_dt - now).total_seconds() / (365.25 * 24 * 3600)
    
    print(f"S={S}, K={K}, T={T:.4f} yrs, r={r:.4f}, q={q:.4f}, sigma={sigma:.2f}")

    return [S, K, T, r, q, sigma]


def black_scholes(option_type, S, K, T, r, q, sigma):
    option_type = option_type.lower()
    d1 = (np.log(S/K) + (r - q + 0.5 * (sigma**2)) * T) / (sigma * np.sqrt(T))
    d2 = d1 - (sigma * np.sqrt(T))
    if option_type == "call":
        price = (S * np.exp(-1 * q * T) * stats.norm.cdf(d1)) - (K * np.exp(-1 * r * T) * stats.norm.cdf(d2))
    elif option_type == "put":
        price = (K * np.exp(-1 * r * T) * stats.norm.cdf(-1*d2)) - (S * np.exp(-1 * q * T) * stats.norm.cdf(-1*d1)) 
    else:
        raise ValueError("please enter either put or call for option type")
    return price
    

if __name__ == "__main__":
    inp = input("Enter the ticker you would like to test the BSM model for: ")
    greeks = generate_greeks(inp)
    option_type = input("Would type of option would you like to use: ")
    print(greeks)
    price = black_scholes(option_type, *greeks)
    print(price)

