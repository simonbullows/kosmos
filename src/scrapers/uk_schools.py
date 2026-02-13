#!/usr/bin/env python3
"""
UK Schools Data Collector
FREE - Get Information About Schools (DfE)
https://get-information-schools.service.gov.uk/
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "https://get-information-schools.service.gov.uk"
DATA_DIR = "/home/ubuntu/.openclaw/workspace/kosmos/data/education"
OUTPUT_FILE = os.path.join(DATA_DIR, "uk_schools.json")

# Note: No API key required for downloads
# For API access: https://find-and-use-an-api.education.gov.uk/


def download_schools_csv():
    """
    Download all schools CSV from DfE
    Updated daily, includes all school types
    """
    # Main download URL for establishments
    csv_url = f"{BASE_URL}/Downloads/Establishments.csv"
    
    print(f"Downloading from: {csv_url}")
    
    try:
        response = requests.get(csv_url, timeout=300)  # 5 min timeout for large file
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error downloading: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def download_groups_csv():
    """Download academy trusts/groups"""
    groups_url = f"{BASE_URL}/Downloads/Groups.csv"
    
    print(f"Downloading from: {groups_url}")
    
    try:
        response = requests.get(groups_url, timeout=300)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error downloading: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def parse_schools_csv(csv_text):
    """Parse CSV and convert to structured JSON"""
    import csv
    from io import StringIO
    
    schools = []
    reader = csv.DictReader(StringIO(csv_text))
    
    for row in reader:
        school = {
            "urn": row.get("URN", ""),
            "uid": row.get("UID", ""),
            "name": row.get("EstablishmentName", ""),
            "type": row.get("TypeOfEstablishment", ""),
            "type_group": row.get("EstablishmentTypeGroup", ""),
            "phase": row.get("PhaseOfEducation", ""),
            "gender": row.get("Gender", ""),
            "religious_character": row.get("ReligiousCharacter", ""),
            "diocese": row.get("Diocese", ""),
            "admissions_policy": row.get("AdmissionsPolicy", ""),
            "school_capacity": row.get("SchoolCapacity", ""),
            "statutory_low_age": row.get("StatutoryLowAge", ""),
            "statutory_high_age": row.get("StatutoryHighAge", ""),
            "nursery_provision": row.get("NurseryProvision", ""),
            "ofsted_rating": row.get("OverallEffectiveness", ""),
            "last_ofsted": row.get("LastInspection", ""),
            "address": {
                "street": row.get("Street", ""),
                "locality": row.get("Locality", ""),
                "address3": row.get("Address3", ""),
                "town": row.get("Town", ""),
                "county": row.get("County", ""),
                "postcode": row.get("Postcode", "")
            },
            "contact": {
                "telephone": row.get("TelephoneNum", ""),
                "fax": row.get("FaxNum", ""),
                "website": row.get("Website", ""),
                "email": row.get("Email", "")
            },
            "head": {
                "name": row.get("HeadTitle", "") + " " + row.get("HeadFirstName", "") + " " + row.get("HeadLastName", ""),
                "role": row.get("HeadPreferredJobTitle", "")
            },
            "local_authority": {
                "code": row.get("LA", ""),
                "name": row.get("LAName", "")
            },
            "region": row.get("Region", ""),
            "open_date": row.get("OpenDate", ""),
            "close_date": row.get("CloseDate", ""),
            "source_url": f"{BASE_URL}/Establishments/Establishment/Details/{row.get('URN', '')}",
            "collected_at": datetime.now().isoformat()
        }
        
        # Clean up empty values
        school = {k: v for k, v in school.items() if v and v != "None"}
        schools.append(school)
    
    return schools


def search_schools_by_la(la_code):
    """Search schools by local authority code"""
    search_url = f"{BASE_URL}/Downloads"
    
    # LA codes are embedded in the full download
    # For LA-specific, we'd need to filter the full CSV
    
    print(f"Note: LA-specific downloads not available directly.")
    print(f"Will filter by LA code '{la_code}' from full CSV.")


def get_school_details(urn):
    """Get detailed info for a single school via API"""
    # API requires DfE Sign-in for full access
    # Basic info available via the establishment URL
    
    url = f"{BASE_URL}/Establishments/Establishment/Details/{urn}"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return {"url": url, "status": "available"}
        else:
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def collect_all_schools():
    """Main collection function"""
    print("=" * 50)
    print("KOSMOS - UK Schools Data Collector")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Download establishments (schools)
    print("\n1. Downloading schools CSV...")
    csv_text = download_schools_csv()
    
    if csv_text:
        schools = parse_schools_csv(csv_text)
        
        # Save JSON
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(schools, f, indent=2)
        
        print(f"\n✓ Saved {len(schools)} schools to {OUTPUT_FILE}")
        
        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Total schools: {len(schools)}")
        
        # Count by type
        types = {}
        for school in schools:
            t = school.get("type_group", "Unknown")
            types[t] = types.get(t, 0) + 1
        
        print("\nBy establishment type group:")
        for t, count in sorted(types.items(), key=lambda x: -x[1]):
            print(f"  {t}: {count}")
        
        # Count by phase
        phases = {}
        for school in schools:
            p = school.get("phase", "Unknown")
            phases[p] = phases.get(p, 0) + 1
        
        print("\nBy phase of education:")
        for p, count in sorted(phases.items(), key=lambda x: -x[1]):
            print(f"  {p}: {count}")
        
        # Count by region
        regions = {}
        for school in schools:
            r = school.get("region", "Unknown")
            regions[r] = regions.get(r, 0) + 1
        
        print("\nBy region:")
        for r, count in sorted(regions.items(), key=lambda x: -x[1])[:10]:
            print(f"  {r}: {count}")
        
        return schools
    
    else:
        print("\n✗ Failed to download schools data")
        return []


if __name__ == "__main__":
    collect_all_schools()
