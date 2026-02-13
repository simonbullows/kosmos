#!/usr/bin/env python3
"""
UK Parliament API Collector
FREE - Official UK Parliament Open Data
https://developer.parliament.uk/
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "https://api.parliament.uk"
DATA_DIR = "/home/ubuntu/.openclaw/workspace/kosmos/data/politics"
OUTPUT_FILE = os.path.join(DATA_DIR, "parliament.json")

# No API key required for basic endpoints
# Rate limit: 200 requests/10 seconds
# Register for higher limits: https://developer.parliament.uk/

HEADERS = {
    "Accept": "application/json"
}

# Resources
MEMENTS_API = "https://api.parliament.uk/historic-mp-api"


def get_all_mps():
    """Get all current MPs"""
    endpoint = f"{BASE_URL}/historic-mp-api/v1/members"
    
    mps = []
    page = 1
    per_page = 200
    
    while True:
        try:
            response = requests.get(
                endpoint,
                headers=HEADERS,
                params={"page": page, "size": per_page},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    break
                
                for item in items:
                    mp = {
                        "id": item.get("value", {}).get("id", ""),
                        "full_title": item.get("value", {}).get("fullTitle", ""),
                        "name": item.get("value", {}).get("name", {}).get("listAs", ""),
                        "first_name": item.get("value", {}).get("name", {}).get("firstName", ""),
                        "last_name": item.get("value", {}).get("name", {}).get("lastName", ""),
                        "gender": item.get("value", {}).get("gender", ""),
                        "birth_date": item.get("value", {}).get("dateOfBirth", ""),
                        "house": item.get("value", {}).get("house", ""),
                        "party": item.get("value", {}).get("party", {}).get("name", ""),
                        "constituency": item.get("value", {}).get("constituency", {}).get("name", ""),
                        "from_date": item.get("value", {}).get("fromDate", ""),
                        "source": "UK Parliament API",
                        "collected_at": datetime.now().isoformat()
                    }
                    mps.append(mp)
                
                print(f"Page {page}: {len(items)} MPs")
                
                if len(items) < per_page:
                    break
                    
                page += 1
                time.sleep(0.5)
                
            else:
                print(f"Error: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Exception: {e}")
            break
    
    return mps


def get_mp_details(mp_id):
    """Get detailed info for a specific MP"""
    endpoint = f"{BASE_URL}/historic-mp-api/v1/members/{mp_id}"
    
    try:
        response = requests.get(endpoint, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def get_all_lords():
    """Get all current Lords"""
    endpoint = f"{BASE_URL}/historic-lords-api/v1/members"
    
    lords = []
    page = 1
    per_page = 200
    
    while True:
        try:
            response = requests.get(
                endpoint,
                headers=HEADERS,
                params={"page": page, "size": per_page},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    break
                
                for item in items:
                    lord = {
                        "id": item.get("value", {}).get("id", ""),
                        "full_title": item.get("value", {}).get("fullTitle", ""),
                        "name": item.get("value", {}).get("name", {}).get("listAs", ""),
                        "title": item.get("value", {}).get("name", {}).get("title", ""),
                        "first_name": item.get("value", {}).get("name", {}).get("firstName", ""),
                        "last_name": item.get("value", {}).get("name", {}).get("lastName", ""),
                        "party": item.get("value", {}).get("party", {}).get("name", ""),
                        "lords_type": item.get("value", {}).get("lordsType", ""),
                        "from_date": item.get("value", {}).get("fromDate", ""),
                        "source": "UK Parliament API",
                        "collected_at": datetime.now().isoformat()
                    }
                    lords.append(lord)
                
                print(f"Page {page}: {len(lords)} Lords total")
                
                if len(items) < per_page:
                    break
                    
                page += 1
                time.sleep(0.5)
                
            else:
                print(f"Error: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Exception: {e}")
            break
    
    return lords


def get_constituencies():
    """Get all UK constituencies"""
    endpoint = f"{BASE_URL}/election-results/api/v1/constituencies"
    
    try:
        response = requests.get(endpoint, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def collect_parliament_data():
    """Main collection function"""
    print("=" * 50)
    print("KOSMOS - UK Parliament Data Collector")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    all_politicians = []
    
    # Collect MPs
    print("\n1. Collecting MPs...")
    mps = get_all_mps()
    print(f"✓ Collected {len(mps)} MPs")
    
    for mp in mps:
        mp["type"] = "MP"
        all_politicians.append(mp)
    
    # Collect Lords
    print("\n2. Collecting Lords...")
    lords = get_all_lords()
    print(f"✓ Collected {len(lords)} Lords")
    
    for lord in lords:
        lord["type"] = "Lord"
        all_politicians.append(lord)
    
    # Save combined data
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_politicians, f, indent=2)
    
    print(f"\n✓ Saved {len(all_politicians)} politicians to {OUTPUT_FILE}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total politicians: {len(all_politicians)}")
    print(f"  MPs: {len(mps)}")
    print(f"  Lords: {len(lords)}")
    
    # Count by party
    parties = {}
    for p in all_politicians:
        party = p.get("party", "Unknown")
        parties[party] = parties.get(party, 0) + 1
    
    print("\nBy party:")
    for party, count in sorted(parties.items(), key=lambda x: -x[1])[:10]:
        print(f"  {party}: {count}")
    
    return all_politicians


if __name__ == "__main__":
    collect_parliament_data()
