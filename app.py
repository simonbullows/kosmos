import streamlit as st
import pandas as pd
import urllib.request
import io
import json
from datetime import datetime

st.set_page_config(page_title="KOSMOS CRM", layout="wide", page_icon="🔗")

# Session state for CRM data
if 'contacts' not in st.session_state:
    st.session_state.contacts = {}
if 'lists' not in st.session_state:
    st.session_state.lists = {"Favorites": [], "To Contact": [], "Contacted": [], "Interested": []}
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'activity' not in st.session_state:
    st.session_state.activity = []

# Load data from GitHub
@st.cache_data
def load_companies():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/kosmos_csr_export.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    df['type'] = 'Company'
    return df

@st.cache_data
def load_schools():
    url = "https://raw.githubusercontent.com/simonbullows/kosmos/master/data/schools_export.csv"
    df = pd.read_csv(io.StringIO(urllib.request.urlopen(url).read().decode('utf-8')))
    df['type'] = 'School'
    return df

companies = load_companies()
schools = load_schools()

# All contacts
all_contacts = pd.concat([companies, schools], ignore_index=True)
all_contacts['display'] = all_contacts.apply(lambda x: f"{x['name'][:45]} | {x['town'] or 'N/A'}", axis=1)

# Sidebar navigation
st.sidebar.title("🔗 KOSMOS CRM")
page = st.sidebar.radio("Navigate", ["Contacts", "Lists", "Pipeline", "Activity", "Settings"])

# ===== CONTACTS PAGE =====
if page == "Contacts":
    st.title("📇 Contacts")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Filter")
        search = st.text_input("🔍 Search", "")
        
        # Type filter
        contact_type = st.multiselect("Type", ["Company", "School"], default=["Company", "School"])
        
        # Category filter
        categories = sorted(all_contacts['category'].dropna().unique())
        selected_cats = st.multiselect("Category", categories)
        
        # Town filter
        towns = sorted(all_contacts['town'].dropna().unique())
        selected_towns = st.multiselect("Town", towns[:50])
        
        # Status filter
        status = st.selectbox("Status", ["All", "New", "Contacted", "Interested", "Not Interested"])
    
    # Filter data
    df = all_contacts.copy()
    
    if search:
        df = df[df['name'].str.contains(search, case=False, na=False)]
    
    if contact_type:
        df = df[df['type'].isin(contact_type)]
    
    if selected_cats:
        df = df[df['category'].isin(selected_cats)]
    
    if selected_towns:
        df = df[df['town'].isin(selected_towns)]
    
    st.markdown(f"**{len(df):,} contacts**")
    
    with col2:
        # Contact selector
        if len(df) > 0:
            selected = st.selectbox("Select contact", df['display'].unique())
            
            if selected:
                contact = df[df['display'] == selected].iloc[0]
                
                st.markdown("---")
                st.subheader(contact['name'])
                
                # Details
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Type:** {contact['type']}")
                c2.write(f"**Category:** {contact.get('category', 'N/A')}")
                c3.write(f"**Town:** {contact.get('town', 'N/A')}")
                
                c1, c2 = st.columns(2)
                c1.write(f"**Postcode:** {contact.get('postcode', 'N/A')}")
                c2.write(f"**County:** {contact.get('county', 'N/A')}")
                
                # Actions
                st.markdown("### Actions")
                ac1, ac2, ac3, ac4 = st.columns(4)
                ac1.button("⭐ Add to Favorites", key="fav")
                ac2.button("📋 Add to List", key="add_list")
                ac3.button("📝 Add Note", key="note")
                ac4.button("📧 Send Email", key="email")
                
                # Notes section
                st.markdown("### Notes")
                if st.text_area("Add a note", key="note_text"):
                    if 'notes' not in st.session_state:
                        st.session_state.notes = {}
                    st.session_state.notes[contact['name']] = st.session_state.note_text
                    st.success("Note saved!")

# ===== LISTS PAGE =====
elif page == "Lists":
    st.title("📋 Contact Lists")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### My Lists")
        
        # Create new list
        new_list = st.text_input("New list name")
        if st.button("Create List"):
            if new_list and new_list not in st.session_state.lists:
                st.session_state.lists[new_list] = []
                st.success(f"Created: {new_list}")
        
        # List selection
        selected_list = st.radio("Select list", list(st.session_state.lists.keys()))
    
    with col2:
        if selected_list:
            contacts = st.session_state.lists[selected_list]
            st.markdown(f"### {selected_list} ({len(contacts)} contacts)")
            
            # Add contacts
            add_contact = st.selectbox("Add contact", all_contacts['display'].unique()[:100])
            if st.button("Add"):
                if add_contact not in contacts:
                    contacts.append(add_contact)
                    st.session_state.lists[selected_list] = contacts
                    st.success(f"Added: {add_contact}")
            
            # Show contacts
            if contacts:
                for i, c in enumerate(contacts):
                    c1, c2 = st.columns([4, 1])
                    c1.write(c)
                    if c2.button("🗑️", key=f"del_{i}"):
                        contacts.pop(i)
                        st.session_state.lists[selected_list] = contacts
                        st.rerun()
            
            # Export list
            if st.button("Export List"):
                st.markdown("### Export")
                st.code(json.dumps(contacts), language="json")

# ===== PIPELINE PAGE =====
elif page == "Pipeline":
    st.title("📊 Pipeline")
    
    # Pipeline stages
    stages = ["New", "Contacted", "Interested", "Proposal", "Negotiation", "Won", "Lost"]
    
    # Sample pipeline data
    pipeline_data = {
        "New": ["Acme Corp", "TechStart Ltd"],
        "Contacted": ["BigCo Industries", "Local Council"],
        "Interested": ["Charity ABC"],
        "Proposal": [],
        "Negotiation": [],
        "Won": [],
        "Lost": []
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Drag and drop (simulated with selectbox)
        st.markdown("### Manage Pipeline")
        
        for stage in stages:
            st.markdown(f"**{stage}** ({len(pipeline_data[stage])})")
            if pipeline_data[stage]:
                for company in pipeline_data[stage]:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"  {company}")
                    c2.selectbox("", ["Move →"], key=f"move_{company}")
            st.markdown("---")

# ===== ACTIVITY PAGE =====
elif page == "Activity":
    st.title("📝 Activity Log")
    
    # Sample activity
    activity = [
        {"date": "2026-02-13", "action": "Contacted", "company": "Acme Corp", "notes": "Initial outreach"},
        {"date": "2026-02-12", "action": "Email sent", "company": "TechStart Ltd", "notes": "Follow up"},
        {"date": "2026-02-11", "action": "Meeting", "company": "Local Council", "notes": "Discussed partnership"},
    ]
    
    # Log new activity
    with st.form("add_activity"):
        st.markdown("### Log Activity")
        c1, c2 = st.columns(2)
        company = c1.selectbox("Company", all_contacts['name'].unique()[:100])
        action = c2.selectbox("Action", ["Contacted", "Email sent", "Called", "Meeting", "Follow up"])
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Log Activity"):
            activity.insert(0, {"date": datetime.now().strftime("%Y-%m-%d"), "action": action, "company": company, "notes": notes})
            st.success("Activity logged!")
    
    # Show activity
    st.markdown("### Recent Activity")
    for a in activity:
        st.markdown(f"**{a['date']}** - {a['action']} - {a['company']}")
        st.caption(a['notes'])
        st.markdown("---")

# ===== SETTINGS PAGE =====
elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.markdown("### Data Sources")
    st.write(f"Companies: {len(companies):,}")
    st.write(f"Schools: {len(schools):,}")
    st.write(f"Total: {len(all_contacts):,}")
    
    st.markdown("### Export Data")
    if st.button("Export All Contacts"):
        csv = all_contacts.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "kosmos_contacts.csv", "text/csv")
    
    st.markdown("### Import Data")
    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.write(f"Imported: {len(df)} contacts")

# Sidebar stats
st.sidebar.markdown("---")
st.sidebar.metric("Total Contacts", f"{len(all_contacts):,}")
st.sidebar.metric("Companies", f"{len(companies):,}")
st.sidebar.metric("Schools", f"{len(schools):,}")
