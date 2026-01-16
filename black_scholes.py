import yfinance as yf
import pandas as pd
import scipy.stats as stats
import numpy as np
import datetime as dt

# Get Ticker object and expires
aapl = yf.Ticker("AAPL")
S = aapl.history(period="1d")["Close"].iloc[-1]
r = yf.Ticker("^IRX").history(period="1d")["Close"].iloc[-1] / 100
aapl_option = aapl.options[0]
sigma = aapl.option_chain(aapl_option).calls["impliedVolatility"][0]

K = aapl.option_chain(aapl_option).calls["strike"][0]

expiration_dates = aapl.options
first_expiry = expiration_dates[0]
opt_chain = aapl.option_chain(first_expiry)

expiry_dt = dt.datetime.strptime(first_expiry, '%Y-%m-%d')
today = dt.datetime.now()
time_delta = expiry_dt - today

T = max(time_delta.days, 1) /365.25




def black_scholes(option_type, S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + (sigma**2)/2) * T) / (sigma*T)
    d2 = d1 - (sigma * np.sqrt(T))
    if option_type == "call":
        price = (S * stats.norm.cdf(d1)) - (K * (np.exp(-1 * r * T)) * stats.norm.cdf(d2))
    elif option_type == "put":
        price = (K * np.exp(-1 * r * T) * stats.norm.cdf(-1*d2)) - (S * stats.norm.cdf(-1*d1)) 
    else:
        raise ValueError("please enter either put or call for option type")
    return price
    

print(black_scholes("call", S, K, T, r, sigma))