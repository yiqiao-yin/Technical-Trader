# 📈 MACD Trading Strategy Simulator

This app simulates a trading strategy using the Moving Average Convergence Divergence (MACD) technical indicator. It allows users to input a stock ticker, start date, and end date to download stock data and visualize the strategy using candlestick charts and MACD indicators. The app marks bullish crossovers with green triangles up and bearish crossovers with red triangles down.

## 🖥️ App

The app is currently deployed to [this app](https://technical-trader.streamlit.app/).

## Features

- **Stock Ticker Input**: Enter any valid stock ticker to analyze.
- **Date Range Selection**: Choose a start and end date for your analysis.
- **Candlestick Chart**: Visualizes the stock price movements.
- **MACD Indicator**: Shows the MACD line, signal line, and crossovers.
- **Crossover Indicators**: Bullish crossovers are marked with green triangles up, and bearish crossovers with red triangles down.

## 🚀 Getting Started

To run the app locally, follow these simple steps:

### Prerequisites

Ensure you have Python installed on your machine. This app was developed using Python 3.8, but it should work on most Python 3.x versions.

### Installation

1. **Clone the repository**

   ```sh
   git clone https://your-repository-url.git
   cd your-repository-directory
   ```

2. **Create and activate a virtual environment (optional but recommended)**

   For Windows:
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```

   For macOS and Linux:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the requirements**

   ```sh
   pip install -r requirements.txt
   ```

### Running the App

After installation, you can run the app using Streamlit:

```sh
streamlit run app.py
```

Open your web browser and go to `http://localhost:8501` to view the app.

## 📚 Documentation

For more information about the used libraries, visit:

- [Streamlit Documentation](https://docs.streamlit.io)
- [yfinance on PyPI](https://pypi.org/project/yfinance/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Python Graphing Library](https://plotly.com/python/)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

Feel free to check the [issues page](https://your-repository-url/issues).

## ✨ Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
