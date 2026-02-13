import streamlit as st
import pandas as pd
import urllib.request
import io
import random

st.set_page_config(page_title="KOSMOS Schools Map", page_icon="🗺️")

# UK postcode to lat/lon
def geocode_uk(postcode):
    if pd.isna(postcode) or not postcode:
        return None, None
    
    pc = str(postcode).strip().upper().replace(' ', '')
    
    centers = {
        'LE': (52.63, -1.13), 'NG': (52.95, -1.15), 'DE': (52.92, -1.55),
        'CV': (52.48, -1.50), 'NN': (52.24, -0.90), 'PE': (52.57, -0.24),
        'MK': (52.04, -0.76), 'WS': (52.58, -1.98), 'DY': (52.51, -2.08),
        'B':  (52.48, -1.89), 'WR': (52.19, -2.22), 'OX': (51.75, -1.25),
        'CB': (52.20, 0.12), 'ST': (52.90, -2.25), 'TF': (52.74, -2.50),
    }
    
    outward = pc[:2] if len(pc) >= 2 else pc[:1]
    
    if outward in centers:
        lat, lon = centers[outward]
        lat += random.uniform(-0.04, 0.04)
        lon += random.uniform(-0.04, 0.04)
        return lat, lon
    
    return 52.5 + random.uniform(-0.5, 0.5), -1.5 + random.uniform(-0.5, 0.5)

# Load single region
@st.cache_data
def load_region(region):
    urls = {
        'Leicester': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/leicester_schools_enriched.csv',
        'Nottingham': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/nottingham_schools_enriched.csv',
        'Derbyshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/derbyshire_schools_enriched.csv',
        'Warwickshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/warwickshire_schools_enriched.csv',
    }
    
    if region not in urls:
        return None
    
    try:
        df = pd.read_csv(io.StringIO(urllib.request.urlopen(urls[region]).read().decode('utf-8')))
        df['region'] = region
        return df
    except Exception as e:
        st.error(f"Error loading {region}: {e}")
        return None

st.title("🗺️ KOSMOS Schools Map")

# Region selector
regions = ['Leicester', 'Nottingham', 'Derbyshire', 'Warwickshire']
selected_region = st.selectbox("Select Region", regions)

# Load data
df = load_region(selected_region)

if df is not None:
    # Status
    def get_status(row):
        has_email = pd.notna(row.get('email', '')) and str(row.get('email', '')).strip() != ''
        has_head = pd.notna(row.get('head_first_name', '')) or pd.notna(row.get('head_last_name', ''))
        has_pp = row.get('has_pupil_premium', False)
        
        if has_email and has_head and has_pp:
            return 'green'
        elif has_email:
            return 'orange'
        else:
            return 'red'
    
    df['status'] = df.apply(get_status, axis=1)
    
    # Stats
    st.metric("Schools", len(df))
    
    green = len(df[df['status'] == 'green'])
    orange = len(df[df['status'] == 'orange'])
    red = len(df[df['status'] == 'red'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Best", green)
    col2.metric("🟠 Email", orange)
    col3.metric("🔴 None", red)
    
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
                'email': str(row.get('email', 'N/A')),
                'head': f"{row.get('head_first_name', '')} {row.get('head_last_name', '')}".strip(),
                'has_pp': row.get('has_pupil_premium', False),
                'status': row.get('status', 'red')
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        st.map(map_df, zoom=8)
        
        # Legend
        st.caption("🟢 = Email+Head+Pupil Premium | 🟠 = Email only | 🔴 = No email")
        
        # Filter
        search = st.text_input("Search", "")
        if search:
            map_df = map_df[map_df['name'].str.contains(search, case=False, na=False)]
        
        st.metric("Showing", len(map_df))
        
        # List
        for _, school in map_df.head(30).iterrows():
            emoji = "🟢" if school['status'] == 'green' else "🟠" if school['status'] == 'orange' else "🔴"
            with st.expander(f"{emoji} {school['name']}"):
                st.write(f"**Town:** {school['town']}")
                if school['email'] != 'N/A':
                    st.write(f"**Email:** {school['email']}")
                if school['head']:
                    st.write(f"**Head:** {school['head']}")

else:
    st.warning("No data")

# Stats
st.sidebar.header("📊 Coverage")
st.sidebar.write("Leicester: 381")
st.sidebar.write("Nottingham: 334")  
st.sidebar.write("Derbyshire: 485")
st.sidebar.write("Warwickshire: 239")
st.sidebar.write("---")
st.sidebar.write("Total: 1,439")
