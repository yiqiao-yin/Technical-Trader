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
    fin_data_dict = stock.financial_data
    fin_data_df = pd.DataFrame.from_dict(fin_data_dict, orient="index").T
    return fin_data_df

# Streamlit app layout
st.title('MACD Trading Strategy Simulation')

# Sidebar inputs
ticker = st.sidebar.text_input('Enter Stock Ticker', 'AAPL').upper()
start_date = st.sidebar.date_input('Start Date', pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('End Date', pd.to_datetime('today'))

# Add sidebar slider for selecting two integers
short_window = st.sidebar.slider('Select short window size', min_value=2, max_value=100, value=12)
long_window = st.sidebar.slider('Select long window size', min_value=2, max_value=250, value=50)
signal_window = st.sidebar.slider('Select signal window size', min_value=2, max_value=100, value=9)

# Add submit button in the sidebar
submit_button = st.sidebar.button('Submit')

# Update to execute changes only when the submit button is clicked
if submit_button:
    # Download stock data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if not data.empty:
        data = calculate_macd(data, short_window, long_window, signal_window)
        data = find_crossovers(data)
        # Plotting
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, subplot_titles=(f'{ticker} Candlestick', 'MACD'), row_width=[0.2, 0.7])

        # Candlestick plot
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlestick'), row=1, col=1)

        # MACD plot
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], line=dict(color='blue', width=2), name='MACD'), row=2, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Signal_Line'], line=dict(color='orange', width=2), name='Signal Line'), row=2, col=1)

        # Marking crossovers
        fig.add_trace(go.Scatter(mode='markers', x=data[data['Crossover'] == 1].index, y=data[data['Crossover'] == 1]['MACD'], marker_symbol='triangle-up', marker_color='green', marker_size=10, name='Bullish Crossover'), row=2, col=1)
        fig.add_trace(go.Scatter(mode='markers', x=data[data['Crossover'] == -1].index, y=data[data['Crossover'] == -1]['MACD'], marker_symbol='triangle-down', marker_color='red', marker_size=10, name='Bearish Crossover'), row=2, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available for the given ticker.")

    # New section to get and display fundamentals data under an expander
    with st.expander("View Fundamentals Data"):
        fundamentals_data = get_fundamentals(ticker)
        st.write(fundamentals_data)
        if not fundamentals_data.empty:
            st.table(fundamentals_data)
        else:
            st.write("No fundamentals data available for the given ticker.")
