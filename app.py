import streamlit as st
import pandas as pd

st.title("File Filter Tool")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Normalize column names (lowercase, underscores)
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
    st.write("Columns loaded:", df.columns)

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
        for col in ['rpm', 'gross_revenue', 'request_ne']:
            if col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '', regex=False).str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                st.warning(f"Column '{col}' not found in file.")

        # Apply filter
        filtered_df = df[
            (df['rpm'] <= rpm_threshold) &
            ((df['gross_revenue'].isna()) | (df['gross_revenue'] <= gross_revenue_max)) &
            (df['request_ne'] >= request_ne_min)
        ]

        st.subheader("Filtered Results")
        st.write(filtered_df)

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="filtered_results.csv")

        st.button("Execute on Platform (Demo)")
