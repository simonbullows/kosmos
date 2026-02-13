#!/usr/bin/env python3
"""
KOSMOS Unified Data Collector
Collects entities with full provenance, confidence scores, and GDPR compliance
"""

import json
import csv
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import os

class KOSMOSCollector:
    """Base collector with common functionality"""
    
    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.ingested_at = datetime.now().isoformat()
        self.records = []
        
    def calculate_confidence(self, record: Dict, required_fields: List[str]) -> int:
        """Calculate confidence based on data completeness"""
        filled_fields = sum(1 for f in required_fields if record.get(f))
        percentage = (filled_fields / len(required_fields)) * 100
        return round(percentage, 0)
    
    def create_provenance(self, record: Dict, pipeline: str) -> Dict:
        """Create provenance hash"""
        key_content = f"{self.entity_type}|{json.dumps(record, sort_keys=True)}"
        return {
            "pipeline": pipeline,
            "source_hash": hashlib.md5(key_content.encode()).hexdigest(),
            "ingested_at": self.ingested_at
        }
    
    def add_universal_fields(self, record: Dict, source_url: str, source_name: str, 
                           confidence: int, gdpr_compliant: bool = True) -> Dict:
        """Add universal KOSMOS fields to any record"""
        return {
            **record,
            "_kosmos": {
                "entity_type": self.entity_type,
                "source_url": source_url,
                "source_name": source_name,
                "source_date": datetime.now().strftime("%Y-%m-%d"),
                "ingested_at": self.ingested_at,
                "confidence_score": confidence,
                "provenance": self.create_provenance(record, f"{self.entity_type}_collector"),
                "gdpr_flags": {
                    "public_only_contact": gdpr_compliant,
                    "minimised": False,
                    "rectification_requested": False,
                    "takedown_requested": False
                },
                "last_verified": self.ingested_at,
                "next_review_due": None
            }
        }
    
    def save(self, filename: str):
        """Save records to JSON"""
        output_dir = f"/home/ubuntu/.openclaw/workspace/kosmos/data/{self.entity_type}"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, filename)
        
        with open(output_file, 'w') as f:
            json.dump(self.records, f, indent=2)
        
        print(f"✓ Saved {len(self.records)} {self.entity_type} records to {output_file}")
        
        # Save metadata
        metadata = {
            "entity_type": self.entity_type,
            "collection_date": self.ingested_at,
            "record_count": len(self.records),
            "source": self.entity_type
        }
        
        meta_file = output_file.replace('.json', '.metadata.json')
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return output_file


class SchoolsCollector(KOSMOSCollector):
    """Collect UK schools with headteachers"""
    
    def __init__(self):
        super().__init__("education")
        self.source_url = "https://github.com/MagneticMule/UK-School-Data"
        self.source_name = "UK School Data (GitHub)"
        self.required_fields = ["name", "postcode", "phone"]
        
    def collect(self):
        """Collect schools from CSV"""
        csv_file = "/home/ubuntu/.openclaw/workspace/kosmos/data/education/uk_schools_raw.csv"
        
        with open(csv_file, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                record = {
                    "name": row.get("name", ""),
                    "type": row.get("type", ""),
                    "local_authority": row.get("la", ""),
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
                        "email": None
                    },
                    "headteacher": {
                        "name": f"{row.get('headfirstname', '')} {row.get('headsecondname', '')}".strip(),
                        "title": row.get("headtitle", "")
                    }
                }
                
                confidence = self.calculate_confidence(record, self.required_fields)
                record = self.add_universal_fields(
                    record, self.source_url, self.source_name, confidence
                )
                
                self.records.append(record)
        
        return self.records


def run_all_collectors():
    """Run all entity collectors"""
    
    print("=" * 60)
    print("K O S M O S - Data Collection")
    print("=" * 60)
    
    # Schools
    print("\n📚 Collecting Schools...")
    schools = SchoolsCollector()
    schools.collect()
    schools.save("schools.json")
    
    # Summary
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Total records: {len(schools.records)}")


if __name__ == "__main__":
    run_all_collectors()
