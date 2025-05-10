import streamlit as st
import pandas as pd

st.set_page_config(page_title="Campaign Insights Dashboard", layout="wide")

st.title("Campaign Insights Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    # Advertiser dropdown
    advertisers = df['Advertiser'].unique().tolist()
    default_advertiser = 'OpenX' if 'OpenX' in advertisers else advertisers[0]
    selected_advertiser = st.selectbox("Select Advertiser", advertisers, index=advertisers.index(default_advertiser))

    # Filter by advertiser
    df = df[df['Advertiser'] == selected_advertiser].copy()

    # Clean numeric columns
    clean_cols = {
        'Request NE': ('Request NE', '', ','),
        'Requests AE': ('Requests AE', '', ','),
        'Publisher Impressions': ('Publisher Impressions', '', ','),
        'FillRate': ('FillRate', '%', ''),
        'eCPM': ('eCPM', '$', ''),
        'Survival rate': ('Survival rate', '%', ''),
        'Gross Revenue': ('Gross Revenue', '$', ''),
        'CTR': ('CTR', '%', ''),
        'Margin': ('Margin', '%', '')
    }

    for col, (colname, remove_char, replace_char) in clean_cols.items():
        df[col] = df[col].astype(str).str.replace(remove_char, '', regex=False).str.replace(replace_char, '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sort dates
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Package', 'Placement', 'Ad format', 'Channel', 'Date'])

    # Day-over-day percent change
    metrics = ['Gross Revenue', 'CTR', 'FillRate', 'Margin', 'eCPM', 'Request NE']
    insights = []
    for metric in metrics:
        df[f'{metric} Change (%)'] = df.groupby(['Package', 'Placement', 'Ad format', 'Channel'])[metric].pct_change() * 100

    # Flag anomalies
    threshold = 20
    for idx, row in df.iterrows():
        for metric in metrics:
            change = row.get(f'{metric} Change (%)')
            if pd.notnull(change) and (abs(change) >= threshold):
                arrow = "🔺" if change >= 0 else "🔻"
                insights.append(f"{arrow} {metric} for {row['Package']} ({row['Ad format']}, {row['Placement']}, {row['Channel']}) changed {change:.1f}% on {row['Date'].strftime('%Y-%m-%d')} (value: {row[metric]:,.2f})")

    # Show insights
    st.subheader(f"Insights for {selected_advertiser}")
    if insights:
        for insight in insights:
            st.write(insight)
    else:
        st.info("No anomalies detected.")

    # Download insights
    insights_df = pd.DataFrame(insights, columns=['Insight'])
    csv_download = insights_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Insights CSV", data=csv_download, file_name="insights.csv")

    # Link to Optimization Tool
    st.markdown("[Go to Product Optimization Tool](https://your-streamlit-app-url.com/ProductOptimizationPage)")

else:
    st.info("Upload a CSV file to begin.")

