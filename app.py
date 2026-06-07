import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import ta

# PAGE CONFIG
st.set_page_config(
    page_title="Stock Market Intelligence Dashboard",
    layout="wide"
)

# CUSTOM CSS
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
h1 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# TITLE
st.title("📈 Stock Market Intelligence Dashboard")

# SIDEBAR
st.sidebar.header("Settings")

ticker = st.sidebar.text_input(
    "Stock Ticker",
    "RELIANCE.NS"
)

period = st.sidebar.selectbox(
    "Period",
    ["1y", "2y", "5y", "10y"],
    index=2
)

# DOWNLOAD DATA
with st.spinner("Downloading stock data..."):

    df = yf.download(
        ticker,
        period=period,
        auto_adjust=False,
        progress=False
    )

# FIX MULTIINDEX
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# CHECK DATA
if df.empty:
    st.error("No stock data found.")
    st.stop()

# INDICATORS
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

df["RSI"] = ta.momentum.RSIIndicator(
    close=df["Close"],
    window=14
).rsi()

# RETURNS
df["Returns"] = df["Close"].pct_change()

annual_return = df["Returns"].mean() * 252
volatility = df["Returns"].std() * np.sqrt(252)

# LATEST DATA
latest = df.iloc[-1]

# TOP METRICS
st.subheader("Market Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current Price",
        f"₹{latest['Close']:.2f}"
    )

with col2:
    st.metric(
        "RSI",
        f"{latest['RSI']:.2f}"
    )

with col3:
    st.metric(
        "Annual Return",
        f"{annual_return:.2%}"
    )

# PRICE CHART
st.subheader("Price Chart")

fig_price = go.Figure()

fig_price.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Close Price",
        line=dict(width=2)
    )
)

fig_price.add_trace(
    go.Scatter(
        x=df.index,
        y=df["SMA20"],
        name="SMA20"
    )
)

fig_price.add_trace(
    go.Scatter(
        x=df.index,
        y=df["SMA50"],
        name="SMA50"
    )
)

fig_price.update_layout(
    height=600,
    template="plotly_dark"
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)

# RSI
st.subheader("RSI Indicator")

fig_rsi = go.Figure()

fig_rsi.add_trace(
    go.Scatter(
        x=df.index,
        y=df["RSI"],
        name="RSI"
    )
)

fig_rsi.add_hline(y=70)
fig_rsi.add_hline(y=30)

fig_rsi.update_layout(
    template="plotly_dark",
    height=400
)

st.plotly_chart(
    fig_rsi,
    use_container_width=True
)

# VOLUME
st.subheader("Trading Volume")

fig_volume = px.bar(
    df,
    x=df.index,
    y="Volume",
    title="Volume"
)

fig_volume.update_layout(
    template="plotly_dark",
    height=400
)

st.plotly_chart(
    fig_volume,
    use_container_width=True
)

# PORTFOLIO METRICS
st.subheader("Portfolio Analytics")

col4, col5 = st.columns(2)

with col4:
    st.metric(
        "Annual Return",
        f"{annual_return:.2%}"
    )

with col5:
    st.metric(
        "Volatility",
        f"{volatility:.2%}"
    )

# DATA TABLE
st.subheader("Latest Data")

st.dataframe(
    df.tail(20),
    use_container_width=True
)

# DOWNLOAD BUTTON
csv = df.to_csv().encode("utf-8")

st.download_button(
    "Download CSV",
    csv,
    f"{ticker}.csv",
    "text/csv"
)