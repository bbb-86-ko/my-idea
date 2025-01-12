import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px

def fetch_stock_data(ticker):
    """Fetch historical stock data."""
    stock = yf.Ticker(ticker)
    data = stock.history(period="1y")
    data['Daily Return'] = data['Close'].pct_change()
    return data

def calculate_short_squeeze_metrics(data, short_float, short_ratio, avg_volume):
    """Calculate metrics to evaluate short squeeze potential."""
    squeeze_score = (short_float / 100) * short_ratio * (avg_volume / 1e6)
    return round(squeeze_score, 2)

# Streamlit App Layout
st.title("Short Squeeze Trading Strategy")
st.sidebar.header("Input Parameters")

# Input fields
ticker = st.sidebar.text_input("Stock Ticker (e.g., GME, TSLA):", "GME")
short_float = st.sidebar.slider("Short Float (%):", 0.0, 100.0, 20.0)
short_ratio = st.sidebar.number_input("Short Ratio (days to cover):", 0.1, 50.0, 5.0)
avg_volume = st.sidebar.number_input("Average Volume (shares):", 1e5, 1e9, 1e6, format="%.0f")

# Fetch and process data
st.write(f"Fetching data for {ticker}...")
data = fetch_stock_data(ticker)
squeeze_score = calculate_short_squeeze_metrics(data, short_float, short_ratio, avg_volume)

# Display metrics
st.subheader("Short Squeeze Metrics")
st.write(f"Short Float: {short_float}%")
st.write(f"Short Ratio: {short_ratio} days")
st.write(f"Average Volume: {avg_volume:.0f} shares")
st.write(f"Squeeze Score: {squeeze_score} (Higher is better)")

# Visualization
st.subheader("Price and Volume Analysis")
fig = px.line(data, x=data.index, y="Close", title=f"{ticker} Closing Price")
st.plotly_chart(fig)

# Short Squeeze Metrics Chart
st.subheader("Short Squeeze Metrics Chart")
metrics_data = pd.DataFrame({
    'Metric': ['Short Float (%)', 'Short Ratio (days)', 'Average Volume (M)'],
    'Value': [short_float, short_ratio, avg_volume / 1e6]
})
metrics_fig = px.bar(metrics_data, x='Metric', y='Value', title="Short Squeeze Metrics", text='Value')
metrics_fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(metrics_fig)

# Trading Strategy Signal
st.subheader("Trading Signal")
if squeeze_score > 50:
    st.success("Potential Short Squeeze Detected! Consider monitoring closely.")
elif squeeze_score > 20:
    st.warning("Moderate Short Squeeze Potential.")
else:
    st.info("Low Short Squeeze Potential.")
