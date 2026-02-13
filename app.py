import streamlit as st
import pandas as pd
import urllib.request
import io

st.set_page_config(page_title="KOSMOS Schools", page_icon="🏫")

# Load school data
@st.cache_data
def load_schools():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/schools_full.csv"
    return pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))

schools = load_schools()

st.title("🏫 KOSMOS Schools CRM")
st.metric("Total Schools", f"{len(schools):,}")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("🔍 Search school name", key="search")

with col2:
    school_type = st.selectbox("Type", ["All"] + sorted(schools['type'].dropna().unique().tolist()))

with col3:
    phase = st.selectbox("Phase", ["All"] + sorted(schools['phase'].dropna().unique().tolist()))

# Filter data
df = schools.copy()

if search:
    df = df[df['name'].str.contains(search, case=False, na=False)]
if school_type != "All":
    df = df[df['type'] == school_type]
if phase != "All":
    df = df[df['phase'] == phase]

st.markdown(f"**{len(df):,} schools**")

# Select school
if len(df) > 0:
    selected = st.selectbox("Select a school", df['name'].unique()[:200])

    if selected:
        s = df[df['name'] == selected].iloc[0]
        
        st.markdown("---")
        st.subheader(s['name'])
        
        # Key info
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Type:** {s.get('type', 'N/A')}")
        c2.write(f"**Phase:** {s.get('phase', 'N/A')}")
        c3.write(f"**Status:** {s.get('status', 'N/A')}")
        
        # Address
        addr = f"{s.get('street', '')}, {s.get('locality', '')}, {s.get('town', '')}, {s.get('county', '')} {s.get('postcode', '')}"
        st.write(f"**Address:** {addr}")
        
        # Contact
        c1, c2 = st.columns(2)
        c1.write(f"**Website:** {s.get('website', 'N/A')}")
        c2.write(f"**Phone:** {s.get('phone', 'N/A')}")
        
        # Headteacher
        head = f"{s.get('head_title', '')} {s.get('head_first_name', '')} {s.get('head_last_name', '')}"
        st.write(f"**Headteacher:** {head}")
        st.write(f"**Role:** {s.get('head_job_title', 'N/A')}")
        
        # Actions
        st.markdown("### Actions")
        ac1, ac2, ac3, ac4 = st.columns(4)
        ac1.button("📧 Email")
        ac2.button("📞 Call")
        ac3.button("⭐ Favorite")
        ac4.button("📋 Add to List")

# Data table
with st.expander("📊 View All Data"):
    st.dataframe(df.head(100), use_container_width=True)

# Stats by phase
st.markdown("### Schools by Phase")
phase_counts = schools['phase'].value_counts().head(10)
st.bar_chart(phase_counts)

# Stats by type
st.markdown("### Schools by Type")
type_counts = schools['type'].value_counts().head(10)
st.bar_chart(type_counts)
