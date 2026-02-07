/**
 * Meta Ads Quality Control - Google Apps Script Version
 * Empire Amplify - Quality Control Automation
 *
 * NO-CODE VERSION FOR META ADS MANAGERS
 *
 * This script runs entirely in Google Sheets - no programming required.
 * Based on professional agency QA standards and Meta Ads best practices.
 *
 * SETUP INSTRUCTIONS:
 * 1. Create a new Google Sheet
 * 2. Extensions → Apps Script → Paste this code
 * 3. Update the CONFIG section below with your details
 * 4. Run createMenu function → Authorize
 * 5. Use the "Meta Quality Control" menu in your sheet
 */

// ============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================================================

var CONFIG = {
  // Your Meta Ad Account ID (format: act_1234567890)
  // Find this in Meta Ads Manager URL or Business Settings
  AD_ACCOUNT_ID: 'act_YOUR_ACCOUNT_ID_HERE',

  // Your Meta Access Token
  // Get from: business.facebook.com → Business Settings → System Users
  // Generate Token with permissions: ads_read, ads_management
  ACCESS_TOKEN: 'YOUR_ACCESS_TOKEN_HERE',

  // Email for alerts and reports
  EMAIL_ADDRESS: 'your.email@company.com',

  // === QUALITY THRESHOLDS ===

  // Frequency: Alert when ad frequency exceeds this
  FREQUENCY_ALERT_THRESHOLD: 2.5,
  FREQUENCY_CRITICAL_THRESHOLD: 3.5,

  // Performance
  CPA_THRESHOLD: 50,  // Maximum acceptable cost per result
  MIN_ROAS: 2.0,  // Minimum return on ad spend
  MIN_CTR: 0.8,  // Minimum click-through rate (%)

  // Budget
  MIN_DAILY_SPEND: 10,  // Alert if spend drops below this
  BUDGET_PACING_MIN: 0.8,  // Alert if under 80% of planned pace
  BUDGET_PACING_MAX: 1.2,  // Alert if over 120% of planned pace

  // Audience
  MIN_AUDIENCE_SIZE: 1000,
  MAX_AUDIENCE_SIZE: 50000000,
  AUDIENCE_OVERLAP_THRESHOLD: 25,  // % overlap

  // Analysis period
  DAYS_TO_ANALYZE: 7,

  // Alerts
  ENABLE_EMAIL_ALERTS: true,
  SLACK_WEBHOOK_URL: ''  // Optional: Add Slack webhook for notifications
};

// ============================================================================
// MAIN MENU - Creates custom menu in Google Sheets
// ============================================================================

function onOpen() {
  createMenu();
}

function createMenu() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Meta Quality Control')
    .addItem('📊 Run Full Quality Audit', 'runFullQualityAudit')
    .addSeparator()
    .addItem('✅ Daily Health Check', 'runDailyHealthCheck')
    .addItem('🎨 Creative Fatigue Report', 'runCreativeFatigueCheck')
    .addItem('👥 Audience Quality Audit', 'runAudienceQualityAudit')
    .addItem('📈 Budget Pacing Check', 'runBudgetPacingCheck')
    .addSeparator()
    .addItem('⚙️ Settings & Help', 'showHelp')
    .addToUi();

  Logger.log('✓ Menu created. Refresh your sheet to see "Meta Quality Control" menu.');
}

// ============================================================================
// FULL QUALITY AUDIT - Comprehensive account health check
// ============================================================================

function runFullQualityAudit() {
  try {
    Logger.log('Starting Full Quality Audit...');
    var ui = SpreadsheetApp.getUi();
    ui.alert('Starting Full Quality Audit',
             'This will take 1-2 minutes. Results will appear in multiple tabs.',
             ui.ButtonSet.OK);

    // Validate configuration
    if (!validateConfig()) {
      return;
    }

    // Fetch data from Meta API
    var accountData = fetchAccountData();
    var campaigns = fetchCampaigns();
    var adSets = fetchAdSets();
    var ads = fetchAds();

    // Calculate health score
    var healthScore = calculateHealthScore(accountData, campaigns, adSets, ads);

    // Identify issues
    var issues = identifyIssues(campaigns, adSets, ads);

    // Write results to sheets
    writeDashboard(healthScore, issues);
    writeCampaignHealth(campaigns);
    writeCreativeFatigue(ads);
    writeAudienceAnalysis(adSets);
    writeConversionEvents(accountData);
    writeIssuesLog(issues);

    // Send email if critical issues found
    if (hasCriticalIssues(issues) && CONFIG.ENABLE_EMAIL_ALERTS) {
      sendAlertEmail(healthScore, issues);
    }

    Logger.log('✓ Full Quality Audit complete. Health Score: ' + healthScore.total + '/100');
    ui.alert('Audit Complete',
             'Health Score: ' + healthScore.total + '/100\n\n' +
             'Critical Issues: ' + countBySeverity(issues, 'CRITICAL') + '\n' +
             'High Priority: ' + countBySeverity(issues, 'HIGH') + '\n\n' +
             'Check the Dashboard tab for details.',
             ui.ButtonSet.OK);

  } catch (error) {
    handleError(error, 'Full Quality Audit');
  }
}

// ============================================================================
// DAILY HEALTH CHECK - Quick validation
// ============================================================================

function runDailyHealthCheck() {
  try {
    Logger.log('Starting Daily Health Check...');

    if (!validateConfig()) {
      return;
    }

    var issues = [];

    // Check 1: Campaigns are spending
    var campaigns = fetchCampaigns();
    var notSpending = campaigns.filter(c => c.status === 'ACTIVE' && c.spend_24h < CONFIG.MIN_DAILY_SPEND);
    if (notSpending.length > 0) {
      issues.push({
        severity: 'HIGH',
        type: 'Spend',
        campaign: notSpending.map(c => c.name).join(', '),
        issue: notSpending.length + ' active campaign(s) with low/no spend in last 24h',
        recommendation: 'Check budget limits, ad approval status, and delivery settings'
      });
    }

    // Check 2: Ad approvals
    var ads = fetchAds();
    var disapproved = ads.filter(a => a.effective_status === 'DISAPPROVED');
    if (disapproved.length > 0) {
      issues.push({
        severity: 'CRITICAL',
        type: 'Approvals',
        campaign: '',
        issue: disapproved.length + ' ad(s) disapproved',
        recommendation: 'Review ads in Meta Ads Manager and address policy violations'
      });
    }

    // Check 3: Pixel health
    var pixelHealth = checkPixelHealth();
    if (!pixelHealth.healthy) {
      issues.push({
        severity: 'CRITICAL',
        type: 'Pixel',
        campaign: '',
        issue: 'Pixel not firing or events missing',
        recommendation: pixelHealth.recommendation
      });
    }

    // Check 4: Budget exhaustion
    var exhausted = campaigns.filter(c => c.budget_remaining < (c.daily_budget * 0.1));
    if (exhausted.length > 0) {
      issues.push({
        severity: 'HIGH',
        type: 'Budget',
        campaign: exhausted.map(c => c.name).join(', '),
        issue: exhausted.length + ' campaign(s) running out of budget',
        recommendation: 'Increase budget or pause campaigns'
      });
    }

    // Write results
    writeIssuesLog(issues);

    // Alert if critical issues
    if (hasCriticalIssues(issues)) {
      var message = 'Daily Health Check found ' + issues.length + ' issue(s):\n\n' +
                    issues.slice(0, 5).map(i => '• ' + i.issue).join('\n');

      SpreadsheetApp.getUi().alert('Issues Found', message, SpreadsheetApp.getUi().ButtonSet.OK);

      if (CONFIG.ENABLE_EMAIL_ALERTS) {
        sendDailyHealthEmail(issues);
      }
    } else {
      Logger.log('✓ Daily Health Check passed. No issues found.');
    }

  } catch (error) {
    handleError(error, 'Daily Health Check');
  }
}

// ============================================================================
// CREATIVE FATIGUE CHECK - Monitor frequency and creative performance
// ============================================================================

function runCreativeFatigueCheck() {
  try {
    Logger.log('Checking Creative Fatigue...');

    if (!validateConfig()) {
      return;
    }

    var ads = fetchAdsWithInsights();
    var fatigued = [];

    ads.forEach(function(ad) {
      var frequency = parseFloat(ad.frequency || 0);
      var ctr = parseFloat(ad.ctr || 0);
      var age_days = calculateAdAge(ad.created_time);

      var status = 'HEALTHY';
      var action = 'Monitor';

      if (frequency > CONFIG.FREQUENCY_CRITICAL_THRESHOLD) {
        status = 'CRITICAL';
        action = 'Refresh creative immediately';
      } else if (frequency > CONFIG.FREQUENCY_ALERT_THRESHOLD) {
        status = 'WARNING';
        action = 'Prepare new creative';
      }

      if (ctr < CONFIG.MIN_CTR) {
        status = 'WARNING';
        action = action + ', Review messaging/targeting';
      }

      if (age_days > 30 && frequency > 2.0) {
        status = 'WARNING';
        action = action + ', Creative is old';
      }

      if (status !== 'HEALTHY') {
        fatigued.push({
          ad_name: ad.name,
          campaign: ad.campaign_name,
          format: ad.format || 'Unknown',
          frequency: frequency.toFixed(2),
          ctr: (ctr * 100).toFixed(2) + '%',
          age_days: age_days,
          status: status,
          action: action
        });
      }
    });

    // Write to sheet
    writeCreativeFatigue(fatigued);

    // Show summary
    var message = 'Creative Fatigue Check Complete\n\n' +
                  'Total Ads: ' + ads.length + '\n' +
                  'Fatigued: ' + fatigued.length + '\n' +
                  'Critical: ' + fatigued.filter(a => a.status === 'CRITICAL').length;

    SpreadsheetApp.getUi().alert('Creative Fatigue Report', message, SpreadsheetApp.getUi().ButtonSet.OK);

    Logger.log('✓ Creative Fatigue Check complete. ' + fatigued.length + ' ads need attention.');

  } catch (error) {
    handleError(error, 'Creative Fatigue Check');
  }
}

// ============================================================================
// META API FUNCTIONS - Fetch data from Meta Marketing API
// ============================================================================

function fetchAccountData() {
  var url = 'https://graph.facebook.com/v21.0/' + CONFIG.AD_ACCOUNT_ID +
            '?fields=name,currency,account_status,disable_reason,min_daily_budget,timezone_name' +
            '&access_token=' + CONFIG.ACCESS_TOKEN;

  var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
  var data = JSON.parse(response.getContentText());

  if (data.error) {
    throw new Error('API Error: ' + data.error.message);
  }

  return data;
}

function fetchAllPages(url) {
  var allData = [];
  var nextUrl = url;
  var maxPages = 10;
  var page = 0;

  while (nextUrl && page < maxPages) {
    var response = UrlFetchApp.fetch(nextUrl, {muteHttpExceptions: true});
    var data = JSON.parse(response.getContentText());

    if (data.error) {
      throw new Error('API Error: ' + data.error.message);
    }

    allData = allData.concat(data.data || []);
    nextUrl = (data.paging && data.paging.next) ? data.paging.next : null;
    page++;
  }

  return allData;
}

function fetchCampaigns() {
  var fields = 'name,status,objective,daily_budget,lifetime_budget,budget_remaining,created_time,start_time,stop_time';
  var url = 'https://graph.facebook.com/v21.0/' + CONFIG.AD_ACCOUNT_ID +
            '/campaigns?fields=' + fields +
            '&access_token=' + CONFIG.ACCESS_TOKEN +
            '&limit=100';

  var campaigns = [];
  var rawCampaigns = fetchAllPages(url);

  // Get insights for each campaign
  rawCampaigns.forEach(function(campaign) {
    var insights = fetchCampaignInsights(campaign.id);
    campaign.spend = insights.spend || 0;
    campaign.impressions = insights.impressions || 0;
    campaign.clicks = insights.clicks || 0;
    campaign.ctr = insights.ctr || 0;
    campaign.cpc = insights.cpc || 0;
    campaign.roas = insights.roas || 0;
    campaigns.push(campaign);
  });

  return campaigns;
}

function fetchCampaignInsights(campaignId) {
  var today = Utilities.formatDate(new Date(), 'GMT', 'yyyy-MM-dd');
  var sinceDate = new Date();
  sinceDate.setDate(sinceDate.getDate() - CONFIG.DAYS_TO_ANALYZE);
  var since = Utilities.formatDate(sinceDate, 'GMT', 'yyyy-MM-dd');

  var url = 'https://graph.facebook.com/v21.0/' + campaignId +
            '/insights?fields=spend,impressions,clicks,ctr,cpc,actions,action_values,cost_per_action_type' +
            '&time_range={"since":"' + since + '","until":"' + today + '"}' +
            '&access_token=' + CONFIG.ACCESS_TOKEN;

  try {
    var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    var data = JSON.parse(response.getContentText());

    if (data.data && data.data.length > 0) {
      var insights = data.data[0];

      // Calculate ROAS if purchase data available
      var roas = 0;
      if (insights.action_values) {
        var purchaseValue = insights.action_values.find(a => a.action_type === 'purchase');
        if (purchaseValue && parseFloat(insights.spend) > 0) {
          roas = parseFloat(purchaseValue.value || 0) / parseFloat(insights.spend);
        }
      }
      insights.roas = roas;

      return insights;
    }
  } catch (e) {
    Logger.log('Warning: Could not fetch insights for campaign ' + campaignId);
  }

  return {spend: 0, impressions: 0, clicks: 0, ctr: 0, cpc: 0, roas: 0};
}

function fetchAdSets() {
  var fields = 'name,status,campaign_id,daily_budget,lifetime_budget,billing_event,optimization_goal,targeting';
  var url = 'https://graph.facebook.com/v21.0/' + CONFIG.AD_ACCOUNT_ID +
            '/adsets?fields=' + fields +
            '&access_token=' + CONFIG.ACCESS_TOKEN +
            '&limit=500';

  return fetchAllPages(url);
}

function fetchAds() {
  var fields = 'name,status,effective_status,creative,adset_id,campaign_id,created_time';
  var url = 'https://graph.facebook.com/v21.0/' + CONFIG.AD_ACCOUNT_ID +
            '/ads?fields=' + fields +
            '&access_token=' + CONFIG.ACCESS_TOKEN +
            '&limit=500';

  return fetchAllPages(url);
}

function fetchAdsWithInsights() {
  var ads = fetchAds();
  var today = Utilities.formatDate(new Date(), 'GMT', 'yyyy-MM-dd');
  var sinceDate = new Date();
  sinceDate.setDate(sinceDate.getDate() - CONFIG.DAYS_TO_ANALYZE);
  var since = Utilities.formatDate(sinceDate, 'GMT', 'yyyy-MM-dd');

  ads.forEach(function(ad) {
    var url = 'https://graph.facebook.com/v21.0/' + ad.id +
              '/insights?fields=impressions,clicks,ctr,frequency,spend' +
              '&time_range={"since":"' + since + '","until":"' + today + '"}' +
              '&access_token=' + CONFIG.ACCESS_TOKEN;

    try {
      var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
      var data = JSON.parse(response.getContentText());

      if (data.data && data.data.length > 0) {
        var insights = data.data[0];
        ad.frequency = insights.frequency || 0;
        ad.ctr = insights.ctr || 0;
        ad.impressions = insights.impressions || 0;
        ad.spend = insights.spend || 0;
      }
    } catch (e) {
      Logger.log('Warning: Could not fetch insights for ad ' + ad.id);
    }
  });

  return ads;
}

// ============================================================================
// HEALTH SCORE CALCULATION
// ============================================================================

function calculateHealthScore(accountData, campaigns, adSets, ads) {
  var score = {
    account_setup: 0,  // 15 points
    campaign_structure: 0,  // 20 points
    creative_health: 0,  // 25 points
    audience_quality: 0,  // 15 points
    conversion_tracking: 0,  // 15 points
    performance: 0,  // 10 points
    total: 0
  };

  // Account Setup (15 points)
  if (accountData.account_status == 1) score.account_setup += 5;  // Active
  if (accountData.currency) score.account_setup += 5;  // Currency set
  if (accountData.timezone_name) score.account_setup += 5;  // Timezone set

  // Campaign Structure (20 points)
  var activeCampaigns = campaigns.filter(c => c.status === 'ACTIVE');
  if (activeCampaigns.length > 0) score.campaign_structure += 10;

  var properlyNamed = campaigns.filter(c => c.name && c.name.length > 5);
  if (properlyNamed.length === campaigns.length) score.campaign_structure += 5;

  var withBudgets = campaigns.filter(c => c.daily_budget || c.lifetime_budget);
  if (withBudgets.length === campaigns.length) score.campaign_structure += 5;

  // Creative Health (25 points)
  var fatigued = ads.filter(a => parseFloat(a.frequency || 0) > CONFIG.FREQUENCY_CRITICAL_THRESHOLD);
  var fatigue_ratio = fatigued.length / Math.max(ads.length, 1);
  score.creative_health = Math.round(25 * (1 - fatigue_ratio));

  // Audience Quality (15 points)
  var learningAdSets = adSets.filter(a => a.status === 'ACTIVE');
  if (learningAdSets.length > 0) score.audience_quality += 15;

  // Conversion Tracking (15 points) - Simplified for now
  score.conversion_tracking = 10;  // Assume basic tracking in place

  // Performance (10 points)
  var performingCampaigns = campaigns.filter(c => {
    return c.roas >= CONFIG.MIN_ROAS && c.ctr >= (CONFIG.MIN_CTR / 100);
  });
  var perf_ratio = performingCampaigns.length / Math.max(activeCampaigns.length, 1);
  score.performance = Math.round(10 * perf_ratio);

  // Calculate total
  score.total = score.account_setup +
                score.campaign_structure +
                score.creative_health +
                score.audience_quality +
                score.conversion_tracking +
                score.performance;

  return score;
}

// ============================================================================
// ISSUE IDENTIFICATION
// ============================================================================

function identifyIssues(campaigns, adSets, ads) {
  var issues = [];
  var today = new Date();

  // Issue 1: High frequency ads
  ads.forEach(function(ad) {
    var frequency = parseFloat(ad.frequency || 0);
    if (frequency > CONFIG.FREQUENCY_CRITICAL_THRESHOLD) {
      issues.push({
        date: today,
        severity: 'CRITICAL',
        type: 'Creative Fatigue',
        campaign: ad.campaign_name || 'Unknown',
        issue: 'Ad "' + ad.name + '" has frequency ' + frequency.toFixed(2),
        recommendation: 'Pause ad and refresh creative immediately',
        status: 'Open'
      });
    } else if (frequency > CONFIG.FREQUENCY_ALERT_THRESHOLD) {
      issues.push({
        date: today,
        severity: 'HIGH',
        type: 'Creative Fatigue',
        campaign: ad.campaign_name || 'Unknown',
        issue: 'Ad "' + ad.name + '" has frequency ' + frequency.toFixed(2),
        recommendation: 'Prepare new creative variants',
        status: 'Open'
      });
    }
  });

  // Issue 2: Disapproved ads
  var disapproved = ads.filter(a => a.effective_status === 'DISAPPROVED');
  disapproved.forEach(function(ad) {
    issues.push({
      date: today,
      severity: 'CRITICAL',
      type: 'Ad Approval',
      campaign: ad.campaign_name || 'Unknown',
      issue: 'Ad "' + ad.name + '" is disapproved',
      recommendation: 'Review ad policy violations in Meta Ads Manager',
      status: 'Open'
    });
  });

  // Issue 3: Poor performance campaigns
  campaigns.forEach(function(campaign) {
    if (campaign.status === 'ACTIVE' && campaign.spend > 50) {
      if (campaign.roas > 0 && campaign.roas < CONFIG.MIN_ROAS) {
        issues.push({
          date: today,
          severity: 'HIGH',
          type: 'Performance',
          campaign: campaign.name,
          issue: 'ROAS ' + campaign.roas.toFixed(2) + ' below target ' + CONFIG.MIN_ROAS,
          recommendation: 'Review targeting, creative, or consider pausing',
          status: 'Open'
        });
      }
    }
  });

  // Issue 4: Low spend campaigns
  var lowSpend = campaigns.filter(c => c.status === 'ACTIVE' && c.spend < CONFIG.MIN_DAILY_SPEND);
  lowSpend.forEach(function(campaign) {
    issues.push({
      date: today,
      severity: 'MEDIUM',
      type: 'Delivery',
      campaign: campaign.name,
      issue: 'Campaign spending only $' + campaign.spend + ' per day',
      recommendation: 'Check budget, bids, audience size, and ad approval status',
      status: 'Open'
    });
  });

  return issues;
}

// ============================================================================
// GOOGLE SHEETS OUTPUT FUNCTIONS
// ============================================================================

function writeDashboard(healthScore, issues) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Dashboard') || ss.insertSheet('Dashboard', 0);
  sheet.clear();

  // Header
  sheet.getRange('A1:F1').merge().setValue('META ADS QUALITY CONTROL DASHBOARD')
    .setBackground('#4267B2').setFontColor('white').setFontSize(16).setFontWeight('bold');

  // Health Score
  sheet.getRange('A3').setValue('Overall Health Score').setFontWeight('bold');
  sheet.getRange('B3').setValue(healthScore.total + '/100')
    .setFontSize(20).setFontWeight('bold')
    .setBackground(getScoreColor(healthScore.total));

  sheet.getRange('A4').setValue('Grade').setFontWeight('bold');
  sheet.getRange('B4').setValue(getGrade(healthScore.total));

  // Score breakdown
  sheet.getRange('A6').setValue('Score Breakdown').setFontWeight('bold');
  sheet.getRange('A7:B12').setValues([
    ['Account Setup (15pts)', healthScore.account_setup],
    ['Campaign Structure (20pts)', healthScore.campaign_structure],
    ['Creative Health (25pts)', healthScore.creative_health],
    ['Audience Quality (15pts)', healthScore.audience_quality],
    ['Conversion Tracking (15pts)', healthScore.conversion_tracking],
    ['Performance (10pts)', healthScore.performance]
  ]);

  // Issues summary
  sheet.getRange('D3').setValue('Issues Summary').setFontWeight('bold');
  sheet.getRange('D4:E7').setValues([
    ['Critical', countBySeverity(issues, 'CRITICAL')],
    ['High', countBySeverity(issues, 'HIGH')],
    ['Medium', countBySeverity(issues, 'MEDIUM')],
    ['Total Issues', issues.length]
  ]);

  // Last updated
  sheet.getRange('A14').setValue('Last Updated: ' + new Date());

  Logger.log('✓ Dashboard written');
}

function writeCampaignHealth(campaigns) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Campaign Health') || ss.insertSheet('Campaign Health');
  sheet.clear();

  // Headers
  var headers = ['Campaign', 'Status', 'Objective', 'Budget', 'Spend', 'ROAS', 'CTR', 'Health'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers])
    .setBackground('#4267B2').setFontColor('white').setFontWeight('bold');

  // Data
  var data = campaigns.map(function(c) {
    var budget = c.daily_budget || c.lifetime_budget || 0;
    var health = 'PASS';
    if (c.roas < CONFIG.MIN_ROAS) health = 'WARNING';
    if (c.spend < CONFIG.MIN_DAILY_SPEND && c.status === 'ACTIVE') health = 'FAIL';

    return [
      c.name,
      c.status,
      c.objective || '',
      '$' + parseFloat(budget).toFixed(2),
      '$' + parseFloat(c.spend || 0).toFixed(2),
      c.roas ? c.roas.toFixed(2) : 'N/A',
      c.ctr ? (c.ctr * 100).toFixed(2) + '%' : 'N/A',
      health
    ];
  });

  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }

  sheet.autoResizeColumns(1, headers.length);
  Logger.log('✓ Campaign Health written');
}

function writeCreativeFatigue(ads) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Creative Fatigue') || ss.insertSheet('Creative Fatigue');
  sheet.clear();

  // Headers
  var headers = ['Ad Name', 'Campaign', 'Frequency', 'CTR', 'Age (days)', 'Status', 'Action'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers])
    .setBackground('#4267B2').setFontColor('white').setFontWeight('bold');

  // Data
  var data = [];
  if (Array.isArray(ads)) {
    data = ads.map(function(ad) {
      return [
        ad.ad_name || ad.name,
        ad.campaign || '',
        ad.frequency || '0',
        ad.ctr || '0%',
        ad.age_days || 0,
        ad.status || 'UNKNOWN',
        ad.action || ''
      ];
    });
  }

  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  } else {
    sheet.getRange('A2').setValue('No fatigued ads found - all ads are healthy!');
  }

  sheet.autoResizeColumns(1, headers.length);
  Logger.log('✓ Creative Fatigue written');
}

function writeAudienceAnalysis(adSets) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Audience Analysis') || ss.insertSheet('Audience Analysis');
  sheet.clear();

  // Headers
  var headers = ['Ad Set', 'Status', 'Optimization Goal', 'Targeting Summary'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers])
    .setBackground('#4267B2').setFontColor('white').setFontWeight('bold');

  // Data
  var data = adSets.map(function(adSet) {
    var targeting = 'Custom';
    if (adSet.targeting) {
      try {
        var t = typeof adSet.targeting === 'string' ? JSON.parse(adSet.targeting) : adSet.targeting;
        if (t.geo_locations) targeting = 'Geo: ' + (t.geo_locations.countries || []).join(', ');
      } catch (e) {}
    }

    return [
      adSet.name,
      adSet.status,
      adSet.optimization_goal || 'Unknown',
      targeting
    ];
  });

  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }

  sheet.autoResizeColumns(1, headers.length);
  Logger.log('✓ Audience Analysis written');
}

function writeConversionEvents(accountData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Conversion Events') || ss.insertSheet('Conversion Events');
  sheet.clear();

  sheet.getRange('A1').setValue('Conversion Events').setFontWeight('bold');
  sheet.getRange('A2').setValue('Account: ' + (accountData.name || 'Unknown'));
  sheet.getRange('A3').setValue('Status: ' + (accountData.account_status == 1 ? 'Active' : 'Inactive'));

  Logger.log('✓ Conversion Events written');
}

function writeIssuesLog(issues) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Issues Log') || ss.insertSheet('Issues Log');
  sheet.clear();

  // Headers
  var headers = ['Date', 'Severity', 'Type', 'Campaign', 'Issue', 'Recommendation', 'Status'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers])
    .setBackground('#E74C3C').setFontColor('white').setFontWeight('bold');

  // Data
  var data = issues.map(function(issue) {
    return [
      Utilities.formatDate(issue.date || new Date(), 'GMT', 'yyyy-MM-dd'),
      issue.severity,
      issue.type,
      issue.campaign,
      issue.issue,
      issue.recommendation,
      issue.status || 'Open'
    ];
  });

  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);

    // Color code by severity
    for (var i = 0; i < data.length; i++) {
      var severity = data[i][1];
      var color = '#FFFFFF';
      if (severity === 'CRITICAL') color = '#FFCDD2';
      else if (severity === 'HIGH') color = '#FFE0B2';
      else if (severity === 'MEDIUM') color = '#FFF9C4';

      sheet.getRange(i + 2, 1, 1, headers.length).setBackground(color);
    }
  } else {
    sheet.getRange('A2').setValue('No issues found - account is healthy!').setFontColor('#27AE60');
  }

  sheet.autoResizeColumns(1, headers.length);
  Logger.log('✓ Issues Log written');
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function validateConfig() {
  var errors = [];

  if (!CONFIG.AD_ACCOUNT_ID || CONFIG.AD_ACCOUNT_ID === 'act_YOUR_ACCOUNT_ID_HERE') {
    errors.push('AD_ACCOUNT_ID not configured');
  }

  if (!CONFIG.ACCESS_TOKEN || CONFIG.ACCESS_TOKEN === 'YOUR_ACCESS_TOKEN_HERE') {
    errors.push('ACCESS_TOKEN not configured');
  }

  if (!CONFIG.EMAIL_ADDRESS || CONFIG.EMAIL_ADDRESS === 'your.email@company.com') {
    errors.push('EMAIL_ADDRESS not configured');
  }

  if (errors.length > 0) {
    var ui = SpreadsheetApp.getUi();
    ui.alert('Configuration Required',
             'Please update the CONFIG section in the script:\n\n' +
             errors.join('\n'),
             ui.ButtonSet.OK);
    return false;
  }

  return true;
}

function calculateAdAge(createdTime) {
  try {
    var created = new Date(createdTime);
    var now = new Date();
    var diffMs = now - created;
    var diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    return diffDays;
  } catch (e) {
    return 0;
  }
}

function checkPixelHealth() {
  try {
    var url = 'https://graph.facebook.com/v21.0/' + CONFIG.AD_ACCOUNT_ID +
              '/adspixels?fields=name,last_fired_time' +
              '&access_token=' + CONFIG.ACCESS_TOKEN;
    var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    var data = JSON.parse(response.getContentText());

    if (data.error) {
      Logger.log('Pixel check API error: ' + data.error.message);
      return {healthy: false, recommendation: 'Could not query pixel: ' + data.error.message};
    }

    var pixels = data.data || [];
    if (pixels.length === 0) {
      return {healthy: false, recommendation: 'No pixel found. Create one in Meta Events Manager.'};
    }

    var pixel = pixels[0];
    if (!pixel.last_fired_time) {
      return {healthy: false, recommendation: 'Pixel "' + pixel.name + '" has never fired. Check website installation.'};
    }

    var hoursSinceLastFire = (new Date() - new Date(pixel.last_fired_time)) / (1000 * 60 * 60);
    if (hoursSinceLastFire > 24) {
      return {healthy: false, recommendation: 'Pixel "' + pixel.name + '" last fired ' + Math.round(hoursSinceLastFire) + 'h ago. Check installation.'};
    }

    return {healthy: true, recommendation: 'Pixel "' + pixel.name + '" is healthy.'};
  } catch (e) {
    Logger.log('Pixel check error: ' + e.toString());
    return {healthy: false, recommendation: 'Could not check pixel: ' + e.toString()};
  }
}

function hasCriticalIssues(issues) {
  return issues.some(function(issue) {
    return issue.severity === 'CRITICAL';
  });
}

function countBySeverity(issues, severity) {
  return issues.filter(function(issue) {
    return issue.severity === severity;
  }).length;
}

function getScoreColor(score) {
  if (score >= 90) return '#27AE60';  // Green
  if (score >= 80) return '#2ECC71';  // Light green
  if (score >= 70) return '#F39C12';  // Orange
  if (score >= 60) return '#E67E22';  // Dark orange
  return '#E74C3C';  // Red
}

function getGrade(score) {
  if (score >= 90) return 'A - Excellent';
  if (score >= 80) return 'B - Good';
  if (score >= 70) return 'C - Fair';
  if (score >= 60) return 'D - Poor';
  return 'F - Critical';
}

function handleError(error, context) {
  Logger.log('ERROR in ' + context + ': ' + error.toString());

  var ui = SpreadsheetApp.getUi();
  ui.alert('Error',
           'An error occurred during ' + context + ':\n\n' +
           error.toString() + '\n\n' +
           'Check the script execution log for details (View → Logs).',
           ui.ButtonSet.OK);
}

function sendAlertEmail(healthScore, issues) {
  if (!CONFIG.EMAIL_ADDRESS || !CONFIG.ENABLE_EMAIL_ALERTS) {
    return;
  }

  var subject = '[META ADS ALERT] Quality Score: ' + healthScore.total + '/100';

  var criticalIssues = issues.filter(i => i.severity === 'CRITICAL');
  var highIssues = issues.filter(i => i.severity === 'HIGH');

  var body = 'Meta Ads Quality Control Alert\n\n' +
             '='.repeat(50) + '\n\n' +
             'Health Score: ' + healthScore.total + '/100 (' + getGrade(healthScore.total) + ')\n\n' +
             'Critical Issues: ' + criticalIssues.length + '\n' +
             'High Priority: ' + highIssues.length + '\n\n';

  if (criticalIssues.length > 0) {
    body += 'CRITICAL ISSUES:\n\n';
    criticalIssues.slice(0, 5).forEach(function(issue) {
      body += '• ' + issue.issue + '\n';
      body += '  → ' + issue.recommendation + '\n\n';
    });
  }

  body += '\nView full report in your Google Sheet:\n';
  body += SpreadsheetApp.getActiveSpreadsheet().getUrl();

  MailApp.sendEmail({
    to: CONFIG.EMAIL_ADDRESS,
    subject: subject,
    body: body
  });

  Logger.log('✓ Alert email sent to ' + CONFIG.EMAIL_ADDRESS);
}

function sendDailyHealthEmail(issues) {
  if (!CONFIG.EMAIL_ADDRESS || !CONFIG.ENABLE_EMAIL_ALERTS) {
    return;
  }

  var subject = '[META ADS] Daily Health Check - ' + issues.length + ' Issue(s)';

  var body = 'Meta Ads Daily Health Check\n\n' +
             '=' + '='.repeat(50) + '\n\n' +
             'Issues Found: ' + issues.length + '\n\n';

  issues.slice(0, 10).forEach(function(issue) {
    body += '• [' + issue.severity + '] ' + issue.issue + '\n';
    body += '  → ' + issue.recommendation + '\n\n';
  });

  body += '\nView full report in your Google Sheet:\n';
  body += SpreadsheetApp.getActiveSpreadsheet().getUrl();

  MailApp.sendEmail({
    to: CONFIG.EMAIL_ADDRESS,
    subject: subject,
    body: body
  });

  Logger.log('✓ Daily health email sent');
}

function showHelp() {
  var ui = SpreadsheetApp.getUi();
  ui.alert('Meta Quality Control - Help',
           'CONFIGURATION:\n' +
           '1. Update CONFIG section in script (Extensions → Apps Script)\n' +
           '2. Add your Ad Account ID and Access Token\n' +
           '3. Set your email and thresholds\n\n' +
           'HOW TO GET ACCESS TOKEN:\n' +
           '1. Go to business.facebook.com\n' +
           '2. Business Settings → System Users\n' +
           '3. Generate Token with ads_read permission\n\n' +
           'AUTOMATION:\n' +
           'Set up triggers (clock icon in Apps Script) to run daily.\n\n' +
           'SUPPORT:\n' +
           'gordon@empireamplify.com.au',
           ui.ButtonSet.OK);
}

// ============================================================================
// END OF SCRIPT
// ============================================================================

Logger.log('✓ Meta Quality Control script loaded successfully');
