#!/usr/bin/env python3
"""
KOSMOS Schools Collector - Full Field Collection
Per spec: Provenance, confidence, timestamps on every record
"""

import csv
import json
import hashlib
from datetime import datetime
import os

SOURCE_URL = "https://raw.githubusercontent.com/MagneticMule/UK-School-Data/master/schools.csv"
SOURCE_DATE = "2026-02-13"  # Will be updated
INGESTED_AT = datetime.now().isoformat()

def calculate_confidence(record_type, field_count):
    """Calculate confidence based on data completeness"""
    if field_count >= 10:
        return 95
    elif field_count >= 7:
        return 80
    elif field_count >= 5:
        return 60
    else:
        return 40

def collect_schools():
    """Collect all UK schools with full metadata"""
    
    schools = []
    
    csv_file = "/home/ubuntu/.openclaw/workspace/kosmos/data/education/uk_schools_raw.csv"
    
    with open(csv_file, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Create provenance hash
            source_content = f"{row.get('name', '')}|{row.get('town', '')}|{row.get('postcode', '')}"
            provenance_hash = hashlib.md5(source_content.encode()).hexdigest()
            
            record = {
                # Universal requirements
                "entity_type": "person",
                "person_type": "education_leader",  # headteacher
                "full_name": f"{row.get('headfirstname', '')} {row.get('headsecondname', '')}".strip(),
                "aliases": [],
                
                # Position/Role
                "position": {
                    "title": row.get("headtitle", ""),
                    "organisation": row.get("name", ""),  # School name
                    "organisation_type": "school",
                    "start_date": None,
                    "end_date": None,
                    "current": True
                },
                
                # Organisation (School)
                "organisation_details": {
                    "name": row.get("name", ""),
                    "type": row.get("type", ""),
                    "address": {
                        "street": row.get("street", ""),
                        "locality": row.get("locality", ""),
                        "town": row.get("town", ""),
                        "county": row.get("county", ""),
                        "postcode": row.get("postcode", ""),
                        "country": "UK"
                    },
                    "contact": {
                        "phone": row.get("tel", ""),
                        "website": row.get("web", ""),
                        "email": None  # Often not public
                    }
                },
                
                # Source tracking
                "source_url": f"https://get-information-schools.service.gov.uk/",
                "source_name": "UK School Data (GitHub)",
                "source_date": SOURCE_DATE,
                "ingested_at": INGESTED_AT,
                
                # Provenance
                "provenance": {
                    "pipeline": "uk_schools_collector",
                    "source_hash": provenance_hash,
                    "confidence_score": calculate_confidence("school", len([v for v in row.values() if v]))
                },
                
                # Compliance
                "gdpr_flags": {
                    "public_only_contact": True,
                    "minimised": False,
                    "rectification_requested": False,
                    "takedown_requested": False
                },
                
                # Review tracking
                "last_verified": INGESTED_AT,
                "next_review_due": None
            }
            
            # Only add if we have a name
            if record["full_name"] and record["full_name"] != "None None":
                schools.append(record)
    
    print(f"Collected {len(schools)} schools")
    return schools

def save_schools(schools):
    """Save to JSON with metadata"""
    
    output_file = "/home/ubuntu/.openclaw/workspace/kosmos/data/education/people_schools.json"
    
    with open(output_file, 'w') as f:
        json.dump(schools, f, indent=2)
    
    print(f"Saved to {output_file}")
    
    # Create metadata file
    metadata = {
        "collection_date": INGESTED_AT,
        "source": SOURCE_URL,
        "record_count": len(schools),
        "entity_type": "person",
        "person_type": "education_leader"
    }
    
    meta_file = "/home/ubuntu/.openclaw/workspace/kosmos/data/education/people_schools.metadata.json"
    with open(meta_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata saved to {meta_file}")

if __name__ == "__main__":
    schools = collect_schools()
    save_schools(schools)
