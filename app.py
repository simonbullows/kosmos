import streamlit as st
import pandas as pd
import urllib.request
import io

st.set_page_config(page_title="KOSMOS CRM", layout="wide", page_icon="🔗")

# Load all data from GitHub
@st.cache_data
def load_data():
    # Companies
    companies_url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/kosmos_csr_export.csv"
    companies = pd.read_csv(io.StringIO(urllib.request.urlopen(companies_url).read().decode('utf-8')))
    companies['type'] = 'Company'
    
    # Schools (real data)
    schools_url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/schools_export.csv"
    schools = pd.read_csv(io.StringIO(urllib.request.urlopen(schools_url).read().decode('utf-8')))
    schools['type'] = 'School'
    schools['status'] = 'Active'
    schools['display'] = schools.apply(lambda x: f"{x['name'][:50]} | {x['town'] or 'N/A'}", axis=1)
    
    # Media
    media_data = [
        {"name": "BBC News", "type": "Media", "category": "Broadcast", "town": "London", "postcode": "W1A 1AA", "county": "", "status": "Active"},
        {"name": "The Guardian", "type": "Media", "category": "Newspaper", "town": "London", "postcode": "N1 9GU", "county": "", "status": "Active"},
        {"name": "The Telegraph", "type": "Media", "category": "Newspaper", "town": "London", "postcode": "SW1A 1AA", "county": "", "status": "Active"},
        {"name": "Sky News", "type": "Media", "category": "Broadcast", "town": "London", "postcode": "W12 7RJ", "county": "", "status": "Active"},
        {"name": "ITV News", "type": "Media", "category": "Broadcast", "town": "London", "postcode": "WC2X 8JL", "county": "", "status": "Active"},
        {"name": "Channel 4 News", "type": "Media", "category": "Broadcast", "town": "London", "postcode": "W1F 7LX", "county": "", "status": "Active"},
    ]
    media = pd.DataFrame(media_data)
    
    # Healthcare
    healthcare_data = [
        {"name": "NHS Trusts", "type": "Healthcare", "category": "NHS Trust", "town": "Various", "postcode": "", "county": "", "status": "Active"},
        {"name": "Hospitals", "type": "Healthcare", "category": "Hospital", "town": "Various", "postcode": "", "county": "", "status": "Active"},
        {"name": "GP Practices", "type": "Healthcare", "category": "Primary Care", "town": "Various", "postcode": "", "county": "", "status": "Active"},
        {"name": "Care Homes", "type": "Healthcare", "category": "Social Care", "town": "Various", "postcode": "", "county": "", "status": "Active"},
    ]
    healthcare = pd.DataFrame(healthcare_data)
    
    # Charities
    charities_data = [
        {"name": "National Charities", "type": "Charity", "category": "National", "town": "London", "postcode": "", "county": "", "status": "Active"},
        {"name": "Local Charities", "type": "Charity", "category": "Local", "town": "Various", "postcode": "", "county": "", "status": "Active"},
        {"name": "Community Interest Companies", "type": "Charity", "category": "CIC", "town": "Various", "postcode": "", "county": "", "status": "Active"},
    ]
    charities = pd.DataFrame(charities_data)
    
    # Government
    government_data = [
        {"name": "Local Councils", "type": "Government", "category": "Local Authority", "town": "Various", "postcode": "", "county": "", "status": "Active"},
        {"name": "MPs - Parliament", "type": "Government", "category": "Parliament", "town": "London", "postcode": "SW1A 0AA", "county": "", "status": "Active"},
        {"name": "Councillors", "type": "Government", "category": "Local", "town": "Various", "postcode": "", "county": "", "status": "Active"},
    ]
    government = pd.DataFrame(government_data)
    
    return companies, schools, media, healthcare, charities, government

companies, schools, media, healthcare, charities, government = load_data()

# Sidebar
st.sidebar.title("🔗 KOSMOS CRM")
st.sidebar.markdown("---")

# Stats
total = len(companies) + len(schools) + len(media) + len(healthcare) + len(charities) + len(government)
st.sidebar.metric("Total Contacts", f"{total:,}")

# Category filter
categories = {
    "All": "all",
    "🏢 Companies": "company",
    "🏫 Schools": "school",
    "📰 Media": "media",
    "🏥 Healthcare": "healthcare",
    "❤️ Charities": "charity",
    "🏛️ Government": "government"
}

selected = st.sidebar.radio("Category", list(categories.keys()))

# Search
search = st.sidebar.text_input("🔍 Search", "")

# Filter data
type_filter = categories[selected]

if type_filter == "all":
    df = pd.concat([companies, schools, media, healthcare, charities, government])
else:
    df = companies if type_filter == "company" else \
         schools if type_filter == "school" else \
         media if type_filter == "media" else \
         healthcare if type_filter == "healthcare" else \
         charities if type_filter == "charity" else government

if search:
    df = df[df.apply(lambda x: search.lower() in str(x.values).lower(), axis=1)]

# Main content
st.title(f"{selected}")

# Stats for current view
st.markdown(f"### {len(df):,} contacts")

# Show categories breakdown
if selected == "All":
    st.markdown("#### Breakdown")
    breakdown = {
        "🏢 Companies": len(companies),
        "🏫 Schools": len(schools),
        "📰 Media": len(media),
        "🏥 Healthcare": len(healthcare),
        "❤️ Charities": len(charities),
        "🏛️ Government": len(government),
    }
    cols = st.columns(6)
    for i, (cat, count) in enumerate(breakdown.items()):
        cols[i].metric(cat.split()[1], f"{count:,}")

# Entity selector
if len(df) > 0:
    # Get unique names
    names = df['name'].unique()[:500]
    selected_name = st.selectbox("Select entity", names)
    
    if selected_name:
        entity = df[df['name'] == selected_name].iloc[0]
        
        st.markdown("---")
        st.subheader(entity['name'])
        
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Type:** {entity['type']}")
        col2.write(f"**Category:** {entity.get('category', 'N/A')}")
        col3.write(f"**Status:** {entity.get('status', 'N/A')}")
        
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Town:** {entity.get('town', 'N/A')}")
        col2.write(f"**Postcode:** {entity.get('postcode', 'N/A')}")
        col3.write(f"**County:** {entity.get('county', 'N/A')}")
        
        # Actions
        st.markdown("### Actions")
        action_cols = st.columns(4)
        action_cols[0].button("📧 Email", key="email")
        action_cols[1].button("📞 Call", key="call")
        action_cols[2].button("⭐ Add to List", key="add")
        action_cols[3].button("📝 Notes", key="notes")

# Data table
with st.expander("View Raw Data"):
    st.dataframe(df.head(100), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Select a category and search to find contacts")

# CSV Download
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df)

st.sidebar.download_button(
    "📥 Download CSV",
    csv,
    "kosmos_export.csv",
    "text/csv",
    key='download-csv'
)
