import streamlit as st
import pandas as pd
import urllib.request
import io

st.set_page_config(page_title="KOSMOS Schools CRM", page_icon="🏫")

# Load enriched Leicester data (with emails)
@st.cache_data
def load_leicester():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/leicester_schools_enriched.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    df['type'] = 'School'
    return df

# Load full UK schools
@st.cache_data
def load_all_schools():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/schools_full.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    df['type'] = 'School'
    return df

st.title("🏫 KOSMOS Schools CRM")

# Data selector
data_source = st.radio("Data Source", ["Leicester (with emails)", "All UK Schools"])

if "Leicester" in data_source:
    schools = load_leicester()
    st.metric("Leicester Schools", f"{len(schools)}")
    found = len(schools[schools['email'].notna() & (schools['email'] != '')])
    st.metric("With Emails", f"{found} ({found/len(schools)*100:.0f}%)")
else:
    schools = load_all_schools()
    st.metric("All UK Schools", f"{len(schools):,}")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("🔍 Search school name")

with col2:
    school_type = st.selectbox("Type", ["All"] + sorted(schools['type'].dropna().unique().tolist()) if 'type' in schools.columns else ["All"]

with col3:
    town = st.selectbox("Town", ["All"] + sorted(schools['town'].dropna().unique().tolist()[:50]) if 'town' in schools.columns else ["All"]

# Filter
df = schools.copy()

if search:
    df = df[df['name'].str.contains(search, case=False, na=False)]
    
st.markdown(f"**{len(df):,} schools**")

# Select school
if len(df) > 0:
    selected = st.selectbox("Select a school", df['name'].unique()[:200])

    if selected:
        s = df[df['name'] == selected].iloc[0]
        
        st.markdown("---")
        st.subheader(s['name'])
        
        # Contact info - HIGHLIGHT EMAIL
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Type:** {s.get('type', 'N/A')}")
        c2.write(f"**Town:** {s.get('town', 'N/A')}")
        c3.write(f"**Postcode:** {s.get('postcode', 'N/A')}")
        
        # EMAIL - Make it prominent
        email = s.get('email', '')
        if pd.notna(email) and email:
            st.markdown(f"### 📧 {email}")
        else:
            st.warning("No email found")
        
        st.write(f"**Phone:** {s.get('phone', 'N/A')}")
        st.write(f"**Website:** {s.get('website', 'N/A')}")
        
        # Headteacher
        head = f"{s.get('head_title', '')} {s.get('head_first_name', '')} {s.get('head_last_name', '')}"
        st.write(f"**Headteacher:** {head}")
        
        # Actions
        st.markdown("### Actions")
        ac1, ac2, ac3, ac4 = st.columns(4)
        if pd.notna(email) and email:
            ac1.button("📧 Email")
        ac2.button("📞 Call")
        ac3.button("⭐ Favorite")
        ac4.button("📋 Add to List")

# Data table
with st.expander("📊 View All Data"):
    st.dataframe(df.head(100), use_container_width=True)

# Stats
if 'Leicester' in data_source:
    st.markdown("### Email Success by Town")
    town_emails = schools.groupby('town').agg({
        'email': lambda x: x.notna().sum()
    }).sort_values('email', ascending=False).head(10)
    st.bar_chart(town_emails['email'])
