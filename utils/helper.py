import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Function to calculate MACD and Signal line
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.Close.ewm(span=short_window, adjust=False).mean()
    long_ema = data.Close.ewm(span=long_window, adjust=False).mean()
    data['MACD'] = short_ema - long_ema
    data['Signal_Line'] = data.MACD.ewm(span=signal_window, adjust=False).mean()
    return data

# Function to find MACD crossover points
def find_crossovers(df):
    df['Crossover'] = 0  # Default no crossover
    # Find crossover points
    crossover_indices = df.index[(df['MACD'] > df['Signal_Line']) & (df['MACD'].shift() < df['Signal_Line'].shift())]
    df.loc[crossover_indices, 'Crossover'] = 1  # Mark green triangle for bullish crossover
    crossover_indices = df.index[(df['MACD'] < df['Signal_Line']) & (df['MACD'].shift() > df['Signal_Line'].shift())]
    df.loc[crossover_indices, 'Crossover'] = -1  # Mark red triangle for bearish crossover
    return df

# New function to get fundamentals data
def get_fundamentals(ticker):
    stock = yf.Ticker(ticker)

    # Fetching annual report data
    return stock.income_stmt, stock.balance_sheet, stock.cashflow
