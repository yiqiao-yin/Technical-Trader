import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
from scipy.stats import norm


def calculate_macd(
    data: pd.DataFrame,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
) -> pd.DataFrame:
    """
    Calculate the Moving Average Convergence Divergence (MACD) and Signal line indicators.

    Parameters:
        data (pd.DataFrame): The dataframe containing stock price information.
        short_window (int): The number of periods for the shorter exponential moving average (EMA).
                            Default is 12.
        long_window (int): The number of periods for the longer EMA. Default is 26.
        signal_window (int): The number of periods for the signal line EMA. Default is 9.

    Returns:
        pd.DataFrame: The input Dataframe with additional columns 'MACD' and 'Signal_Line'
                      which contains the computed MACD values and signal line values respectively.

    Note: The function assumes that the input DataFrame contains a 'Close' column from which it computes the EMAs.
    """
    # Calculate the Short term Exponential Moving Average
    short_ema = data.Close.ewm(span=short_window, adjust=False).mean()

    # Calculate the Long term Exponential Moving Average
    long_ema = data.Close.ewm(span=long_window, adjust=False).mean()

    # Compute MACD (short EMA - long EMA)
    data["MACD"] = short_ema - long_ema

    # Compute Signal Line (EMA of MACD)
    data["Signal_Line"] = data.MACD.ewm(span=signal_window, adjust=False).mean()

    return data


def calculate_normalized_macd(
    data: pd.DataFrame,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
) -> pd.DataFrame:
    """
    Calculate the normalized Moving Average Convergence Divergence (MACD) and Signal line.

    The MACD is a trend-following momentum indicator that shows the relationship between
    two moving averages of a security's price. The MACD is calculated by subtracting the
    long-term exponential moving average (EMA) from the short-term EMA. A nine-day EMA of
    the MACD called the "Signal Line," is then plotted on top of the MACD, functioning as
    a trigger for buy and sell signals.

    This function adds a normalization step to the typical MACD calculation by standardizing
    the values using z-scores.

    Parameters:
        data (pd.DataFrame): The dataframe containing stock price information with a 'Close' column.
        short_window (int): The number of periods for the shorter EMA. Default is 12.
        long_window (int): The number of periods for the longer EMA. Default is 26.
        signal_window (int): The number of periods for the signal line EMA. Default is 9.

    Returns:
        pd.DataFrame: The input Dataframe is returned with additional columns 'MACD' and 'Signal_Line',
                      which contains the computed normalized MACD and signal line values respectively.
    """
    # Calculate the Short term Exponential Moving Average
    short_ema = data.Close.ewm(span=short_window, adjust=False).mean()

    # Calculate the Long term Exponential Moving Average
    long_ema = data.Close.ewm(span=long_window, adjust=False).mean()

    # Compute MACD (short EMA - long EMA)
    data["MACD"] = short_ema - long_ema

    # Compute Signal Line (EMA of MACD)
    data["Signal_Line"] = data.MACD.ewm(span=signal_window, adjust=False).mean()

    # Normalize the 'MACD' column using z-score normalization
    data["MACD"] = (data["MACD"] - data["MACD"].mean()) / data["MACD"].std()

    # Normalize the 'Signal_Line' column using z-score normalization
    data["Signal_Line"] = (data["Signal_Line"] - data["Signal_Line"].mean()) / data[
        "Signal_Line"
    ].std()

    return data


def calculate_percentile_macd(
    data: pd.DataFrame,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
) -> pd.DataFrame:
    """
    Calculate the percentile-based Moving Average Convergence Divergence (MACD) and Signal line.

    This function computes the MACD by subtracting the long-term exponential moving average (EMA)
    from the short-term EMA. It then calculates the Signal Line, which is a smoothing of the MACD
    values. After normalization using z-scores, the normalized MACD and Signal Line values are converted
    to percentiles, which are then rescaled to range from -100% to +100%.

    Parameters:
        data (pd.DataFrame): The dataframe containing stock price information with a 'Close' column.
        short_window (int): The number of periods for the shorter EMA. Default is 12.
        long_window (int): The number of periods for the longer EMA. Default is 26.
        signal_window (int): The number of periods for the signal line EMA. Default is 9.

    Returns:
        pd.DataFrame: The input Dataframe with additional columns 'MACD' and 'Signal_Line', representing
                      the rescaled percentile values of the corresponding MACD and signal line calculations.
    """
    # Calculate the Short term Exponential Moving Average
    short_ema = data.Close.ewm(span=short_window, adjust=False).mean()

    # Calculate the Long term Exponential Moving Average
    long_ema = data.Close.ewm(span=long_window, adjust=False).mean()

    # Compute MACD (short EMA - long EMA)
    data["MACD"] = short_ema - long_ema

    # Compute Signal Line (EMA of MACD)
    data["Signal_Line"] = data.MACD.ewm(span=signal_window, adjust=False).mean()

    # Normalize the 'MACD' column using z-score normalization
    data["MACD"] = (data["MACD"] - data["MACD"].mean()) / data["MACD"].std()

    # Normalize the 'Signal_Line' column using z-score normalization
    data["Signal_Line"] = (data["Signal_Line"] - data["Signal_Line"].mean()) / data[
        "Signal_Line"
    ].std()

    # Convert normalized data to percentiles (CDF) and rescale to -100% to +100%
    # Rescaling allows comparing the relative position of the current value within the distribution
    data["MACD"] = norm.cdf(data["MACD"]) * 200 - 100
    data["Signal_Line"] = norm.cdf(data["Signal_Line"]) * 200 - 100

    return data


def find_crossovers(
    df: pd.DataFrame, bullish_threshold: float, bearish_threshold: float
) -> pd.DataFrame:
    """
    Identifies the bullish and bearish crossover points between MACD and Signal Line.

    This function checks where the MACD line crosses the Signal Line from below (bullish crossover)
    or from above (bearish crossover). It then marks these crossovers with a 1 for bullish or -1
    for bearish within a new column in the DataFrame called 'Crossover'.

    Parameters:
        df (pd.DataFrame): The dataframe containing the columns 'MACD' and 'Signal_Line'.
        bullish_threshold (float): The threshold above which a crossover is considered bullish.
        bearish_threshold (float): The threshold below which a crossover is considered bearish.

    Returns:
        pd.DataFrame: The input DataFrame with an additional 'Crossover' column indicating
                      the bullish (+1) and bearish (-1) crossovers.
    """

    # Initialize 'Crossover' column to zero, indicating no crossover by default
    df["Crossover"] = 0

    # Find bullish crossovers - when the MACD crosses the Signal Line from below
    # and the Signal Line is below the bullish threshold.
    crossover_indices = df.index[
        (df["MACD"] > df["Signal_Line"])
        & (df["MACD"].shift() < df["Signal_Line"].shift())
        & (df["Signal_Line"] < bullish_threshold)
    ]
    # Mark the bullish crossovers with 1 in the 'Crossover' column
    df.loc[crossover_indices, "Crossover"] = 1

    # Find bearish crossovers - when the MACD crosses the Signal Line from above
    # and the Signal Line is above the bearish threshold.
    crossover_indices = df.index[
        (df["MACD"] < df["Signal_Line"])
        & (df["MACD"].shift() > df["Signal_Line"].shift())
        & (df["Signal_Line"] > bearish_threshold)
    ]
    # Mark the bearish crossovers with -1 in the 'Crossover' column
    df.loc[crossover_indices, "Crossover"] = -1

    return df


def get_fundamentals(ticker: str) -> tuple(pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    Fetches the income statement, balance sheet, and cash flow statement for a given stock ticker.

    This function retrieves fundamental financial information about a stock using the yfinance library,
    which fetches this data from Yahoo Finance.

    Parameters:
        ticker (str): The stock symbol to query.

    Returns:
        tuple of pandas.DataFrame: A 3-tuple where the first element is an income statement DataFrame,
                                   the second is a balance sheet DataFrame, and the third
                                   is a cash flow statement DataFrame.
    """
    # Create a Ticker object which allows access to Yahoo finance's vast data source
    stock = yf.Ticker(ticker)

    # Fetching and returning annual income statement, balance sheet, and cashflow data
    return stock.income_stmt, stock.balance_sheet, stock.cashflow


def create_fig(data: pd.DataFrame, ticker: str) -> go.Figure:
    """
    Creates a Plotly graph object (figure) that includes a candlestick plot of the stock prices,
    moving averages and a MACD (Moving Average Convergence Divergence) chart for the given data.

    Parameters:
        data (pandas.DataFrame): The input data containing the stock price information.
                                 It must include 'Close', 'Open', 'High', 'Low' columns and
                                 'MACD', 'Signal_Line', 'Crossover' values calculated externally.
        ticker (str): The stock symbol used in subplot titles to indicate the stock being analyzed.

    Returns:
        plotly.graph_objs._figure.Figure: A figure object which includes the visualization of
                                          the stock prices with moving averages and a MACD chart.
    """

    # Calculate moving averages
    data["MA12"] = data["Close"].rolling(window=12).mean()
    data["MA26"] = data["Close"].rolling(window=26).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()
    data["MA200"] = data["Close"].rolling(window=200).mean()

    # Initialize figure with subplots
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=(f"{ticker} Candlestick", "MACD"),
        row_width=[0.2, 0.7],
    )

    # Add Candlestick trace
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

    # Add Moving Average traces
    for ma, color in zip(
        ["MA12", "MA26", "MA50", "MA200"], ["magenta", "cyan", "yellow", "black"]
    ):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[ma],
                line=dict(color=color, width=1.5),
                name=f"{ma} days MA",
            ),
            row=1,
            col=1,
        )

    # Add MACD and Signal Line traces
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

    # Add markers for Bullish and Bearish crossovers on MACD chart
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

    # Add markers for Bullish and Bearish crossovers on the Candlestick chart
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

    # Update layout configurations
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800,  # Define the height of the figure
    )

    return fig
