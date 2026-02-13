import streamlit as st
import sqlite3
import pandas as pd
import urllib.request

CSV_URL = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/kosmos_csr_export.csv"

st.set_page_config(page_title="KOSMOS Database", layout="wide")
st.title("🔗 KOSMOS Database")
st.markdown("UK Stakeholder Mapping for CSR Programmes")

# Load data from GitHub
try:
    import io
    data = urllib.request.urlopen(CSV_URL).read().decode('utf-8')
    df = pd.read_csv(io.StringIO(data))
    st.metric("Total CSR Companies", f"{len(df):,}")
    
    # Search
    search = st.text_input("Search companies, towns...")
    
    if search:
        results = df[df.apply(lambda x: search.lower() in str(x).lower(), axis=1)]
        st.subheader(f"Results ({len(results)})")
        st.dataframe(results.head(100), use_container_width=True)
    else:
        # Show sample
        st.subheader("Sample Companies")
        st.dataframe(df.head(50), use_container_width=True)
        
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.write("CSV file not found or empty")
