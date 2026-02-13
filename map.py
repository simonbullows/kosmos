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
        'WV': (52.55, -2.08), 'DY': (52.45, -2.05), 'HR': (52.08, -2.72),
    }
    
    outward = pc[:2] if len(pc) >= 2 else pc[:1]
    
    if outward in centers:
        lat, lon = centers[outward]
        lat += random.uniform(-0.04, 0.04)
        lon += random.uniform(-0.04, 0.04)
        return lat, lon
    
    return 52.5 + random.uniform(-0.5, 0.5), -1.5 + random.uniform(-0.5, 0.5)

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
        return pd.read_csv(io.StringIO(urllib.request.urlopen(urls[region]).read().decode('utf-8')))
    except:
        return None

st.title("🗺️ KOSMOS Schools Map")

# Region selector
region = st.selectbox("Select Region", ["Leicester", "Nottingham", "Derbyshire", "Warwickshire", "All Regions"])

df = load_region(region if region != "All Regions" else "Leicester")

if df is not None:
    # Load all if "All Regions"
    if region == "All Regions":
        dfs = []
        for r in ['Leicester', 'Nottingham', 'Derbyshire', 'Warwickshire']:
            d = load_region(r)
            if d is not None:
                dfs.append(d)
        df = pd.concat(dfs, ignore_index=True) if dfs else None
    
    if df is not None:
        # Determine status for each school
        def get_status(row):
            has_email = pd.notna(row.get('email', '')) and str(row.get('email', '')).strip() != ''
            has_head = pd.notna(row.get('head_first_name', '')) or pd.notna(row.get('head_last_name', ''))
            has_pp = row.get('has_pupil_premium', False)
            
            if has_email and has_head and has_pp:
                return 'green'  # Has email + head + pupil premium
            elif has_email:
                return 'orange'  # Has email
            else:
                return 'red'  # No email
        
        df['status'] = df.apply(get_status, axis=1)
        
        # Stats
        st.metric("Total Schools", len(df))
        green = len(df[df['status'] == 'green'])
        orange = len(df[df['status'] == 'orange'])
        red = len(df[df['status'] == 'red'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 Head + Email + PP", green)
        col2.metric("🟠 Email Only", orange)
        col3.metric("🔴 No Email", red)
        
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
            
            # Filter
            st.subheader("🔍 Filters")
            filter_col, search_col = st.columns(2)
            with filter_col:
                status_filter = st.selectbox("Filter by status", ["All", "🟢 Head + Email + PP", "🟠 Email Only", "🔴 No Email"])
            with search_col:
                search = st.text_input("Search school", "")
            
            if status_filter != "All":
                status_map = {
                    "🟢 Head + Email + PP": "green",
                    "🟠 Email Only": "orange", 
                    "🔴 No Email": "red"
                }
                map_df = map_df[map_df['status'] == status_map[status_filter]]
            
            if search:
                map_df = map_df[map_df['name'].str.contains(search, case=False, na=False)]
            
            st.metric("Showing", len(map_df))
            
            # Map with colors
            st.subheader(f"📍 {region if region != 'All Regions' else 'All Regions'} Schools")
            
            # Color map
            color_map = {'green': '#00CC00', 'orange': '#FF9900', 'red': '#FF4444'}
            
            if len(map_df) > 0:
                st.map(map_df, zoom=8, color='#FF4B4B')
                
                # Legend
                st.markdown("""
                **Legend:**
                - 🟢 Green: Has email + headteacher + pupil premium (best for business)
                - 🟠 Orange: Has email collected
                - 🔴 Red: No email yet
                """)
            
            # School list
            st.subheader("📋 Schools")
            for _, school in map_df.head(30).iterrows():
                emoji = "🟢" if school['status'] == 'green' else "🟠" if school['status'] == 'orange' else "🔴"
                with st.expander(f"{emoji} {school['name']} ({school['town']})"):
                    st.write(f"**Town:** {school['town']}")
                    st.write(f"**Status:** {school['status']}")
                    if school['email'] != 'N/A':
                        st.write(f"**Email:** {school['email']}")
                    if school['head']:
                        st.write(f"**Head:** {school['head']}")
                    st.write(f"**Pupil Premium:** {'Yes' if school['has_pp'] else 'No'}")

else:
    st.warning("Data not available")

# Stats sidebar
st.sidebar.header("📊 Coverage")
st.sidebar.write("Leicester: ✅ 381 schools")
st.sidebar.write("Nottingham: ✅ 334 schools")  
st.sidebar.write("Derbyshire: ✅ 485 schools")
st.sidebar.write("Warwickshire: ✅ 239 schools")
st.sidebar.write("---")
st.sidebar.write("**Total: 1,439 schools**")
