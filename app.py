import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helper import *
from scipy.stats import norm

# Streamlit app layout
st.set_page_config(layout="wide")
st.title('MACD Trading Strategy Simulation')

# Sidebar inputs
ticker = st.sidebar.text_input('Enter Stock Ticker', 'AAPL').upper()
start_date = st.sidebar.date_input('Start Date', pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('End Date', pd.to_datetime('today'))

# Add sidebar slider for selecting two integers
st.sidebar.success("Please  select your own parameters.")
short_window = st.sidebar.slider('Select short window size', min_value=2, max_value=200, value=12)
long_window = st.sidebar.slider('Select long window size', min_value=2, max_value=250, value=50)
signal_window = st.sidebar.slider('Select signal window size', min_value=2, max_value=250, value=9)
values = st.sidebar.slider(
    'Select a range of values',
    min_value=-100,
    max_value=100,
    value=(-10, 10),
    step=1)
option = st.sidebar.selectbox(
    'How would you like rescale data?',
    ('Original', 'Normalization', 'Percentile'))
if option == 'Original':
    st.success('We use the stock price (within the range selected) to create the MACD and Signal Line (which numerically vary based on price data).')
elif option == 'Normalization':
    st.success('We use the stock price (within the range selected) to create the MACD and Signal Line (which numerically vary based on price data). Next, we normalize the MACD/Signal Line so that fall in a consistent range, i.e. approximately from -2 to 2.')
else:
    st.success('We use the stock price (within the range selected) to create the MACD and Signal Line (which numerically vary based on price data). Next, we normalize the MACD/Signal Line so that fall in a consistent range, i.e. approximately from -2 to 2. Last, we use the normalized data to create probabilities from -100% to +100%. The probability means statistically what is believed to reverse the current direction.')

# Add submit button in the sidebar
submit_button = st.sidebar.button('Submit')

# Update to execute changes only when the submit button is clicked
if submit_button:
    with st.spinner('Wait for it...'):

        # Download stock data
        data = yf.download(ticker, start=start_date, end=end_date)
        
        if not data.empty:
            if option == "Normalization":
                data = calculate_normalized_macd(data, short_window, long_window, signal_window)
                some_warning_message = "normalized data"
            elif option == "Percentile":
                data = calculate_percentile_macd(data, short_window, long_window, signal_window)
                some_warning_message = "percentile data (numbers in %)"
            else:
                data = calculate_macd(data, short_window, long_window, signal_window)
                some_warning_message = "original data"
            data = find_crossovers(data, values[0], values[1])
    
            # Plotting
            fig = create_fig(data, ticker)
            st.plotly_chart(fig, use_container_width=True)
            st.warning(f"In the above graph, we use {some_warning_message}.")
        else:
            st.write("No data available for the given ticker.")
    
        # New section to get and display fundamentals data under an expander
        with st.expander("View Fundamentals Data"):
            fundamentals_data, _, _ = get_fundamentals(ticker)
            if not fundamentals_data.empty:
                st.table(fundamentals_data)
            else:
                st.write("No fundamentals data available for the given ticker.")
