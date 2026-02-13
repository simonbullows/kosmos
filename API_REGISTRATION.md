# KOSMOS API Registrations

## Companies House (FREE)
1. Go to: https://developer.company-information.service.gov.uk/
2. Click "Create API key"
3. Enter:
   - Application name: KOSMOS
   - Application description: UK public data database for internal research
4. Copy your API key
5. Set environment variable:
   ```
   export COMPANIES_HOUSE_API_KEY="your-key-here"
   ```

## Charity Commission (FREE)
1. Go to: https://register-of-charities.charitycommission.gov.uk//account/sign-in
2. Create account (free)
3. Request API access
4. Set environment variable:
   ```
   export CHARITY_COMMISSION_API_KEY="your-key-here"
   ```

## TheyWorkForYou (£20+/month)
1. Go to: https://www.theyworkforyou.com/api/
2. Sign up for plan
3. Get API key
4. Set environment variable:
   ```
   export THEYWORKFORYOU_API_KEY="your-key-here"
   ```

## Quick Setup
```bash
# Companies House (immediate)
export COMPANIES_HOUSE_API_KEY="your-key"

# Test connection
python3 /workspace/kosmos/src/scrapers/companies_house_kosmos.py
```
