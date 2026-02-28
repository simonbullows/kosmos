# Become Inspired Jobs Board (Windows Compatible)

**Created:** 2026-02-28

---

## Summary

| Category | Jobs | Suitable for Multimedia Candidate |
|----------|------|----------------------------------|
| Content Moderation | 30 | 14 |
| AI Training/Evaluation | 20 | 10 |
| Multimedia Design | 15 | 15 |
| Education | 6 | 0 |
| **Total** | **81** | **39** |

---

## Top Picks for Multimedia Candidate

### High Priority (Best Match)

| ID | Role | Company | Rate | Location |
|----|------|---------|------|----------|
| CM004 | Image Quality Analyst | Crossing Hurdles | $25/hr | Remote UK |
| CM005 | Image Review & QA Specialist | Crossing Hurdles | $25/hr | Remote UK |
| CM026 | Image Moderator | OpenAI | - | Remote |
| MD001 | Junior Graphic Designer | Connor | - | Remote UK |
| MD002 | Visual Content Designer | Fiverr | - | Remote |
| MD003 | Junior Multimedia Designer | 99designs | - | Remote |
| MD005 | Children's Content Designer | CBeebies | - | London |

---

## Running the Scraper on Windows

The scraper needs Python. Install from: https://www.python.org/downloads/

Then run:
```cmd
pip install httpx aiofiles
python jobs-board\scraper\scraper.py scan
```

Or use the provided batch file:
```cmd
jobs-board\scraper\run-scan.bat
```

---

## Files

- `jobs.json` - All jobs data (137 roles)
- `scraper\scraper.py` - Job scraper script
- `scraper\run-scan.bat` - Windows batch file to run scan

---

*Last updated: 2026-02-28*
