# Meta Ads Quality Control

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Empire-Amplify/meta-ads-quality-control/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Scripts that audit your Meta (Facebook/Instagram) advertising accounts and identify issues before they impact performance.

These scripts automate quality control checks based on industry-standard agency audit templates and Meta Ads best practices.

---

## Two Ways to Use This

### Option 1: No-Code (Google Sheets + Apps Script)

**Suitable for:** Meta Ads managers without programming experience

[**→ Start here with the No-Code Setup Guide**](#no-code-setup-google-apps-script)

- Works entirely in Google Sheets
- No installation required
- Point-and-click interface
- Results appear automatically in sheets
- Email alerts when issues found

### Option 2: Full Code (Python Scripts)

**Suitable for:** Developers, agencies managing multiple accounts, advanced automation

[**→ Python Setup Guide**](#python-setup-developers)

- Full Meta Marketing API access
- Schedule via cron/cloud functions
- Multi-account (Business Manager) support
- Custom integrations possible
- Advanced reporting options

---

## What Gets Checked

Based on professional agency QA standards and Meta best practices:

### Pre-Launch Checks
- **Account Setup**: Currency, timezone, spending limits, audience controls
- **Campaign Configuration**: Naming conventions, objectives, budget, bid strategy
- **Targeting**: Location targeting, age restrictions, placement exclusions
- **Pixel & Tracking**: Conversion events configured, pixel installed correctly
- **Creative Compliance**: Ad formats, text limits, image specifications
- **Policy Adherence**: Special ad categories, brand safety declarations

### Daily Monitoring
- **Post-Launch Check** (24-48 hours): Ads approved, spending, tracking functional
- **Budget Pacing**: Spend rate vs plan, budget exhaustion risk
- **Creative Fatigue**: Frequency monitoring (alert at >2.5)
- **Performance**: CPA/ROAS vs targets, anomaly detection
- **URLs**: Landing pages functional, correct destination
- **Pixel Health**: Conversion events firing, data flowing

### Weekly Analysis
- **Creative Performance**: CTR trends, engagement rates, fatigue indicators
- **Audience Health**: Overlap analysis, exhaustion detection, sizing issues
- **Optimization Opportunities**: Budget reallocation, audience expansion
- **Trend Analysis**: Week-over-week performance changes

---

## Quality Score (0-100)

Your account receives a health score based on:

- **Account Setup** (15pts): Pixel, domain verification, iOS14, business verification
- **Campaign Structure** (20pts): Naming conventions, budget setup, objectives
- **Creative Health** (25pts): Fatigue level, format compliance, variety
- **Audience Quality** (15pts): Sizing, overlap, exhaustion
- **Conversion Tracking** (15pts): Events firing, match quality, CAPI status
- **Performance** (10pts): Meeting targets, delivery health

**Grade Scale:**
- **90-100**: Optimal - Account health is optimal
- **80-89**: Good - Minor issues, not time-sensitive
- **70-79**: Fair - Several items need attention
- **60-69**: Poor - Multiple problems identified
- **Below 60**: Critical - Immediate action required

---

## No-Code Setup (Google Apps Script)

### What You'll Get

- Quality control dashboard in Google Sheets
- Automated daily/weekly checks
- Email alerts for critical issues
- Creative fatigue tracking
- Budget pacing monitor
- One-click campaign audit

### Setup Steps

**Step 1: Create a Google Sheet**

1. Go to [sheets.google.com](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it "Meta Ads Quality Control - [Your Client]"

**Step 2: Install the Script**

1. In your sheet, click Extensions → Apps Script
2. Delete any existing code
3. Copy the code from [`google-apps-script/MetaQualityControl.gs`](google-apps-script/MetaQualityControl.gs)
4. Paste into the Apps Script editor
5. Click Save (disk icon)
6. Name the project "Meta Quality Control"

**Step 3: Configure Settings**

At the top of the script, find the CONFIG section:

```javascript
var CONFIG = {
  // Your Meta Ad Account ID (act_XXXXXXXXXX)
  AD_ACCOUNT_ID: 'act_1234567890',

  // Your Meta Access Token (from Business Settings → System Users)
  ACCESS_TOKEN: 'YOUR_ACCESS_TOKEN_HERE',

  // Email for alerts
  EMAIL_ADDRESS: 'your.email@company.com',

  // Alert thresholds
  FREQUENCY_ALERT_THRESHOLD: 2.5,  // Alert when frequency exceeds this
  CPA_THRESHOLD: 50,  // Your maximum acceptable CPA
  MIN_DAILY_SPEND: 10,  // Alert if spend drops below this

  // How far back to analyze (days)
  DAYS_TO_ANALYZE: 7
};
```

**Step 4: Get Your Meta Access Token**

1. Go to [business.facebook.com](https://business.facebook.com)
2. Click Business Settings
3. Go to Users → System Users
4. Create a system user (or select existing)
5. Click Generate New Token
6. Select your ad account
7. Select permissions: `ads_read`, `ads_management`
8. Copy the token and paste into CONFIG.ACCESS_TOKEN

**Step 5: Test the Script**

1. Click Run → Run function → `createMenu`
2. Click Authorize when prompted
3. Select your Google account
4. Click Advanced → Go to [project name]
5. Click Allow

Refresh your Google Sheet. You'll see a new menu: "Meta Quality Control"

**Step 6: Run Your First Audit**

1. Click Meta Quality Control → Run Full Quality Audit
2. Wait 1-2 minutes while it analyzes your account
3. Results appear in multiple tabs:
   - **Dashboard**: Overall health score and critical issues
   - **Campaign Health**: Campaign-level analysis
   - **Creative Fatigue**: Ads by frequency
   - **Audience Analysis**: Ad set performance
   - **Issues Log**: Prioritized action items

**Step 7: Schedule Automation**

1. In Apps Script editor, click Triggers (clock icon)
2. Click + Add Trigger
3. Configure:
   - Function: `runDailyHealthCheck`
   - Event source: Time-driven
   - Type: Day timer
   - Time: 9am-10am
4. Click Save

Your account will now be checked daily at 9am automatically.

---

## Python Setup (Developers)

### Prerequisites

- Python 3.8 or higher
- Meta Marketing API credentials
- Google Sheets API credentials (for output)

### Quick Start

**1. Clone the Repository**

```bash
git clone https://github.com/Empire-Amplify/meta-ads-quality-control.git
cd meta-ads-quality-control
```

**2. Install Dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure Credentials**

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Meta Marketing API
META_AD_ACCOUNT_ID=act_1234567890
META_ACCESS_TOKEN=your_access_token_here
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret

# Google Sheets (for output)
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
SPREADSHEET_ID=your_spreadsheet_id

# Email notifications
EMAIL_ADDRESS=your.email@company.com
SENDGRID_API_KEY=optional_for_sendgrid

# Thresholds
FREQUENCY_ALERT_THRESHOLD=2.5
CPA_THRESHOLD=50
MIN_DAILY_SPEND=10
```

**4. Test Connection**

```bash
python scripts/test_connection.py
```

You should see:
```
✓ Connected to Meta Marketing API
✓ Ad Account: Your Account Name (act_1234567890)
✓ Found X campaigns
✓ Connection successful!
```

### Running Scripts

**Daily Health Check:**
```bash
python scripts/daily_health_check.py
```

**Full Quality Audit:**
```bash
python scripts/comprehensive_quality_check.py
```

**Creative Fatigue Monitor:**
```bash
python scripts/creative_fatigue_monitor.py
```

**Audience Quality Audit:**
```bash
python scripts/audience_quality_audit.py
```

### Schedule Automation

**Using cron (Linux/Mac):**

```bash
# Edit crontab
crontab -e

# Add these lines
0 9 * * * cd /path/to/meta-ads-quality-control && python scripts/daily_health_check.py
0 */6 * * * cd /path/to/meta-ads-quality-control && python scripts/creative_fatigue_monitor.py
0 9 * * 1 cd /path/to/meta-ads-quality-control && python scripts/comprehensive_quality_check.py
```

**Using Task Scheduler (Windows):**

Create scheduled tasks to run:
- `daily_health_check.py` - Daily at 9am
- `creative_fatigue_monitor.py` - Every 6 hours
- `comprehensive_quality_check.py` - Monday 9am

**Using Cloud Functions:**

Deploy to AWS Lambda, Google Cloud Functions, or Azure Functions for serverless execution.

---

## Available Scripts

### Quality Audits

| Script | Frequency | What It Checks |
|--------|-----------|----------------|
| `comprehensive_quality_check.py` | Weekly | Full account audit, generates health score 0-100 |
| `daily_health_check.py` | Daily | Quick validation (spending, approvals, URLs, pixel) |
| `pre_launch_validator.py` | Pre-launch | Validates campaign before going live |

### Performance Monitoring

| Script | Frequency | What It Checks |
|--------|-----------|----------------|
| `creative_fatigue_monitor.py` | Every 6 hours | Frequency tracking, CTR decline, engagement drop |
| `budget_pacing_monitor.py` | Every 4 hours | Spend rate, budget exhaustion risk |
| `anomaly_alerts.py` | Every 4 hours | Statistical anomalies (spend/CPA/ROAS spikes) |

### Technical Checks

| Script | Frequency | What It Checks |
|--------|-----------|----------------|
| `pixel_health_check.py` | Daily | Pixel status, events firing, CAPI connection |
| `conversion_tracking_audit.py` | Daily | Event match quality, attribution windows |

### Analysis & Optimization

| Script | Frequency | What It Checks |
|--------|-----------|----------------|
| `audience_quality_audit.py` | Weekly | Audience sizing, overlap, exhaustion |
| `account_structure_audit.py` | Weekly | Naming conventions, budget strategy |
| `performance_forecasting.py` | Weekly | Month-end projections |

---

## Google Sheets Output Structure

Results are written to your Google Sheet in these tabs:

**1. Dashboard**
- Overall health score (0-100)
- Critical issues count
- Top 5 priority actions
- Quick stats (spend, ROAS, frequency)

**2. Campaign Health**
```
Campaign | Ad Sets | Ads | Budget | Spend | ROAS | Frequency | Status | Issues
---------|---------|-----|--------|-------|------|-----------|--------|-------
TOF-Cold | 5       | 15  | $500   | $487  | 2.1  | 1.8       | PASS   | None
BOF-Warm | 3       | 12  | $300   | $289  | 4.5  | 3.2       | WARN   | High freq
```

**3. Creative Fatigue**
```
Ad Name  | Format | Frequency | CTR  | CPM | Engagement | Age | Status | Action
---------|--------|-----------|------|-----|------------|-----|--------|--------
Video1   | Video  | 2.8       | 1.2% | $15 | 3.5%       | 12d | Active | Monitor
Static2  | Image  | 4.1       | 0.3% | $28 | 0.8%       | 45d | Alert  | Refresh
```

**4. Audience Analysis**
```
Ad Set   | Audience Size | Frequency | CPA | ROAS | Learning | Issues
---------|---------------|-----------|-----|------|----------|--------
LAL 1%   | 2.3M          | 2.1       | $45 | 3.2  | Complete | None
Custom   | 45k           | 4.5       | $89 | 1.2  | Complete | Fatigued
```

**5. Conversion Events**
```
Event    | Last Fired | Count (24h) | Match Quality | Status | Issues
---------|------------|-------------|---------------|--------|--------
Purchase | 10m ago    | 145         | 8.2           | OK     | None
Lead     | 2h ago     | 23          | 6.8           | WARN   | Low match
```

**6. Issues Log**
```
Date  | Severity | Type  | Campaign | Issue           | Recommendation      | Status
------|----------|-------|----------|-----------------|---------------------|--------
01/27 | CRITICAL | Pixel | Summer   | Not firing      | Check installation  | Open
01/27 | HIGH     | Freq  | Q1-Promo | 4.2 frequency   | New creative needed | Open
01/27 | MEDIUM   | Aud   | Retarget | Audience 15k    | Expand targeting    | Open
```

---

## Recommended Schedule

**For initial deployment:**
- `daily_health_check.py` (9am daily)
- `creative_fatigue_monitor.py` (every 6 hours)
- `budget_pacing_monitor.py` (every 4 hours)

**For established accounts:**
- Add `comprehensive_quality_check.py` (Monday 9am)
- Add `audience_quality_audit.py` (weekly)

**For optimization:**
- Add `performance_forecasting.py` (weekly)
- Add `anomaly_alerts.py` (every 4 hours)

---

## Checklists

Ready-to-use QA checklists based on agency templates:

- [Daily Health Check](checklists/daily-health-check.md)
- [Weekly Maintenance](checklists/weekly-maintenance.md)
- [Pre-Launch Campaign](checklists/pre-launch-campaign.md)
- [Creative Refresh](checklists/creative-refresh-checklist.md)
- [Monthly Deep Dive](checklists/monthly-deep-dive.md)

---

## Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed installation instructions
- [Script Catalog](docs/SCRIPT_CATALOG.md) - Complete reference for all scripts
- [Architecture](docs/ARCHITECTURE.md) - Technical architecture and data flow
- [Meta vs Google Ads](docs/META_VS_GOOGLE.md) - Platform comparison

---

## Troubleshooting

### Google Apps Script Issues

| Issue | Solution |
|-------|----------|
| "Authorization required" | Extensions → Apps Script → Run → Authorize |
| "Invalid access token" | Generate new token in Business Settings → System Users |
| "No data returned" | Check ad account ID format (must be act_XXXXXXXXXX) |

### Python Issues

| Issue | Solution |
|-------|----------|
| "facebook_business not found" | Run `pip install -r requirements.txt` |
| "Invalid OAuth access token" | Check ACCESS_TOKEN in .env file |
| "Ad account not found" | Verify ad account ID in .env (act_XXXXXXXXXX) |

---

## FAQ

**Can this work with Instagram ads?**
Yes. Instagram ads are managed through Meta Ads Manager and use the same API.

**Does this work for multiple ad accounts?**
Yes. For Python, configure multiple account IDs. For Google Sheets, create separate sheets per account.

**Will this make changes to my campaigns?**
No. All scripts are read-only and only report issues. No modifications are made to campaigns.

**How is this different from Meta's native tools?**
- Works across multiple accounts from one place
- Automated email alerts
- Historical tracking in Google Sheets
- Custom quality score based on agency standards
- Based on professional QA best practices

**What permissions do I need?**
- Meta: `ads_read` permission (no write access needed)
- Google Sheets: Edit access to your results spreadsheet

---

## Questions?

- Email: gordon@empireamplify.com.au
- Issues: [GitHub Issues](https://github.com/Empire-Amplify/meta-ads-quality-control/issues)
- Meta API Docs: [Meta Marketing API](https://developers.facebook.com/docs/marketing-apis)

---

## License

MIT License - Free to use and modify.

**Empire Amplify** | Melbourne, Australia | 2026
