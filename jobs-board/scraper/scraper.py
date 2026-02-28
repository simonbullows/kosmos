#!/usr/bin/env python3
"""
Job Board Scraper for Become Inspired
Uses SearXNG for free unlimited search
"""
import json
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any

SEARXNG_URL = "http://localhost:8080"

def generate_job_id(category: str, index: int) -> str:
    prefix = {"content_moderation": "CM", "ai_training": "AI", "multimedia_design": "MD", "education": "ED"}
    return f"{prefix.get(category, 'JB')}{index:03d}"

async def search_searxng(query: str, engines: str = "google,bing", num: int = 15) -> List[Dict]:
    """Search using local SearXNG instance"""
    import httpx
    
    url = f"{SEARXNG_URL}/search"
    params = {
        "q": query,
        "format": "json",
        "engines": engines,
        "num_results": num
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
    except Exception as e:
        print(f"SearXNG search error: {e}")
    
    return []

async def run_full_scan():
    """Run a comprehensive job scan"""
    print("🔍 Starting job scan via SearXNG...")
    
    queries = [
        "content moderator remote UK indeed",
        "AI trainer remote UK jobs",
        "image review analyst remote",
        "data annotation remote UK",
        "multimedia designer remote jobs",
        "graphic designer remote UK indeed"
    ]
    
    all_jobs = []
    
    for query in queries:
        print(f"  Searching: {query}")
        results = await search_searxng(query)
        all_jobs.extend(results)
        await asyncio.sleep(0.5)
    
    # Deduplicate by URL
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        url = job.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_jobs.append(job)
    
    print(f"📊 Found {len(unique_jobs)} unique jobs")
    return unique_jobs

def categorize_job(job: Dict) -> str:
    """Categorize a job"""
    text = f"{job.get('title', '')} {job.get('content', '')}".lower()
    
    if any(x in text for x in ["content moderator", "content review", "image review", "quality analyst", "trust & safety"]):
        return "content_moderation"
    elif any(x in text for x in ["AI trainer", "AI training", "data annotator", "data labeling", "machine learning"]):
        return "ai_training"
    elif any(x in text for x in ["multimedia", "designer", "graphic", "illustrator", "creative"]):
        return "multimedia_design"
    elif any(x in text for x in ["teacher", "education", "tutor", "instructor"]):
        return "education"
    else:
        return "other"

def match_for_candidate(job: Dict) -> List[str]:
    """Determine if job is suitable for candidate"""
    matches = []
    text = f"{job.get('title', '')} {job.get('content', '')}".lower()
    
    skills = ["graphic", "illustration", "design", "multimedia", "image", "visual", "creative"]
    if any(s in text for s in skills):
        matches.append("multimedia_candidate")
    
    return matches

def update_jobs_board(new_jobs: List[Dict]):
    """Update jobs.json"""
    jobs_file = "/home/ubuntu/.openclaw/workspace/jobs-board/jobs.json"
    
    if os.path.exists(jobs_file):
        with open(jobs_file, "r") as f:
            board = json.load(f)
    else:
        board = {"jobs_board": {"categories": {}, "candidates": {}}}
    
    cm_index = len(board["jobs_board"]["categories"].get("content_moderation", []))
    ai_index = len(board["jobs_board"]["categories"].get("ai_training", []))
    md_index = len(board["jobs_board"]["categories"].get("multimedia_design", []))
    
    added = 0
    for job in new_jobs:
        category = categorize_job(job)
        
        if category == "content_moderation":
            job_id = generate_job_id("content_moderation", cm_index + 1)
            cm_index += 1
        elif category == "ai_training":
            job_id = generate_job_id("ai_training", ai_index + 1)
            ai_index += 1
        elif category == "multimedia_design":
            job_id = generate_job_id("multimedia_design", md_index + 1)
            md_index += 1
        else:
            continue
        
        suitable = match_for_candidate(job)
        priority = "high" if suitable else "normal"
        
        # Extract domain for company
        url = job.get("url", "")
        domain = ""
        if url:
            domain = url.split("/")[2] if "//" in url else url
        
        new_job = {
            "id": job_id,
            "role": job.get("title", "Unknown"),
            "company": domain,
            "location": "Remote/UK",
            "url": url,
            "status": "not_applied",
            "suitable_for": suitable,
            "priority": priority,
            "source": "SearXNG",
            "scraped": datetime.now().isoformat()
        }
        
        if category not in board["jobs_board"]["categories"]:
            board["jobs_board"]["categories"][category] = []
        
        board["jobs_board"]["categories"][category].append(new_job)
        added += 1
    
    with open(jobs_file, "w") as f:
        json.dump(board, f, indent=2)
    
    print(f"✅ Added {added} new jobs to board")

async def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        jobs = await run_full_scan()
        update_jobs_board(jobs)
        print("🎉 Scan complete!")
    else:
        print("Job Board Scraper (SearXNG)")
        print("Usage: python3 scraper.py scan")
        print("  scan - Run job scan via local SearXNG")

if __name__ == "__main__":
    asyncio.run(main())
