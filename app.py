import streamlit as st
import pandas as pd

st.title("Excel Filter Tool")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])


if uploaded_file:
    df = pd.read_csv(uploaded_file)
(uploaded_file)
    st.write("File uploaded successfully:")
    st.write(df.head())

    rpm_threshold = st.number_input("RPM threshold (≤)", value=0.001)
    gross_revenue_max = st.number_input("Gross Revenue max (≤)", value=1.0)
    request_ne_min = st.number_input("Request NE min (≥)", value=5000000)

    if st.button("Run Filter"):
        df['RPM'] = pd.to_numeric(df['RPM'], errors='coerce')
        df['Gross Revenue'] = pd.to_numeric(df['Gross Revenue'], errors='coerce')
        df['Request NE'] = pd.to_numeric(df['Request NE'], errors='coerce')

        filtered_df = df[
            (df['RPM'] <= rpm_threshold) &
            ((df['Gross Revenue'].isna()) | (df['Gross Revenue'] <= gross_revenue_max)) &
            (df['Request NE'] >= request_ne_min)
        ]

        st.subheader("Filtered Results")
        st.write(filtered_df)

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="filtered_results.csv")

        st.button("Execute on Platform (Demo)")

