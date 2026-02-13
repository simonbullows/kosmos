#!/usr/bin/env python3
"""
Charity Commission Data Collector
FREE - Official UK Charity Register
https://register-of-charities.charitycommission.gov.uk/
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "https://api.charitycommission.gov.uk/api/v1"
DATA_DIR = "/home/ubuntu/.openclaw/workspace/kosmos/data/charities"
OUTPUT_FILE = os.path.join(DATA_DIR, "charities.json")

# API requires registration
# Basic data available via downloads at:
# https://register-of-charity-commissioners.data.gov.uk/

API_KEY = os.environ.get("CHARITY_COMMISSION_API_KEY", "")
HEADERS = {"ApiKey": API_KEY} if API_KEY else {}


def download_charities_csv():
    """
    Download full charity register (updated monthly)
    Free download from Charity Commission
    """
    # Main data download page
    download_url = "https://register-of-charity-commissioners.data.gov.uk/"
    
    print(f"Data available at: {download_url}")
    print("\nNote: Full CSV download requires visiting the page and clicking download.")
    print("Alternative: Use the API for targeted searches.")
    
    return None


def search_charities(query="", registered_before=None, 
                    income_min=None, income_max=None,
                    size=100):
    """
    Search charities via API
    """
    endpoint = f"{BASE_URL}/search"
    
    params = {
        "search": query,
        "size": min(size, 500)
    }
    
    try:
        response = requests.get(
            endpoint,
            headers=HEADERS,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def get_charity_details(charity_number):
    """Get detailed info for a single charity"""
    endpoint = f"{BASE_URL}/charity/{charity_number}"
    
    try:
        response = requests.get(
            endpoint,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"Charity {charity_number} not found")
            return None
        else:
            print(f"Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def get_charity_trustees(charity_number):
    """Get trustees for a charity"""
    endpoint = f"{BASE_URL}/charity/{charity_number}/trustees"
    
    try:
        response = requests.get(
            endpoint,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def get_charity_financials(charity_number):
    """Get financial data for a charity"""
    endpoint = f"{BASE_URL}/charity/{charity_number}/financial"
    
    try:
        response = requests.get(
            endpoint,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def parse_charity_record(data):
    """Parse charity API response into standardized format"""
    return {
        "charity_number": data.get("charityNumber"),
        "name": data.get("charityName"),
        "registration_status": data.get("registrationStatus"),
        "registration_date": data.get("registrationDate"),
        "removal_date": data.get("removalDate"),
        "charity_type": data.get("charityType"),
        "operational": data.get("operational"),
        "sub_charity": data.get("subCharity"),
        "address": {
            "street": data.get("addressLine1", ""),
            "address_line_2": data.get("addressLine2", ""),
            "city": data.get("townCity", ""),
            "county": data.get("county", ""),
            "postcode": data.get("postcode", ""),
            "country": data.get("country", "")
        },
        "phone": data.get("phoneNumber", ""),
        "website": data.get("website", ""),
        "email": data.get("emailAddress", ""),
        "trustees_count": data.get("numberOfTrustees"),
        "activities": data.get("activities", ""),
        "beneficiaries": data.get("beneficiaries", ""),
        "source": "Charity Commission API",
        "collected_at": datetime.now().isoformat()
    }


def collect_sample_charities(count=100):
    """Collect sample charities for testing"""
    charities = []
    
    print("=" * 50)
    print("KOSMOS - Charity Commission Data Collector")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Get top charities by income (example)
    print("\nSearching for charities...")
    
    results = search_charities(size=50)
    
    if results:
        for item in results.get("charities", [])[:count]:
            charity_number = item.get("charityNumber")
            
            if charity_number:
                details = get_charity_details(charity_number)
                
                if details:
                    charity = parse_charity_record(details)
                    
                    # Get trustees
                    trustees = get_charity_trustees(charity_number)
                    if trustees:
                        charity["trustees"] = trustees.get("trustees", [])
                    
                    charities.append(charity)
                    print(f"✓ {charity['name']}")
                    
                    time.sleep(0.5)  # Rate limiting
    
    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(charities, f, indent=2)
    
    print(f"\n✓ Saved {len(charities)} charities to {OUTPUT_FILE}")
    
    return charities


def get_charity_summaries():
    """Get summary data for all charities"""
    # The full register is ~170,000 charities
    # Best approached by collecting in batches
    
    print("\nNote: Full charity collection requires:")
    print("1. API key registration (free)")
    print("2. Processing the monthly CSV download")
    print("3. Or targeted searches by criteria")
    
    return None


if __name__ == "__main__":
    # For demo, try API collection
    collect_sample_charities(20)
