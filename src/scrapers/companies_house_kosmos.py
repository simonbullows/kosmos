#!/usr/bin/env python3
"""
KOSMOS Companies House Collector
FREE API - No authentication needed for basic search
https://developer.company-information.service.gov.uk/
"""

import requests
import json
import time
from datetime import datetime
import os

BASE_URL = "https://api.company-information.service.gov.uk"
OUTPUT_DIR = "/home/ubuntu/.openclaw/workspace/kosmos/data/businesses"
DATA_FILE = os.path.join(OUTPUT_DIR, "companies.json")

# API key for higher limits (register for free)
API_KEY = os.environ.get("COMPANIES_HOUSE_API_KEY", "")

HEADERS = {"Accept": "application/json"}
if API_KEY:
    HEADERS["Authorization"] = API_KEY

# Rate limits: No key = 150 req/5sec, 15000/day | With key = 600 req/10sec, 500000/day


def search_companies(query="", size="large", limit=500):
    """
    Search for companies
    size: "large" (250+ employees), "medium" (50-249), "small" (10-49), "micro" (0-9)
    """
    companies = []
    start_index = 0
    
    while start_index < limit:
        params = {
            "q": query if query else "company",
            "size": size,
            "start_index": start_index,
            "items_per_page": min(100, limit - start_index)
        }
        
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
                
                for company in items:
                    record = {
                        "company_number": company.get("company_number"),
                        "name": company.get("company_name"),
                        "type": company.get("type"),
                        "status": company.get("status"),
                        "address": company.get("registered_office_address", {}),
                        "sic_codes": company.get("sic_codes", []),
                        "source_url": company.get("links", {}).get("self"),
                        "source_name": "Companies House API",
                        "source_date": datetime.now().strftime("%Y-%m-%d"),
                        "ingested_at": datetime.now().isoformat(),
                        "confidence_score": 80,  # High - official data
                        "provenance": {
                            "pipeline": "companies_house_collector",
                            "source_hash": company.get("company_number", ""),
                            "ingested_at": datetime.now().isoformat()
                        },
                        "gdpr_flags": {
                            "public_only_contact": True,
                            "minimised": False,
                            "rectification_requested": False,
                            "takedown_requested": False
                        }
                    }
                    companies.append(record)
                
                print(f"Found {len(items)} companies (total so far: {len(companies)})")
                
                if len(items) < 100:
                    break
                    
                start_index += 100
                time.sleep(6 if not API_KEY else 1)  # Rate limiting
                
            elif response.status_code == 429:
                print("Rate limited, waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"Error: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Exception: {e}")
            break
    
    return companies


def get_company_details(company_number):
    """Get full details for a company"""
    try:
        response = requests.get(
            f"{BASE_URL}/company/{company_number}",
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


def collect_directors(companies, max_companies=50):
    """Collect directors from companies (public officers)"""
    directors = []
    
    for i, company in enumerate(companies[:max_companies]):
        company_number = company.get("company_number")
        
        if company_number:
            officers = get_company_officers(company_number)
            
            if officers:
                for officer in officers.get("items", []):
                    director = {
                        "name": officer.get("name"),
                        "role": officer.get("officer_role"),
                        "company_number": company_number,
                        "company_name": company.get("name"),
                        "appointment_date": officer.get("appointed_on"),
                        "resignation_date": officer.get("resigned_on"),
                        "nationality": officer.get("nationality"),
                        "country_of_residence": officer.get("country_of_residence"),
                        "date_of_birth": officer.get("date_of_birth"),
                        "address": officer.get("address", {}),
                        "source_url": f"{BASE_URL}/company/{company_number}/officers",
                        "source_name": "Companies House API",
                        "source_date": datetime.now().strftime("%Y-%m-%d"),
                        "ingested_at": datetime.now().isoformat(),
                        "confidence_score": 90,  # Very high - official record
                        "provenance": {
                            "pipeline": "companies_house_directors",
                            "source_hash": officer.get("links", {}).get("self", ""),
                            "ingested_at": datetime.now().isoformat()
                        },
                        "gdpr_flags": {
                            "public_only_contact": True,  # Directors are public record
                            "minimised": False,
                            "rectification_requested": False,
                            "takedown_requested": False
                        }
                    }
                    directors.append(director)
            
            print(f"Processed {i+1}/{min(max_companies, len(companies))}: {company.get('name')}")
            time.sleep(1.5 if not API_KEY else 0.5)
    
    return directors


def run_collection():
    """Main collection"""
    print("=" * 60)
    print("KOSMOS - Companies House Data Collection")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Collect companies
    print("\n1. Searching for large UK companies...")
    companies = search_companies(size="large", limit=200)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(companies, f, indent=2)
    
    print(f"\n✓ Saved {len(companies)} companies to {DATA_FILE}")
    
    # Collect directors (from first 50 companies)
    print("\n2. Collecting directors/officers...")
    directors = collect_directors(companies, max_companies=50)
    
    directors_file = os.path.join(OUTPUT_DIR, "directors.json")
    with open(directors_file, 'w') as f:
        json.dump(directors, f, indent=2)
    
    print(f"\n✓ Saved {len(directors)} directors to {directors_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Companies collected: {len(companies)}")
    print(f"Directors collected: {len(directors)}")
    
    return companies, directors


if __name__ == "__main__":
    run_collection()
