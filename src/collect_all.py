#!/usr/bin/env python3
"""
KOSMOS Data Collection Runner
Runs all scrapers to collect UK public data
"""

import os
import sys
import json
import time
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COLLECTION_LOG = os.path.join(DATA_DIR, "collection_log.jsonl")


def log_collection(category, source, count, status="success"):
    """Log collection activity"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "source": source,
        "records": count,
        "status": status
    }
    
    with open(COLLECTION_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return log_entry


def run_collectors():
    """Run all data collectors"""
    
    print("=" * 60)
    print("K O S M O S - Data Collection System")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().isoformat()}")
    print(f"Data directory: {DATA_DIR}")
    
    results = []
    
    # 1. Companies House
    print("\n" + "-" * 60)
    print("1. COMPANIES HOUSE (Top UK Companies)")
    print("-" * 60)
    
    try:
        from scrapers.companies_house import collect_top_companies
        companies = collect_top_companies(count=100)
        log_collection("businesses", "Companies House API", len(companies))
        results.append(("Companies", len(companies)))
    except Exception as e:
        print(f"✗ Error: {e}")
        log_collection("businesses", "Companies House API", 0, str(e))
        results.append(("Companies", 0, str(e)))
    
    time.sleep(2)  # Rate limiting between collectors
    
    # 2. UK Schools
    print("\n" + "-" * 60)
    print("2. UK SCHOOLS (DfE Get Information About Schools)")
    print("-" * 60)
    
    try:
        from scrapers.uk_schools import collect_all_schools
        schools = collect_all_schools()
        log_collection("education", "DfE Schools CSV", len(schools))
        results.append(("Schools", len(schools)))
    except Exception as e:
        print(f"✗ Error: {e}")
        log_collection("education", "DfE Schools CSV", 0, str(e))
        results.append(("Schools", 0, str(e)))
    
    time.sleep(2)
    
    # 3. Charity Commission
    print("\n" + "-" * 60)
    print("3. CHARITY COMMISSION (UK Charities)")
    print("-" * 60)
    
    try:
        from scrapers.charity_commission import collect_sample_charities
        charities = collect_sample_charities(count=50)
        log_collection("charities", "Charity Commission API", len(charities))
        results.append(("Charities", len(charities)))
    except Exception as e:
        print(f"✗ Error: {e}")
        log_collection("charities", "Charity Commission API", 0, str(e))
        results.append(("Charities", 0, str(e)))
    
    time.sleep(2)
    
    # 4. UK Parliament
    print("\n" + "-" * 60)
    print("4. UK PARLIAMENT (MPs and Lords)")
    print("-" * 60)
    
    try:
        from scrapers.parliament_api import collect_parliament_data
        politicians = collect_parliament_data()
        log_collection("politics", "UK Parliament API", len(politicians))
        results.append(("Politicians", len(politicians)))
    except Exception as e:
        print(f"✗ Error: {e}")
        log_collection("politics", "UK Parliament API", 0, str(e))
        results.append(("Politicians", 0, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"\nFinished at: {datetime.now().isoformat()}")
    
    print("\nRecords collected:")
    total = 0
    for name, count, *error in results:
        if error:
            print(f"  {name}: ERROR - {error[0]}")
        else:
            print(f"  {name}: {:,} records".format(count))
            total += count
    
    print(f"\nTOTAL: {total:,} records")
    print(f"\nCollection log: {COLLECTION_LOG}")
    
    return results


if __name__ == "__main__":
    run_collectors()
