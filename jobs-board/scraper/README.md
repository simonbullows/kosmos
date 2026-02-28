# Job Board Scraper

Automated scraper that polls major job boards and adds suitable jobs to your board.

## Usage

### Run a Fresh Scan

```bash
python3 jobs-board/scraper/scraper.py scan
```

This will:
1. Search Indeed, LinkedIn, remote job sites via Serper API
2. Look for: content moderation, AI training, image review, multimedia design
3. Filter for remote/UK positions
4. Match jobs against candidate profiles
5. Add new jobs to `jobs-board/jobs.json`

### Schedule Automatic Scans

Add to cron for daily scans:
```bash
0 9 * * * cd /home/ubuntu/.openclaw/workspace && python3 jobs-board/scraper/scraper.py scan >> /var/log/jobs.log 2>&1
```

## Job Boards Searched

- Indeed (via Serper)
- LinkedIn Jobs (via Serper)
- Remote-specific boards (via Serper)
- Company career pages

## Matching Criteria

Jobs are matched against candidate skills:
- **Multimedia Candidate:** graphic design, illustration, 3D, web design, multimedia, image review
- **Content Moderation:** content review, trust & safety, quality analyst
- **AI Training:** AI trainer, data annotation, machine learning

## Priority Levels

- 🟢 **high** - Matches candidate skills
- ⚪ **normal** - Other suitable roles
