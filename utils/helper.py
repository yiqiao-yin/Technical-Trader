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
def find_crossovers(df, bullish_threshold, bearish_threshold):
    df['Crossover'] = 0  # Default no crossover
    # Find crossover points
    crossover_indices = df.index[(df['MACD'] > df['Signal_Line']) & (df['MACD'].shift() < df['Signal_Line'].shift()) & (df['Signal_Line'] < bullish_threshold)]
    df.loc[crossover_indices, 'Crossover'] = 1  # Mark green triangle for bullish crossover
    crossover_indices = df.index[(df['MACD'] < df['Signal_Line']) & (df['MACD'].shift() > df['Signal_Line'].shift()) & (df['Signal_Line'] > bearish_threshold)]
    df.loc[crossover_indices, 'Crossover'] = -1  # Mark red triangle for bearish crossover
    return df

# New function to get fundamentals data
def get_fundamentals(ticker):
    stock = yf.Ticker(ticker)

    # Fetching annual report data
    return stock.income_stmt, stock.balance_sheet, stock.cashflow

# Create figure object
def create_fig(data, ticker):
    # Plotting
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, subplot_titles=(f'{ticker} Candlestick', 'MACD'), row_width=[0.2, 0.7])
    
    # Candlestick plot
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlestick'), row=1, col=1)
    
    # MACD plot
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], line=dict(color='blue', width=2), name='MACD'), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Signal_Line'], line=dict(color='orange', width=2), name='Signal Line'), row=2, col=1)
    
    # Marking crossovers
    fig.add_trace(go.Scatter(mode='markers', x=data[data['Crossover'] == 1].index, y=data[data['Crossover'] == 1]['MACD'], marker_symbol='triangle-up', marker_color='green', marker_size=20, name='Bullish Crossover (MACD) ✅'), row=2, col=1)
    fig.add_trace(go.Scatter(mode='markers', x=data[data['Crossover'] == -1].index, y=data[data['Crossover'] == -1]['MACD'], marker_symbol='triangle-down', marker_color='red', marker_size=20, name='Bearish Crossover (MACD) 🈲'), row=2, col=1)
    
    # Marking crossovers on stock chart
    fig.add_trace(go.Scatter(mode='markers', x=data[data['Crossover'] == 1].index, y=data[data['Crossover'] == 1]['Close'], marker_symbol='triangle-up', marker_color='green', marker_size=25, name='Bullish Crossover (Close) ✅'), row=1, col=1)
    fig.add_trace(go.Scatter(mode='markers', x=data[data['Crossover'] == -1].index, y=data[data['Crossover'] == -1]['Close'], marker_symbol='triangle-down', marker_color='red', marker_size=25, name='Bearish Crossover (Close) 🈲'), row=1, col=1)
    
    # Layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800  # Set the height of the figure (in pixels)
    )

    return fig
