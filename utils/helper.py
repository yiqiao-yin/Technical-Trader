import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
from scipy.stats import norm


# Function to calculate MACD and Signal line
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.Close.ewm(span=short_window, adjust=False).mean()
    long_ema = data.Close.ewm(span=long_window, adjust=False).mean()
    data["MACD"] = short_ema - long_ema
    data["Signal_Line"] = data.MACD.ewm(span=signal_window, adjust=False).mean()
    return data


# Function to calculate MACD and Signal line (normalized)
def calculate_normalized_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.Close.ewm(span=short_window, adjust=False).mean()
    long_ema = data.Close.ewm(span=long_window, adjust=False).mean()
    data["MACD"] = short_ema - long_ema
    data["Signal_Line"] = data.MACD.ewm(span=signal_window, adjust=False).mean()

    # Normalize the 'MACD' column
    data["MACD"] = (data["MACD"] - data["MACD"].mean()) / data["MACD"].std()

    # Normalize the 'Signal_Line' column
    data["Signal_Line"] = (data["Signal_Line"] - data["Signal_Line"].mean()) / data[
        "Signal_Line"
    ].std()

    return data


def calculate_percentile_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.Close.ewm(span=short_window, adjust=False).mean()
    long_ema = data.Close.ewm(span=long_window, adjust=False).mean()
    data["MACD"] = short_ema - long_ema
    data["Signal_Line"] = data.MACD.ewm(span=signal_window, adjust=False).mean()

    # Normalize the 'MACD' and 'Signal_Line' columns
    data["MACD"] = (data["MACD"] - data["MACD"].mean()) / data["MACD"].std()
    data["Signal_Line"] = (data["Signal_Line"] - data["Signal_Line"].mean()) / data[
        "Signal_Line"
    ].std()

    # Convert normalized data to percentiles (CDF) and rescale to -100% to +100%
    data["MACD"] = norm.cdf(data["MACD"]) * 200 - 100  # Rescale CDF values
    data["Signal_Line"] = (
        norm.cdf(data["Signal_Line"]) * 200 - 100
    )  # Rescale CDF values

    return data


# Function to find MACD crossover points
def find_crossovers(df, bullish_threshold, bearish_threshold):
    df["Crossover"] = 0  # Default no crossover
    # Find crossover points
    crossover_indices = df.index[
        (df["MACD"] > df["Signal_Line"])
        & (df["MACD"].shift() < df["Signal_Line"].shift())
        & (df["Signal_Line"] < bullish_threshold)
    ]
    df.loc[
        crossover_indices, "Crossover"
    ] = 1  # Mark green triangle for bullish crossover
    crossover_indices = df.index[
        (df["MACD"] < df["Signal_Line"])
        & (df["MACD"].shift() > df["Signal_Line"].shift())
        & (df["Signal_Line"] > bearish_threshold)
    ]
    df.loc[
        crossover_indices, "Crossover"
    ] = -1  # Mark red triangle for bearish crossover
    return df


# New function to get fundamentals data
def get_fundamentals(ticker):
    stock = yf.Ticker(ticker)

    # Fetching annual report data
    return stock.income_stmt, stock.balance_sheet, stock.cashflow


# Create figure object
def create_fig(data, ticker):
    # Calculate moving averages
    data['MA12'] = data['Close'].rolling(window=12).mean()
    data['MA26'] = data['Close'].rolling(window=26).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()

    # Plotting
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=(f"{ticker} Candlestick", "MACD"),
        row_width=[0.2, 0.7],
    )

    # Candlestick plot
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Candlestick",
        ),
        row=1,
        col=1,
    )

    # Add moving average traces
    for ma, color in zip(['MA12', 'MA26', 'MA50', 'MA200'], ['magenta', 'cyan', 'yellow', 'black']):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[ma],
                line=dict(color=color, width=1.5),
                name=f'{ma} days MA',
            ),
            row=1,
            col=1,
        )

    # MACD plot
    fig.add_trace(
        go.Scatter(
            x=data.index, y=data["MACD"], line=dict(color="blue", width=2), name="MACD"
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Signal_Line"],
            line=dict(color="orange", width=2),
            name="Signal Line",
        ),
        row=2,
        col=1,
    )

    # Marking crossovers
    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=data[data["Crossover"] == 1].index,
            y=data[data["Crossover"] == 1]["MACD"],
            marker_symbol="triangle-up",
            marker_color="green",
            marker_size=20,
            name="Bullish Crossover (MACD) ✅",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=data[data["Crossover"] == -1].index,
            y=data[data["Crossover"] == -1]["MACD"],
            marker_symbol="triangle-down",
            marker_color="red",
            marker_size=20,
            name="Bearish Crossover (MACD) 🈲",
        ),
        row=2,
        col=1,
    )

    # Marking crossovers on stock chart
    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=data[data["Crossover"] == 1].index,
            y=data[data["Crossover"] == 1]["Close"],
            marker_symbol="triangle-up",
            marker_color="green",
            marker_size=25,
            name="Bullish Crossover (Close) ✅",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=data[data["Crossover"] == -1].index,
            y=data[data["Crossover"] == -1]["Close"],
            marker_symbol="triangle-down",
            marker_color="red",
            marker_size=25,
            name="Bearish Crossover (Close) 🈲",
        ),
        row=1,
        col=1,
    )

    # Layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800,  # Set the height of the figure (in pixels)
    )

    return fig
