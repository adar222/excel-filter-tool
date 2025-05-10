import streamlit as st
import pandas as pd

st.set_page_config(page_title="Revenue Impact Insights", layout="wide")
st.title("📊 Revenue Impact Dashboard (≥ $10 Gross Revenue Change)")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip() for col in df.columns]

    # Clean and prepare
    df['Date'] = pd.to_datetime(df['Date'])
    df['Gross Revenue'] = df['Gross Revenue'].astype(str).str.replace("$", "").str.replace(",", "").astype(float)

    # Sort and calculate day-over-day change
    df = df.sort_values(by=['Package', 'Date'])
    df['Gross Revenue Change'] = df.groupby('Package')['Gross Revenue'].diff()

    # Filter: only rows with ≥ $10 absolute revenue change
    threshold = 10
    filtered = df[abs(df['Gross Revenue Change']) >= threshold]

    st.subheader(f"Insights: Packages with ≥ ${threshold} day-over-day gross revenue change")

    if not filtered.empty:
        st.dataframe(filtered[['Date', 'Package', 'Ad format', 'Channel', 'Placement', 'Gross Revenue', 'Gross Revenue Change']])
    else:
        st.info("No significant revenue changes detected.")

    # Download option
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", data=csv, file_name="significant_revenue_changes.csv")

else:
    st.info("Upload a CSV file to begin.")
