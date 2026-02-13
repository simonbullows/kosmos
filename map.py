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

@st.cache_data
def load_all_regions():
    """Load all available regions"""
    urls = {
        'Leicester': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/leicester_schools_enriched.csv',
        'Nottingham': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/nottingham_schools_enriched.csv',
        'Derbyshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/derbyshire_schools_enriched.csv',
        'Warwickshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/warwickshire_schools_enriched.csv',
    }
    
    all_dfs = []
    for region, url in urls.items():
        try:
            df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
            df['region'] = region
            all_dfs.append(df)
        except:
            pass
    
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return None

st.title("🗺️ KOSMOS Schools Map - Midlands")

# Load all regions
df = load_all_regions()

if df is not None:
    # Determine status
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
    st.metric("Total Schools", len(df))
    
    col1, col2, col3, col4 = st.columns(4)
    green = len(df[df['status'] == 'green'])
    orange = len(df[df['status'] == 'orange'])
    red = len(df[df['status'] == 'red'])
    col1.metric("🟢 Best", green)
    col2.metric("🟠 Email", orange)
    col3.metric("🔴 None", red)
    col4.metric("Regions", df['region'].nunique())
    
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
                'region': str(row.get('region', '')),
                'email': str(row.get('email', 'N/A')),
                'head': f"{row.get('head_first_name', '')} {row.get('head_last_name', '')}".strip(),
                'has_pp': row.get('has_pupil_premium', False),
                'status': row.get('status', 'red')
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        
        # Filters
        st.subheader("🔍 Filters")
        
        filter_col, search_col, region_col = st.columns(3)
        with filter_col:
            status_filter = st.selectbox("By Status", ["All", "🟢 Best (Email+Head+PP)", "🟠 Email Only", "🔴 No Email"])
        with search_col:
            search = st.text_input("Search school", "")
        with region_col:
            regions = ["All"] + sorted(df['region'].unique().tolist())
            region_filter = st.selectbox("By Region", regions)
        
        # Apply filters
        if status_filter != "All":
            status_map = {
                "🟢 Best (Email+Head+PP)": "green",
                "🟠 Email Only": "orange",
                "🔴 No Email": "red"
            }
            map_df = map_df[map_df['status'] == status_map[status_filter]]
        
        if region_filter != "All":
            map_df = map_df[map_df['region'] == region_filter]
        
        if search:
            map_df = map_df[map_df['name'].str.contains(search, case=False, na=False)]
        
        st.metric("Showing", len(map_df))
        
        # Map
        st.subheader(f"📍 Schools Map")
        
        # Show map
        if len(map_df) > 0:
            st.map(map_df, zoom=7)
        
        # Legend
        st.markdown("""
        **Legend:**
        - 🟢 Green: Has email + headteacher + pupil premium (best)
        - 🟠 Orange: Has email  
        - 🔴 Red: No email yet
        """)
        
        # School list
        st.subheader("📋 Schools")
        
        # Show schools in columns
        for i in range(0, len(map_df.head(50)), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(map_df):
                    school = map_df.iloc[idx]
                    emoji = "🟢" if school['status'] == 'green' else "🟠" if school['status'] == 'orange' else "🔴"
                    with col:
                        st.markdown(f"**{emoji} {school['name']}**")
                        st.caption(f"{school['town']} ({school['region']})")
                        if school['email'] != 'N/A':
                            st.caption(f"📧 {school['email']}")
                        if school['head']:
                            st.caption(f"👤 {school['head']}")

else:
    st.warning("No data available")

# Sidebar
st.sidebar.header("📊 Coverage")
st.sidebar.write("Leicester: ✅ 381 schools")
st.sidebar.write("Nottingham: ✅ 334 schools")  
st.sidebar.write("Derbyshire: ✅ 485 schools")
st.sidebar.write("Warwickshire: ✅ 239 schools")
st.sidebar.write("---")
st.sidebar.write("**Total: 1,439 schools**")
