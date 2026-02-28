# KOSMOS Jobs Board

A database of content moderation and AI training/evaluation jobs for Simon.

## Structure

- **jobs.db** - SQLite database with all jobs
- **jobs.db** contains:
  - title, company, pay_rate, location, job_type, category, url, status, applied_date, notes

## Categories

- Content Moderation (30 jobs)
- AI Training (20 jobs)
- AI Evaluation (8 jobs)

## Top Paying Jobs

| Pay | Role | Company |
|-----|------|---------|
| $90/hr | Data Scientist - AI Research | Crossing Hurdles |
| $65/hr | Language Specialist | Crossing Hurdles |
| $60/hr | MS Office Content Reviewer | Crossing Hurdles |
| $30/hr | AI Quality Analyst (LLM) | Crossing Hurdles |
| $25/hr | Image Quality Analyst | Crossing Hurdles |

## Usage

```python
import sqlite3

conn = sqlite3.connect('jobs.db')
c = conn.cursor()

# All new jobs
c.execute("SELECT * FROM jobs WHERE status = 'new'")

# By category
c.execute("SELECT * FROM jobs WHERE category = 'Content Moderation'")

# By company
c.execute("SELECT * FROM jobs WHERE company = 'Crossing Hurdles'")

# Update status
c.execute("UPDATE jobs SET status = 'applied', applied_date = '2026-02-28' WHERE id = 1")

conn.commit()
conn.close()
```

## Sync to GitHub

Jobs database is synced to: https://github.com/simonbullows/kosmos/tree/master/data/jobs
