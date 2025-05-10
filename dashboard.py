import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Revenue Impact Dashboard", layout="wide")

st.title("📊 Revenue Impact Dashboard (≥ $10 Gross Revenue Change)")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Normalize columns
    df.columns = [col.strip() for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Gross Revenue'] = df['Gross Revenue'].astype(str).str.replace("$", "").str.replace(",", "")
    df['Gross Revenue'] = pd.to_numeric(df['Gross Revenue'], errors='coerce')

    # Find the latest date
    latest_date = df['Date'].max()

    # Split into two windows: last 3 days vs previous 3 days
    recent = df[df['Date'] > latest_date - pd.Timedelta(days=3)]
    prior = df[(df['Date'] <= latest_date - pd.Timedelta(days=3)) & (df['Date'] > latest_date - pd.Timedelta(days=6))]

    # Aggregate revenue per package
    recent_rev = recent.groupby("Package")["Gross Revenue"].sum().rename("Recent")
    prior_rev = prior.groupby("Package")["Gross Revenue"].sum().rename("Prior")
    merged = pd.concat([recent_rev, prior_rev], axis=1).fillna(0)

    # Compute $ and % change
    merged["Change ($)"] = merged["Recent"] - merged["Prior"]
    merged = merged[merged["Change ($)"].abs() >= 10]

    merged["Change (%)"] = merged.apply(
        lambda row: ((row["Change ($)"] / row["Prior"]) * 100) if row["Prior"] != 0 else np.nan,
        axis=1
    )

    # Format insights
    insights = []
    for idx, row in merged.iterrows():
        trend = "increased" if row["Change ($)"] > 0 else "dropped"
        percent = f"{abs(row['Change (%)']):.1f}%" if not np.isnan(row["Change (%)"]) else "N/A"
        revenue = f"${abs(row['Change ($)']):,.0f}"
        insights.append(f"📦 `{idx}` gross revenue {trend} by {percent} ({revenue}) over the last 3 days vs prior.")

    # Display
    st.subheader("Insights: Packages with ≥ $10 day-over-day gross revenue change")
    if insights:
        for line in insights:
            st.markdown(f"- {line}")
    else:
        st.info("No packages with ≥ $10 gross revenue change found.")
