import streamlit as st
import pandas as pd
import urllib.request
import io
import random

st.set_page_config(page_title="KOSMOS Schools Map", page_icon="🗺️")

# Simple UK postcode to lat/lon (approximate)
def geocode_uk(postcode):
    """Approximate geocoding for UK postcodes"""
    if pd.isna(postcode) or not postcode:
        return None, None
    
    pc = str(postcode).strip().upper().replace(' ', '')
    
    # Outward code centers (approximate)
    centers = {
        'LE': (52.63, -1.13),   # Leicester
        'NG': (52.95, -1.15),   # Nottingham
        'DE': (52.92, -1.55),   # Derby
        'CV': (52.48, -1.50),   # Coventry
        'NN': (52.24, -0.90),   # Northampton
        'PE': (52.57, -0.24),   # Peterborough
        'MK': (52.04, -0.76),   # Milton Keynes
        'WS': (52.58, -1.98),   # Walsall
        'DY': (52.51, -2.08),   # Dudley
        'B':  (52.48, -1.89),   # Birmingham
        'WR': (52.19, -2.22),   # Worcester
        'CV': (52.48, -1.50),   # Warwick
        'OX': (51.75, -1.25),   # Oxford
        'CB': (52.20, 0.12),   # Cambridge
    }
    
    outward = pc[:2] if len(pc) >= 2 else pc[:1]
    
    if outward in centers:
        lat, lon = centers[outward]
        # Add small random offset to spread markers
        lat += random.uniform(-0.05, 0.05)
        lon += random.uniform(-0.05, 0.05)
        return lat, lon
    
    # Default - add randomness
    return 52.5 + random.uniform(-0.5, 0.5), -1.3 + random.uniform(-0.5, 0.5)

# Cache data loading
@st.cache_data
def load_region(region):
    """Load school data for a region"""
    urls = {
        'Leicester': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/leicester_schools_enriched.csv',
        'Nottingham': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/nottingham_schools_enriched.csv',
        'Derbyshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/derbyshire_schools_enriched.csv',
    }
    
    if region not in urls:
        return None
    
    try:
        df = pd.read_csv(io.StringIO(urllib.request.urlopen(urls[region]).read().decode('utf-8')))
        return df
    except:
        return None

st.title("🗺️ KOSMOS Schools Regional Map")

# Region selector
region = st.selectbox("Select Region", ["Leicester", "Nottingham", "Derbyshire"])

# Load data
df = load_region(region)

if df is not None:
    st.metric("Total Schools", len(df))
    
    if 'email' in df.columns:
        emails = len(df[df['email'].notna() & (df['email'] != '')])
        st.metric("With Emails", f"{emails} ({emails/len(df)*100:.0f}%)")
    
    # Create map data
    map_data = []
    for _, row in df.iterrows():
        lat, lon = geocode_uk(row.get('postcode', ''))
        if lat:
            map_data.append({
                'lat': lat,
                'lon': lon,
                'name': str(row.get('name', ''))[:40],
                'town': str(row.get('town', '')),
                'email': str(row.get('email', 'N/A'))
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            show_emails = st.checkbox("Show only schools with emails", False)
        with col2:
            color_by = st.selectbox("Color by", ["None", "Town"])
        
        if show_emails:
            map_df = map_df[map_df['email'] != 'N/A']
            st.metric("Showing", len(map_df))
        
        # Display map
        st.subheader(f"📍 {region} Schools")
        st.map(map_df, zoom=8, color='#FF4B4B')
        
        # School list with emails
        st.subheader("📋 Schools")
        
        # Search
        search = st.text_input("Search schools", "")
        if search:
            map_df = map_df[map_df['name'].str.contains(search, case=False, na=False)]
        
        # Show schools
        for _, school in map_df.head(50).iterrows():
            with st.expander(f"{school['name']} ({school['town']})"):
                st.write(f"**Town:** {school['town']}")
                st.write(f"**Email:** {school['email']}")
                st.write(f"**Location:** {school['lat']:.4f}, {school['lon']:.4f}")

else:
    st.warning(f"Data for {region} not available yet. Check back later!")
    
# Stats
st.sidebar.header("📊 Coverage")
st.sidebar.write("Leicester: ✅ 381 schools")
st.sidebar.write("Nottingham: ✅ 334 schools")  
st.sidebar.write("Derbyshire: ✅ 485 schools")
st.sidebar.write("Warwickshire: ⏳ Queued")
