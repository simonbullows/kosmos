import streamlit as st
import pandas as pd
import urllib.request
import io

st.set_page_config(page_title="KOSMOS CRM", layout="wide", page_icon="🔗")

# Load data from GitHub
@st.cache_data
def load_companies():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/kosmos_csr_export.csv"
    return pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))

@st.cache_data  
def load_schools():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/schools_export.csv"
    return pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏢 Companies", "🏫 Schools", "❤️ Charities", "🏥 Healthcare", "🏛️ Government"])

# ===== COMPANIES =====
with tab1:
    st.title("🏢 Companies")
    
    companies = load_companies()
    st.metric("Total Companies", f"{len(companies):,}")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search = st.text_input("Search companies", key="co_search")
        category = st.selectbox("Category", ["All"] + sorted(companies['category'].dropna().unique().tolist()))
        town = st.selectbox("Town", ["All"] + sorted(companies['town'].dropna().unique().tolist()[:50]))
    
    with col2:
        # Filter
        df = companies.copy()
        if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        if category != "All":
            df = df[df['category'] == category]
        if town != "All":
            df = df[df['town'] == town]
        
        st.write(f"**{len(df):,} companies**")
        
        # Select company
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
    
    schools = load_schools()
    st.metric("Total Schools", f"{len(schools):,}")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search = st.text_input("Search schools", key="sch_search")
        school_type = st.selectbox("Type", ["All"] + sorted(schools['category'].dropna().unique().tolist()[:30]))
        town_filter = st.selectbox("Town", ["All"] + sorted(schools['town'].dropna().unique().tolist()[:50]))
    
    with col2:
        # Filter
        df = schools.copy()
        if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        if school_type != "All":
            df = df[df['category'] == school_type]
        if town_filter != "All":
            df = df[df['town'] == town_filter]
        
        st.write(f"**{len(df):,} schools**")
        
        # Select school
        if len(df) > 0:
            selected = st.selectbox("Select school", df['name'].unique()[:100])
            
            if selected:
                s = df[df['name'] == selected].iloc[0]
                
                st.markdown("---")
                st.subheader(s['name'])
                
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Type:** {s.get('category', 'N/A')}")
                c2.write(f"**Town:** {s.get('town', 'N/A')}")
                c3.write(f"**Postcode:** {s.get('postcode', 'N/A')}")
                
                c1, c2 = st.columns(2)
                c1.write(f"**County:** {s.get('county', 'N/A')}")
                
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
    st.info("⚠️ Charity data requires API access. See Settings for setup.")
    
    # Placeholder for charity data
    st.write("Register for Charity Commission API to load official charity data.")
    
    with st.expander("Setup Instructions"):
        st.markdown("""
        1. Go to: https://register-of-charity-commission.apps.gov.uk/
        2. Register for API access (free)
        3. Download full charity dataset
        4. Upload CSV here
        """)

# ===== HEALTHCARE =====
with tab4:
    st.title("🏥 Healthcare")
    st.info("⚠️ NHS data requires official sources.")
    
    st.write("""
    **Data sources:**
    - NHS Trusts: https://digital.nhs.uk/services/organisation-data
    - Care Quality Commission: https://www.cqc.org.uk
    """)

# ===== GOVERNMENT =====
with tab5:
    st.title("🏛️ Government")
    st.info("⚠️ Government data requires official sources.")
    
    st.write("""
    **Data sources:**
    - MPs: https://members-api.parliament.uk
    - Councillors: https://openregister.org
    - Councils: https://local.gov.uk
    """)

# Sidebar
with st.sidebar:
    st.title("🔗 KOSMOS CRM")
    st.metric("Total Contacts", f"{len(load_companies()) + len(load_schools()):,}")
    
    st.markdown("### Quick Links")
    st.page_link("https://github.com/simonbullows/kosmos", label="GitHub Repo")
    st.page_link("https://find-and-update.company-information.service.gov.uk", label="Companies House")
    st.page_link("https://register-of-charity-commission.apps.gov.uk", label="Charity Commission")
    
    st.markdown("### Data Status")
    st.write("✅ Companies: 50K (from Companies House)")
    st.write("✅ Schools: 30K (from UK School Data)")
    st.write("❌ Charities: Need API access")
    st.write("❌ Healthcare: Need NHS data")
    st.write("❌ Government: Need official sources")
    
    st.markdown("### Upload Data")
    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded:
        st.write("Upload processed - would need database update")
