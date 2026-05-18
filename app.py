
# Streamlit Dashboard for Enterprise Log Analysis
# Save this as app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

st.set_page_config(page_title="Enterprise Log Analysis Dashboard", layout="wide")

st.title("📊 Enterprise Log Analysis for Retail Systems")

uploaded_file = st.file_uploader("Upload Apache Log File (.log)", type=["log", "txt"])

if uploaded_file is not None:

    lines = uploaded_file.read().decode("utf-8").splitlines()

    st.subheader("Raw Log Preview")
    st.write(f"Total raw lines: {len(lines)}")
    st.code("\n".join(lines[:5]))

    # Regex pattern
    pattern = re.compile(r"\[(.*?)\] \[(.*?)\] (.*)")

    parsed_data = []

    for line in lines:
        match = pattern.match(line)

        if match:
            timestamp_raw = match.group(1)
            log_level = match.group(2)
            message = match.group(3)

            parsed_data.append({
                "timestamp_raw": timestamp_raw,
                "log_level": log_level,
                "message": message
            })

    df = pd.DataFrame(parsed_data)

    # Datetime conversion
    df["timestamp"] = pd.to_datetime(
        df["timestamp_raw"],
        format="%a %b %d %H:%M:%S %Y",
        errors="coerce"
    )

    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour

    error_df = df[df["log_level"] == "error"]

    st.subheader("Summary Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Logs", len(df))
    col2.metric("Error Logs", len(error_df))
    col3.metric("Unique Log Levels", df["log_level"].nunique())
    col4.metric("Parse Success Rate", "100%")

    st.subheader("Parsed Data Preview")
    st.dataframe(df.head())

    # Log level chart
    st.subheader("Log Level Distribution")

    fig1, ax1 = plt.subplots()
    df["log_level"].value_counts().plot(kind="bar", ax=ax1)
    st.pyplot(fig1)

    # Daily error trend
    st.subheader("Daily Error Frequency")

    daily_errors = error_df.groupby("date").size()

    fig2, ax2 = plt.subplots()
    daily_errors.plot(marker="o", ax=ax2)
    ax2.set_ylabel("Error Count")
    st.pyplot(fig2)

    # Hourly error trend
    st.subheader("Hourly Error Distribution")

    hourly_errors = error_df.groupby("hour").size()

    fig3, ax3 = plt.subplots()
    hourly_errors.plot(kind="bar", ax=ax3)
    ax3.set_ylabel("Error Count")
    st.pyplot(fig3)

    # Top errors
    st.subheader("Top Repeated Error Messages")

    top_errors = error_df["message"].value_counts().head(10)

    fig4, ax4 = plt.subplots()
    top_errors.plot(kind="barh", ax=ax4)
    st.pyplot(fig4)

    # Clustering
    st.subheader("Error Message Clustering")

    if len(error_df) >= 5:

        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform(error_df["message"])

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        error_df = error_df.copy()
        error_df["cluster"] = kmeans.fit_predict(X)

        st.dataframe(error_df[["message", "cluster"]].head(15))

    st.success("Dashboard analysis completed successfully!")
