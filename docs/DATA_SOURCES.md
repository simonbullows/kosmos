# KOSMOS Data Sources

## Research findings for UK public data sources

---

## 1. EDUCATION

### ✅ CONFIRMED SOURCES

| Source | URL | Format | Notes |
|--------|-----|--------|-------|
| **Get Information About Schools** | https://get-information-schools.service.gov.uk/ | API + Downloads | Daily updated, FREE, official DfE data |
| **Schools in England (data.gov.uk)** | https://www.data.gov.uk/dataset/67f809fb-7bfe-4baa-abe4-090d48cfc323/schools-in-england | CSV, JSON | All school types, monthly updates |
| **EduBase** | Formerly DfE register | API | Now merged into Get Information About Schools |
| **GitHub - UK School Data** | https://github.com/MagneticMule/UK-School-Data | JSON | Pre-scraped UK school list |

### Fields Available
- School name, address, postcode
- School type (primary, secondary, academy, free school)
- Head teacher name
- Ofsted rating
- Phone, website, email
- Local authority

### API Access
- Free download of all establishments
- Search API available
- No authentication required for basic data

---

## 2. HEALTHCARE

### ⚠️ TO RESEARCH
- NHS Trust Directory
- Care Quality Commission (CQC)
- NHS Digital

---

## 3. CHARITIES

### ✅ CONFIRMED SOURCES

| Source | URL | Format | Notes |
|--------|-----|--------|-------|
| **Charity Commission** | https://register-of-charities.charitycommission.gov.uk/ | API + CSV | Official UK charity database |

### Fields Available
- Charity name, number, registration date
- Trustees
- Address, contact info
- Financial data
- Charitable activities

---

## 4. POLITICS

### ✅ CONFIRMED SOURCES

| Source | URL | Format | Notes |
|--------|-----|--------|-------|
| **TheyWorkForYou API** | https://www.theyworkforyou.com/api/ | JSON API | Paid (£20+/mo), comprehensive |
| **ParlParse (TheyWorkForYou)** | https://parser.theyworkforyou.com/members.html | JSON | Free, structured MP data |
| **UK Parliament API** | https://developer.parliament.uk/ | JSON API | Free official API |
| **Public Whip** | https://www.publicwhip.org.uk/project/data.php | CSV | Voting records, free |
| **Democracy Club** | https://democracyclub.org.uk/projects/data/ | CSV, API | Candidates, elections |

### Fields Available
- MP name, party, constituency
- Contact details
- Voting records
- Speeches, debates
- Lords, devolved assemblies

---

## 5. VENTURE CAPITAL

### ⚠️ TO RESEARCH
- Beauhurst (paid)
- PitchBook (paid)
- UK Business Angels Association
- British Private Equity & Venture Capital Association

---

## 6. MEDIA

### ⚠️ TO RESEARCH
- Press Gazette
- Ofcom (broadcasters)
- Media directories

---

## 7. LOCAL GOVERNMENT

### ⚠️ TO RESEARCH
- Local councils (400+ in UK)
- GOV.UK local government data
- Office for National Statistics

---

## 8. GRANTS

### ⚠️ TO RESEARCH
- UKRI
- National Lottery
- Granttree
- Research England

---

## 9. BUSINESSES (CSR/ESG)

### ✅ CONFIRMED SOURCES

| Source | URL | Format | Notes |
|--------|-----|--------|-------|
| **Companies House** | https://find-and-update.company-information.service.gov.uk/ | API + CSV | FREE, official UK company data |

### Fields Available
- Company name, address, postcode
- Directors, officers
- SIC codes
- Filing history
- Officers' address history (for contacts)

---

## Priority List

### IMMEDIATE (Free + Easy)
1. **Companies House API** - FREE, comprehensive
2. **Get Information About Schools** - FREE, daily updates
3. **Charity Commission** - FREE, official

### NEXT (Moderate Effort)
4. **UK Parliament API** - FREE, structured
5. **ParlParse** - FREE, MP data

### LATER (Paid/Complex)
6. **TheyWorkForYou** - £20+/mo, worth it?
7. **Beauhurst** - Paid VC data
8. **Press directories** - Need research

---

## Action Items

- [ ] Sign up for Companies House API key
- [ ] Download schools data CSV
- [ ] Download charities data CSV
- [ ] Set up Parliament API access
- [ ] Create scraper scripts for each source
- [ ] Design data validation process

---

## Estimated Record Counts

| Category | Approximate UK Total |
|----------|---------------------|
| Schools | ~25,000 |
| Colleges | ~300 |
| Universities | ~200 |
| NHS Trusts | ~200 |
| Hospitals | ~1,500 |
| Charities | ~170,000 |
| MPs | ~650 |
| Lords | ~800 |
| Local councils | ~400 |
| VC firms | ~1,000 |
| Major businesses | ~10,000 |

**TOTAL: ~200,000+ records to collect**
