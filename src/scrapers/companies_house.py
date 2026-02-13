#!/usr/bin/env python3
"""
Companies House API Collector
FREE - No API key required for basic search
https://developer.company-information.service.gov.uk/
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "https://api.company-information.service.gov.uk"
DATA_DIR = "/home/ubuntu/.openclaw/workspace/kosmos/data/businesses"
OUTPUT_FILE = os.path.join(DATA_DIR, "companies_house.json")

# Companies House API key (register for free at above URL)
# Without key: 150 requests/5 seconds, 15,000 requests/day
# With key: 600 requests/10 seconds, 500,000 requests/day
API_KEY = os.environ.get("COMPANIES_HOUSE_API_KEY", "")

HEADERS = {
    "Accept": "application/json"
}

if API_KEY:
    HEADERS["Authorization"] = API_KEY


def search_companies(query="", sector=None, location=None, size="large", limit=100):
    """
    Search for companies
    size: "large" (250+ employees), "medium" (50-249), "small" (10-49), "micro" (0-9)
    """
    results = []
    start_index = 0
    
    while start_index < limit:
        params = {
            "q": query,
            "start_index": start_index,
            "items_per_page": min(100, limit - start_index)
        }
        
        if sector:
            params["sic_codes"] = sector
        
        if location:
            params["registered_office_address"] = location
        
        try:
            response = requests.get(
                f"{BASE_URL}/search/companies",
                headers=HEADERS,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                results.extend(items)
                
                total = data.get("total_results", 0)
                print(f"Found {len(items)} companies (total: {total})")
                
                if len(items) < 100:
                    break
                    
                start_index += 100
                time.sleep(1)  # Rate limiting
                
            elif response.status_code == 429:
                print("Rate limited, waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                break
                
        except Exception as e:
            print(f"Exception: {e}")
            break
    
    return results


def get_company_details(company_number):
    """Get detailed info for a single company"""
    try:
        response = requests.get(
            f"{BASE_URL}/company/{company_number}",
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting {company_number}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def get_company_officers(company_number):
    """Get directors/officers for a company"""
    try:
        response = requests.get(
            f"{BASE_URL}/company/{company_number}/officers",
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


def get_filing_history(company_number, limit=10):
    """Get recent filing history"""
    try:
        response = requests.get(
            f"{BASE_URL}/company/{company_number}/filing-history",
            headers=HEADERS,
            params={"items_per_page": limit},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None


def collect_top_companies(industry=None, count=500):
    """
    Collect top companies by industry
    Industry SIC codes:
    - 64-66: Financial services
    - 72: Scientific research
    - 85: Education
    - 86-88: Healthcare
    """
    companies = []
    
    if industry:
        results = search_companies(sector=industry, limit=count)
    else:
        # Get large companies (250+ employees)
        results = search_companies(size="large", limit=count)
    
    for company in results:
        company_number = company.get("company_number")
        
        if company_number:
            # Get detailed info
            details = get_company_details(company_number)
            if details:
                # Get officers (directors)
                officers = get_company_officers(company_number)
                
                record = {
                    "company_number": company_number,
                    "name": details.get("company_name"),
                    "type": details.get("type"),
                    "status": details.get("status"),
                    "incorporation_date": details.get("incorporation_date"),
                    "dissolution_date": details.get("dissolution_date"),
                    "address": details.get("registered_office_address", {}),
                    "sic_codes": details.get("sic_codes", []),
                    "industry": details.get("industry_description", ""),
                    "website": details.get("company_uri"),
                    "officers": officers.get("items", []) if officers else [],
                    "source": "Companies House API",
                    "collected_at": datetime.now().isoformat()
                }
                
                companies.append(record)
                print(f"✓ {record['name']}")
                
                time.sleep(0.5)  # Rate limiting
    
    return companies


if __name__ == "__main__":
    print("=" * 50)
    print("KOSMOS - Companies House Data Collector")
    print("=" * 50)
    print(f"\nOutput directory: {DATA_DIR}")
    print(f"API key set: {'Yes' if API_KEY else 'No (rate limited)'}")
    
    # Create directory
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Collect top UK companies
    print("\nCollecting top UK companies...")
    companies = collect_top_companies(industry=None, count=100)
    
    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(companies, f, indent=2)
    
    print(f"\n✓ Saved {len(companies)} companies to {OUTPUT_FILE}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Companies collected: {len(companies)}")
    
    # Count by industry
    industries = {}
    for c in companies:
        ind = c.get("industry", "Unknown")
        industries[ind] = industries.get(ind, 0) + 1
    
    print("\nBy industry:")
    for ind, count in sorted(industries.items(), key=lambda x: -x[1])[:10]:
        print(f"  {ind}: {count}")
