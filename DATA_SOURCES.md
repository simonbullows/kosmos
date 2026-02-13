# KOSMOS Data Sources - Official Data Required

## Current Data (Limited)

| Category | Count | Source | Issue |
|----------|-------|--------|-------|
| Companies | 50,000 | Companies House (basic) | Missing directors, financials |
| Schools | 30,000 | UK School Data (GitHub) | Basic data only |

## Missing Data (Need Official Sources)

| Category | Source | Action Required |
|----------|--------|----------------|
| Charities | Charity Commission | Register for API, download full data |
| MPs/Parliament | UK Parliament API | Register for access |
| NHS Trusts | NHS Digital | Download official datasets |
| Local Gov | Open Register | Download full data |
| Media | Publisher websites | Manual collection |

## How to Get Official Data

### 1. Companies House (for company directors)
1. Go to: https://find-and-update.company-information.service.gov.uk/
2. Register for API key (free)
3. Access: https://developer.company-information.service.gov.uk/

### 2. Charity Commission
1. Go to: https://register-of-charity-commission.apps.gov.uk/
2. Create account
3. Download full register (CSV)

### 3. UK Parliament (MPs)
1. Go to: https://members-api.parliament.uk/
2. Register for developer access
3. Access member data

### 4. NHS Data
1. Go to: https://digital.nhs.uk/services/organisation-data
2. Download NHS organisation data

## Next Steps

1. **Register for APIs** (free)
2. **Download official datasets**
3. **Upload to KOSMOS**
4. **Refresh Streamlit app**

## Files Needed

- `charities.csv` - Full charity register
- `mp.csv` - All UK MPs
- `councillors.csv` - Local councillors  
- `nhs_trusts.csv` - NHS organisations
- `councils.csv` - Local authorities
- `media.csv` - Media contacts

## Where to Find

- **Companies House**: https://companieshouse.gov.uk
- **Charity Commission**: https://charity-commission.gov.uk
- **Parliament**: https://parliament.uk
- **NHS**: https.nhs.uk
- **Local Gov**: https://local.gov.uk
