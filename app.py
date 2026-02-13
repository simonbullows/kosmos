import streamlit as st
import pandas as pd
import urllib.request
import io

st.set_page_config(page_title="KOSMOS CRM", layout="wide", page_icon="🔗")

# Load data from GitHub
@st.cache_data
def load_companies():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/kosmos_csr_export.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    df['type'] = 'Company'
    return df

@st.cache_data
def load_schools():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/schools_full.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    df['type'] = 'School'
    return df

# Load data
companies = load_companies()
schools = load_schools()

# Stats
total = len(companies) + len(schools)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏢 Companies", "🏫 Schools", "❤️ Charities", "🏥 Healthcare", "🏛️ Government"])

# ===== COMPANIES =====
with tab1:
    st.title("🏢 Companies")
    st.metric("Total Companies", f"{len(companies):,}")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search = st.text_input("Search companies", key="co_search")
        category = st.selectbox("Category", ["All"] + sorted(companies['category'].dropna().unique().tolist()))
        town = st.selectbox("Town", ["All"] + sorted(companies['town'].dropna().unique().tolist()[:50]))
    
    with col2:
        df = companies.copy()
        if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        if category != "All":
            df = df[df['category'] == category]
        if town != "All":
            df = df[df['town'] == town]
        
        st.write(f"**{len(df):,} companies**")
        
        if len(df) > 0:
            selected = st.selectbox("Select company", df['name'].unique()[:100])
            
            if selected:
                c = df[df['name'] == selected].iloc[0]
                st.markdown("---")
                st.subheader(c['name'])
                
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Category:** {c.get('category', 'N/A')}")
                c2.write(f"**Town:** {c.get('town', 'N/A')}")
                c3.write(f"**Postcode:** {c.get('postcode', 'N/A')}")
                
                c1, c2 = st.columns(2)
                c1.write(f"**County:** {c.get('county', 'N/A')}")
                c2.write(f"**Status:** {c.get('status', 'N/A')}")
                
                # Actions
                st.markdown("### Actions")
                ac1, ac2, ac3, ac4 = st.columns(4)
                ac1.button("📧 Email")
                ac2.button("📞 Call")
                ac3.button("⭐ Favorite")
                ac4.button("📋 Add to List")

# ===== SCHOOLS =====
with tab2:
    st.title("🏫 Schools")
    st.metric("Total Schools", f"{len(schools):,}")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search = st.text_input("Search schools", key="sch_search")
        school_type = st.selectbox("Type", ["All"] + sorted(schools['type'].dropna().unique().tolist()))
        town_filter = st.selectbox("Town", ["All"] + sorted(schools['town'].dropna().unique().tolist()[:50]))
        phase = st.selectbox("Phase", ["All"] + sorted(schools['phase'].dropna().unique().tolist()))
    
    with col2:
        df = schools.copy()
        if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        if school_type != "All":
            df = df[df['type'] == school_type]
        if town_filter != "All":
            df = df[df['town'] == town_filter]
        if phase != "All":
            df = df[df['phase'] == phase]
        
        st.write(f"**{len(df):,} schools**")
        
        if len(df) > 0:
            selected = st.selectbox("Select school", df['name'].unique()[:100])
            
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
                c1, c2 = st.columns(2)
                addr = f"{s.get('street', '')}, {s.get('locality', '')}, {s.get('town', '')}, {s.get('county', '')} {s.get('postcode', '')}"
                c1.write(f"**Address:** {addr}")
                c2.write(f"**Constituency:** {s.get('constituency', 'N/A')}")
                
                # Contact
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Website:** {s.get('website', 'N/A')}")
                c2.write(f"**Phone:** {s.get('phone', 'N/A')}")
                
                # Headteacher
                head = f"{s.get('head_title', '')} {s.get('head_first_name', '')} {s.get('head_last_name', '')}"
                c1.write(f"**Headteacher:** {head}")
                c2.write(f"**Role:** {s.get('head_job_title', 'N/A')}")
                
                # Actions
                st.markdown("### Actions")
                ac1, ac2, ac3, ac4 = st.columns(4)
                ac1.button("📧 Email")
                ac2.button("📞 Call")
                ac3.button("⭐ Favorite")
                ac4.button("📋 Add to List")

# ===== CHARITIES =====
with tab3:
    st.title("❤️ Charities")
    st.info("⚠️ Upload charity data to add here")
    
    st.write("""
    **Required data format:**
    - Charity name
    - Registration number
    - Address
    - Phone/Email
    - Trustees
    """)
    
    st.file_uploader("Upload charity CSV", type="csv")

# ===== HEALTHCARE =====
with tab4:
    st.title("🏥 Healthcare")
    st.info("⚠️ Upload NHS/healthcare data")
    
    st.write("""
    **Data sources:**
    - NHS Digital: https://digital.nhs.uk/services/organisation-data
    - Care Quality Commission: https://www.cqc.org.uk
    """)

# ===== GOVERNMENT =====
with tab5:
    st.title("🏛️ Government")
    st.info("⚠️ Upload government data")
    
    st.write("""
    **Data sources:**
    - MPs: https://members-api.parliament.uk
    - Councillors: https://openregister.org
    - Councils: https://local.gov.uk
    """)

# Sidebar
with st.sidebar:
    st.title("🔗 KOSMOS CRM")
    st.metric("Total Contacts", f"{total:,}")
    
    st.markdown("### Data Status")
    st.write(f"✅ Companies: {len(companies):,}")
    st.write(f"✅ Schools: {len(schools):,}")
    st.write("❌ Charities: Upload required")
    st.write("❌ Healthcare: Upload required")
    st.write("❌ Government: Upload required")
    
    st.markdown("### Upload Data")
    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded:
        st.write("Upload received - needs processing")
