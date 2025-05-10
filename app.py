import streamlit as st
import pandas as pd

st.title("File Filter Tool")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Auto-detect file type
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("File uploaded successfully:")
    st.write(df.head())
    st.write("Column data types:")
    st.write(df.dtypes)

    # Set threshold inputs
    rpm_threshold = st.number_input("RPM threshold (≤)", value=0.001, format="%.4f")
    gross_revenue_max = st.number_input("Gross Revenue max (≤)", value=1.0)
    request_ne_min = st.number_input("Request NE min (≥)", value=5000000, step=1000)
    st.caption(f"Formatted Request NE min: {request_ne_min:,}")

    if st.button("Run Filter"):
        # Clean + convert numeric fields
        for col in ['RPM', 'Gross Revenue', 'Request NE']:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Apply filter
        filtered_df = df[
            (df['RPM'] <= rpm_threshold) &
            ((df['Gross Revenue'].isna()) | (df['Gross Revenue'] <= gross_revenue_max)) &
            (df['Request NE'] >= request_ne_min)
        ]

        st.subheader("Filtered Results")
        st.write(filtered_df)

        # Export CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="filtered_results.csv")

        st.button("Execute on Platform (Demo)")
