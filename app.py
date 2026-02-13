import streamlit as st
import pandas as pd
import urllib.request
import io
import time

st.set_page_config(page_title="KOSMOS Schools CRM", page_icon="🏫")

# Cache data loading
@st.cache_data
def load_leicester():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/leicester_schools_enriched.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    return df

@st.cache_data
def load_all_schools():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/schools_full.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    return df

# Simple postcode to lat/lon (UK)
def geocode_postcode(postcode):
    """Simple UK postcode geocoding"""
    if pd.isna(postcode) or not postcode:
        return None, None
    
    # Clean postcode
    pc = postcode.strip().upper().replace(' ', '')
    
    # Use a simple approximation (UK grid)
    # This is a simplified version - for production, use a proper API
    try:
        # Try to extract outward code
        if len(pc) >= 2:
            # LE2, LE3, etc - approximate center of Leicester area
            outward = pc[:2] if pc.startswith('LE') else pc[:3]
            
            # Approximate centers for common codes
            centers = {
                'LE1': (52.6337, -1.1315),  # Leicester center
                'LE2': (52.6337, -1.1315),
                'LE3': (52.6337, -1.1315),
                'LE4': (52.6337, -1.1315),
                'LE5': (52.6337, -1.1315),
                'LE6': (52.6337, -1.1315),
                'LE7': (52.6337, -1.1315),
                'LE8': (52.6337, -1.1315),
                'LE9': (52.6337, -1.1315),
                'DE': (52.9225, -1.4750),  # Derby
                'NG': (52.9548, -1.1581),  # Nottingham
                'CV': (52.4800, -1.5000),  # Coventry
                'NN': (52.2405, -0.9024),  # Northampton
            }
            
            if outward in centers:
                lat, lon = centers[outward]
                # Add small random offset to spread markers
                import random
                lat += random.uniform(-0.02, 0.02)
                lon += random.uniform(-0.02, 0.02)
                return lat, lon
    except:
        pass
    
    # Default to Leicester
    return 52.6337 + (hash(pc) % 100 - 50) * 0.0001, -1.1315 + (hash(pc) % 100 - 50) * 0.0001

st.title("🏫 KOSMOS Schools CRM")

# Data source selector
data_source = st.radio("Data Source", ["Leicester (with emails)", "All UK Schools"], horizontal=True)

if "Leicester" in data_source:
    schools = load_leicester()
    st.metric("Total Schools", len(schools))
    found = len(schools[schools['email'].notna() & (schools['email'] != '')])
    st.metric("With Emails", f"{found} ({found/len(schools)*100:.0f}%)")
else:
    schools = load_all_schools()
    st.metric("All UK Schools", f"{len(schools):,}")

# Sidebar filters
st.sidebar.header("Filters")

# Town/Area dropdown
if 'town' in schools.columns:
    towns = ["All"] + sorted(schools['town'].dropna().unique().tolist())
    selected_town = st.sidebar.selectbox("Select Town/Area", towns)
else:
    selected_town = "All"

# Search
search = st.sidebar.text_input("🔍 Search school name", "")

# Apply filters
df = schools.copy()

if selected_town != "All":
    df = df[df['town'] == selected_town]

if search:
    df = df[df['name'].str.contains(search, case=False, na=False)]

# Show count
st.markdown(f"### {len(df)} schools")

# MAP VIEW
if st.checkbox("🗺️ Show Map"):
    st.subheader("School Locations")
    
    # Geocode postcodes
    map_data = []
    for _, row in df.iterrows():
        lat, lon = geocode_postcode(row.get('postcode', ''))
        if lat and lon:
            map_data.append({
                'lat': lat,
                'lon': lon,
                'name': row['name'][:30],
                'email': row.get('email', '')
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        
        # Show map
        st.map(map_df, zoom=10, color='#FF4B4B')
        
        # Show as table below
        with st.expander("View on map (table)"):
            st.dataframe(map_df, use_container_width=True)
    else:
        st.warning("No location data available")

# School list
st.subheader("Schools")

if len(df) == 0:
    st.warning("No schools found")
else:
    # Show schools
    for i, (_, row) in enumerate(df.head(50).iterrows()):
        with st.expander(f"{row['name'][:50]} ({row.get('town', 'N/A')})"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Town", row.get('town', 'N/A'))
            c2.metric("Type", row.get('type', 'N/A'))
            c3.metric("Postcode", row.get('postcode', 'N/A'))
            
            email = row.get('email', '')
            if pd.notna(email) and email:
                st.markdown(f"### 📧 {email}")
            else:
                st.warning("No email")
            
            st.write(f"**Phone:** {row.get('phone', 'N/A')}")
            st.write(f"**Website:** {row.get('website', 'N/A')}")
            
            # Headteacher
            head = f"{row.get('head_title', '')} {row.get('head_first_name', '')} {row.get('head_last_name', '')}"
            if head.strip():
                st.write(f"**Head:** {head}")

# Stats
if "Leicester" in data_source:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Email by Town")
    town_stats = schools.groupby('town')['email'].apply(lambda x: x.notna().sum()).sort_values(ascending=False).head(10)
    st.sidebar.bar_chart(town_stats)
