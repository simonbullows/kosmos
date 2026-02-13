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

# Load region
@st.cache_data
def load_region(region):
    urls = {
        'Leicester': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/leicester_schools_enriched.csv',
        'Nottingham': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/nottingham_schools_enriched.csv',
        'Derbyshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/derbyshire_schools_enriched.csv',
        'Warwickshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/warwickshire_schools_enriched.csv',
        'Staffordshire': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/staffordshire_schools_enriched.csv',
        'Birmingham': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/birmingham_schools_enriched.csv',
        'Dudley': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/dudley_schools_enriched.csv',
        'Walsall': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/walsall_schools_enriched.csv',
        'Wolverhampton': 'https://raw.githubusercontent.com/simonbullows/kosmos/master/data/wolverhampton_schools_enriched.csv',
        'All Regions': 'ALL'
    }
    
    if region == 'All Regions':
        dfs = []
        for r, url in urls.items():
            if r == 'All Regions': continue
            try:
                df_r = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
                df_r['region'] = r
                dfs.append(df_r)
            except:
                pass
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return None
    
    if region not in urls:
        return None
    
    try:
        df = pd.read_csv(io.StringIO(urllib.request.urlopen(urls[region]).read().decode('utf-8')))
        df['region'] = region
        return df
    except:
        return None

st.title("🗺️ KOSMOS Schools Map")

# Region selector
regions = ['All Regions', 'Leicester', 'Nottingham', 'Derbyshire', 'Warwickshire', 
           'Staffordshire', 'Birmingham', 'Dudley', 'Walsall', 'Wolverhampton']
selected_region = st.selectbox("Select Region", regions)

df = load_region(selected_region)

if df is not None:
    # Determine status - only green if ALL three: email + headteacher + pupil premium confirmed
    def get_status(row):
        has_email = pd.notna(row.get('email', '')) and str(row.get('email', '')).strip() != ''
        has_head = pd.notna(row.get('head_first_name', '')) or pd.notna(row.get('head_last_name', ''))
        has_pp = row.get('has_pupil_premium', False) == True or row.get('has_pupil_premium', '') == True
        
        if has_email and has_head and has_pp:
            return 'green'
        elif has_email:
            return 'orange'
        else:
            return 'red'
    
    df['status'] = df.apply(get_status, axis=1)
    
    # Stats
    total = len(df)
    green = len(df[df['status'] == 'green'])
    orange = len(df[df['status'] == 'orange'])
    red = len(df[df['status'] == 'red'])
    send_count = df['has_send'].sum() if 'has_send' in df.columns else 0
    ofsted_count = df['ofsted_rating'].notna().sum() if 'ofsted_rating' in df.columns else 0
    
    st.subheader(f"📊 {selected_region}")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total", total)
    col2.metric("🟢 Complete", green, delta=f"{green/total*100:.0f}%" if total else "0%")
    col3.metric("🟠 Email Only", orange, delta=f"{orange/total*100:.0f}%" if total else "0%")
    col4.metric("🔴 None", red, delta=f"{red/total*100:.0f}%" if total else "0%")
    col5.metric("⭐ Ofsted", ofsted_count, delta=f"{ofsted_count/total*100:.0f}%" if total else "0%")
    col6.metric("♿ SEND", send_count, delta=f"{send_count/total*100:.0f}%" if total else "0%")
    
    # Map
    map_data = []
    for _, row in df.iterrows():
        lat, lon = geocode_uk(row.get('postcode', ''))
        if lat:
            map_data.append({
                'lat': lat,
                'lon': lon,
                'name': str(row.get('name', '')),
                'town': str(row.get('town', '')),
                'status': row.get('status', 'red'),
                # All fields
                'email': str(row.get('email', '')) if pd.notna(row.get('email', '')) else 'MISSING',
                'phone': str(row.get('phone', '')) if pd.notna(row.get('phone', '')) else 'MISSING',
                'website': str(row.get('website', '')) if pd.notna(row.get('website', '')) else 'MISSING',
                'head_title': str(row.get('head_title', '')) if pd.notna(row.get('head_title', '')) else '',
                'head_first_name': str(row.get('head_first_name', '')) if pd.notna(row.get('head_first_name', '')) else '',
                'head_last_name': str(row.get('head_last_name', '')) if pd.notna(row.get('head_last_name', '')) else '',
                'head_job_title': str(row.get('head_job_title', '')) if pd.notna(row.get('head_job_title', '')) else '',
                'type': str(row.get('type', '')) if pd.notna(row.get('type', '')) else 'MISSING',
                'postcode': str(row.get('postcode', '')) if pd.notna(row.get('postcode', '')) else 'MISSING',
                # Address fields
                'street': str(row.get('street', '')) if pd.notna(row.get('street', '')) else '',
                'locality': str(row.get('locality', '')) if pd.notna(row.get('locality', '')) else '',
                'county': str(row.get('county', '')) if pd.notna(row.get('county', '')) else '',
                'has_pupil_premium': row.get('has_pupil_premium', False),
                'has_financial_reports': row.get('has_financial_reports', False),
                'all_emails': str(row.get('all_emails', '')) if pd.notna(row.get('all_emails', '')) else '',
                'staff_contacts': str(row.get('staff_contacts', '')) if pd.notna(row.get('staff_contacts', '')) else '',
                # New enrichment fields
                'ofsted_rating': str(row.get('ofsted_rating', '')) if pd.notna(row.get('ofsted_rating', '')) else '',
                'has_send': row.get('has_send', False),
                'governors': str(row.get('governors', '')) if pd.notna(row.get('governors', '')) else '',
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        st.map(map_df, zoom=8)
        
        st.caption("🟢 = Email + Headteacher + Pupil Premium | 🟠 = Email only | 🔴 = No email | ⭐ = Ofsted rated | ♿ = SEND support")
        
        # Search
        search = st.text_input("Search schools", "")
        if search:
            map_df = map_df[map_df['name'].str.contains(search, case=False, na=False)]
        
        st.metric("Showing", len(map_df))
        
        # Show ALL data for each school
        for _, school in map_df.head(30).iterrows():
            emoji = "🟢" if school['status'] == 'green' else "🟠" if school['status'] == 'orange' else "🔴"
            
            with st.expander(f"{emoji} {school['name']}"):
                # Basic info
                col1, col2 = st.columns(2)
                col1.write(f"**Type:** {school['type']}")
                col2.write(f"**Town:** {school['town']}")
                
                # Address
                st.write("---")
                st.write("**📍 Address:**")
                parts = []
                if school.get('street'):
                    parts.append(str(school.get('street', '')))
                if school.get('locality'):
                    parts.append(str(school.get('locality', '')))
                if school.get('town'):
                    parts.append(str(school.get('town', '')))
                if school.get('county'):
                    parts.append(str(school.get('county', '')))
                if school.get('postcode'):
                    parts.append(str(school.get('postcode', '')))
                
                address = ', '.join([p for p in parts if p and p != 'nan'])
                if address:
                    st.write(f"  {address}")
                else:
                    st.write("  ❌ MISSING")
                
                # Contact
                st.write("---")
                st.write("**📧 Contact:**")
                email = school['email'] if school['email'] != 'MISSING' else '❌ MISSING'
                st.write(f"  Email: {email}")
                
                website = school['website'] if school['website'] != 'MISSING' else '❌ MISSING'
                st.write(f"  Website: {website}")
                
                # Headteacher
                st.write("---")
                st.write("**👤 Headteacher:**")
                head = f"{school['head_title']} {school['head_first_name']} {school['head_last_name']}".strip()
                if head:
                    st.write(f"  Name: {head}")
                else:
                    st.write("  Name: ❌ MISSING")
                
                if school['head_job_title']:
                    st.write(f"  Title: {school['head_job_title']}")
                
                # Pupil Premium
                st.write("---")
                st.write("**💰 Pupil Premium:**")
                pp = school['has_pupil_premium']
                st.write(f"  Status: {'✅ Yes' if pp else '❌ No/Unknown'}")
                
                # Financial
                fin = school['has_financial_reports']
                st.write(f"  Financial Reports: {'✅ Yes' if fin else '❌ No/Unknown'}")
                
                # All emails
                if school['all_emails']:
                    st.write("---")
                    st.write("**📬 All Emails:**")
                    st.write(f"  {school['all_emails']}")
                
                # NEW: Ofsted, SEND, Governors
                st.write("---")
                st.write("**🏫 Ofsted & SEND:**")
                ofsted = school.get('ofsted_rating', '')
                st.write(f"  Rating: {ofsted if ofsted else '❌ Not found'}")
                send = school.get('has_send', False)
                st.write(f"  SEND Support: {'✅ Yes' if send else '❌ No/Unknown'}")
                
                if school.get('governors'):
                    st.write("---")
                    st.write("**👥 Governors:**")
                    st.write(f"  {school['governors']}")

# Sidebar
st.sidebar.header("📊 All Regions")
st.sidebar.write("🗺️ **All Regions:** 2,488 schools")
st.sidebar.write("Leicester: 381 | Nottingham: 334")
st.sidebar.write("Derbyshire: 485 | Warwickshire: 239")
st.sidebar.write("Staffordshire: 303 | Birmingham: 301")
st.sidebar.write("Dudley: 78 | Walsall: 85 | Wolverhampton: 72")
st.sidebar.write("---")
st.sidebar.write("**New Data Available:**")
st.sidebar.write("• Ofsted ratings (enriched regions)")
st.sidebar.write("• SEND facilities (enriched regions)")
st.sidebar.write("• Governor names (enriched regions)")
