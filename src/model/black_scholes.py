import yfinance as yf
import pandas as pd
import scipy.stats as stats
import numpy as np
import datetime as dt
import sys
import os

# gain access to greek variables
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, src_dir)

from analytics import greek_variables as gv

def generate_greeks(ticker):
    # Get Ticker object and expires
    ticker = yf.Ticker(ticker)

    # Get dividend yield
    q = gv.get_dividend_yield(ticker)

    # Current stock price
    S = gv.get_stock_price(ticker)
    
    # 13-week T-bill ( risk-free rate )
    r = gv.get_risk_free_rate()

    # get closest matching strike price to user inp
    calls = gv.get_call_data(ticker)
    K = gv.get_strike_price(calls)
    
    # calculate volatility based on strike price + Cap/floor IV for robustness
    sigma = gv.get_volatility(calls, K)
    if sigma < 0.05:                                
        sigma = 0.2  # 20% for deep ITM
    if sigma > 1.0:
        sigma = 0.5  # 50% for extreme OTM                           
    
    
    # Find first expiry strictly in the future
    T = gv.find_expiry(ticker)
    

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

