import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Campaign Insights Dashboard", layout="wide")

st.title("Campaign Insights Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
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

    # CONFIGURABLE TOP N PACKAGES
    top_n = st.number_input("Number of Top Packages (by Gross Revenue) to Analyze", min_value=1, max_value=50, value=10, step=1)

    # Get total revenue per package
    package_revenue = df.groupby('Package')['Gross Revenue'].sum().sort_values(ascending=False)
    top_packages = package_revenue.head(top_n).index.tolist()

    # Filter df to top packages
    df = df[df['Package'].isin(top_packages)]

    st.write(f"Analyzing top {top_n} packages by Gross Revenue:")

    # Anomaly detection
    metrics = ['Gross Revenue', 'CTR', 'FillRate', 'Margin', 'eCPM', 'Request NE']
    for metric in metrics:
        df[f'{metric} Change (%)'] = df.groupby(['Package', 'Placement', 'Ad format', 'Channel'])[metric].pct_change() * 100

    # Threshold filter
    threshold_slider = st.slider("Minimum % Change to Show Insights", min_value=10, max_value=100, value=30, step=5)

    # Generate insights
    insights = []

    for idx, row in df.iterrows():
        package_display = f"`{row['Package']}`"

        for metric in metrics:
            change = row.get(f'{metric} Change (%)')

            if (
                pd.isnull(change)
                or abs(change) < threshold_slider
                or pd.isnull(row[metric])
                or row[metric] == 0
                or change in [float('inf'), float('-inf')]
            ):
                continue

            arrow = "🔺" if change > 0 else "🔻"
            insight = (
                f"{arrow} {metric} for {package_display} "
                f"({row['Ad format']}, {row['Placement']}, {row['Channel']}) "
                f"{'increased' if change > 0 else 'decreased'} {abs(change):.1f}% on {row['Date'].strftime('%Y-%m-%d')} "
                f"(value: {row[metric]:,.2f}, Gross Revenue: {row['Gross Revenue']:,.2f})"
            )
            insights.append(insight)

    # Display insights
    st.subheader(f"Insights for {selected_advertiser} (Top {top_n} Packages)")
    if insights:
        for insight in insights:
            st.write(insight)
    else:
        st.info("No anomalies detected in top packages.")

    # Download button
    insights_df = pd.DataFrame(insights, columns=['Insight'])
    csv_download = insights_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Insights CSV", data=csv_download, file_name="insights.csv")

    # AI Chat box (demo)
    st.subheader("💬 Ask AI About This Data (Demo)")
    user_question = st.text_area("Type your question:")
    if st.button("Ask AI"):
        mock_responses = [
            "This dataset contains 12 packages. Highest CTR was 1.45%.",
            "Top grossing package is `com.peoplefun.wordcross` with $5,000.",
            "FillRate dropped significantly on 2025-05-07 for `1037773731`.",
            "Margin is consistently over 20% for your top 3 packages."
        ]
        ai_answer = random.choice(mock_responses)
        st.success(f"AI (Demo): {ai_answer}")

    # Navigation
    st.markdown("[Go to Product Optimization Tool](https://your-streamlit-app-url.com/ProductOptimizationPage)")

else:
    st.info("Upload a CSV file to begin.")
