import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Revenue Impact Dashboard", layout="wide")
st.title("📊 Revenue Impact Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip() for col in df.columns]

    # Clean & convert
    df['Date'] = pd.to_datetime(df['Date'])
    df['Gross Revenue'] = df['Gross Revenue'].astype(str).str.replace("$", "").str.replace(",", "").astype(float)
    df['CTR'] = df['CTR'].astype(str).str.replace("%", "").astype(float)

    def clean_margin(value):
        value = str(value).replace('%', '').replace(',', '').strip()
        if value.startswith('(') and value.endswith(')'):
            return -float(value.strip('()%'))
        try:
            return float(value)
        except:
            return None

    df['Margin'] = df['Margin'].apply(clean_margin)
    df['eCPM'] = df['eCPM'].astype(str).str.replace("$", "").astype(float)

    # Define time windows
    latest_date = df['Date'].max()
    window_1 = df[df['Date'] > latest_date - pd.Timedelta(days=3)]
    window_2 = df[(df['Date'] <= latest_date - pd.Timedelta(days=3)) & (df['Date'] > latest_date - pd.Timedelta(days=6))]

    # Aggregate
    agg_cols = ['Gross Revenue', 'CTR', 'Margin', 'eCPM']
    w1_agg = window_1.groupby('Package')[agg_cols].mean().rename(columns=lambda x: f"{x} (Recent)")
    w2_agg = window_2.groupby('Package')[agg_cols].mean().rename(columns=lambda x: f"{x} (Prior)")

    merged = w1_agg.merge(w2_agg, left_index=True, right_index=True)

    for col in agg_cols:
        merged[f'{col} Change (%)'] = ((merged[f'{col} (Recent)'] - merged[f'{col} (Prior)']) / merged[f'{col} (Prior)']) * 100

    # Filter insights
    significant_changes = merged[
        (abs(merged['Gross Revenue Change (%)']) >= 20) &
        (merged['Gross Revenue (Recent)'] >= 10)
    ]

    st.subheader("📌 Strategic Package Insights (3d vs 3d)")

    if not significant_changes.empty:
        for idx, row in significant_changes.iterrows():
            pkg = idx
            rev_change = row['Gross Revenue Change (%)']
            ctr_change = row['CTR Change (%)']
            margin_change = row['Margin Change (%)']
            ecpm_change = row['eCPM Change (%)']

            trend = "increased" if rev_change > 0 else "dropped"
            insight = (
                f"📦 Package `{pkg}` {trend} gross revenue by {abs(rev_change):.1f}% "
                f"over the last 3 days vs prior 3. "
                f"CTR: {ctr_change:+.1f}%, Margin: {margin_change:+.1f}%, eCPM: {ecpm_change:+.1f}%."
            )
            st.markdown(insight)
    else:
        st.info("No significant revenue shifts found.")

    # AI Chat box (optional demo)
    st.subheader("💬 Ask AI About This Data (Demo)")
    user_question = st.text_area("Type your question:")
    if st.button("Ask AI"):
        mock_responses = [
            "The strongest performance came from `com.puzzle.star` with $5,200 in revenue.",
            "Margin increased significantly on 2 high-volume apps.",
            "CTR decreased for 40% of packages in the past 3 days.",
        ]
        ai_answer = random.choice(mock_responses)
        st.success(f"AI (Demo): {ai_answer}")

    # Optional link to optimization tool
    st.markdown("[Go to Product Optimization Tool](https://your-streamlit-app-url.com/ProductOptimizationPage)")

else:
    st.info("Upload a CSV file to begin.")
