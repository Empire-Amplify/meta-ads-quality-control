"""
Comprehensive Quality Check for Meta Ads
Full account audit - run weekly
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple

from _config import Config
from _meta_api_client import MetaAPIClient
from _shared_utilities import (
    calculate_frequency,
    calculate_cpa,
    calculate_roas,
    calculate_ctr,
    calculate_health_score,
    extract_metric_from_actions,
    extract_value_from_action_values,
    categorize_issue
)
from _email_alerts import EmailAlertHandler
from _sheets_writer import GoogleSheetsWriter

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_comprehensive_quality_check() -> Dict:
    """
    Run comprehensive quality check

    Returns:
        Dictionary with comprehensive audit results
    """
    logger.info("Starting comprehensive quality check...")

    # Initialize clients
    api_client = MetaAPIClient()
    email_handler = EmailAlertHandler()
    sheets_writer = GoogleSheetsWriter()

    # Validate configuration
    is_valid, errors = Config.validate()
    if not is_valid:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return {'status': 'error', 'errors': errors}

    results = {
        'timestamp': datetime.now().isoformat(),
        'status': 'success',
        'health_score': 0,
        'component_scores': {},
        'issues': [],
        'campaigns': [],
        'adsets': [],
        'ads': []
    }

    # Audit 1: Account Setup (15 points)
    logger.info("Auditing account setup...")
    account_score, account_issues = audit_account_setup(api_client)
    results['component_scores']['account_setup'] = account_score
    results['issues'].extend(account_issues)

    # Audit 2: Campaign Structure (20 points)
    logger.info("Auditing campaign structure...")
    campaign_score, campaign_issues, campaign_data = audit_campaign_structure(api_client)
    results['component_scores']['campaign_structure'] = campaign_score
    results['issues'].extend(campaign_issues)
    results['campaigns'] = campaign_data

    # Audit 3: Creative Health (25 points)
    logger.info("Auditing creative health...")
    creative_score, creative_issues, ad_data = audit_creative_health(api_client)
    results['component_scores']['creative_health'] = creative_score
    results['issues'].extend(creative_issues)
    results['ads'] = ad_data

    # Audit 4: Audience Quality (15 points)
    logger.info("Auditing audience quality...")
    audience_score, audience_issues, adset_data = audit_audience_quality(api_client)
    results['component_scores']['audience_quality'] = audience_score
    results['issues'].extend(audience_issues)
    results['adsets'] = adset_data

    # Audit 5: Conversion Tracking (15 points)
    logger.info("Auditing conversion tracking...")
    conversion_score, conversion_issues = audit_conversion_tracking(api_client)
    results['component_scores']['conversion_tracking'] = conversion_score
    results['issues'].extend(conversion_issues)

    # Audit 6: Performance (10 points)
    logger.info("Auditing performance...")
    performance_score, performance_issues = audit_performance(api_client, campaign_data)
    results['component_scores']['performance'] = performance_score
    results['issues'].extend(performance_issues)

    # Calculate overall health score
    health_score_data = calculate_health_score(
        account_setup_score=account_score,
        campaign_structure_score=campaign_score,
        creative_health_score=creative_score,
        audience_quality_score=audience_score,
        conversion_tracking_score=conversion_score,
        performance_score=performance_score
    )

    results['health_score'] = health_score_data['total_score']
    results['grade'] = health_score_data['grade']
    results['status_text'] = health_score_data['status']

    # Categorize issues
    critical_issues = [i for i in results['issues'] if i['severity'] == 'critical']
    high_issues = [i for i in results['issues'] if i['severity'] == 'high']

    # Log summary
    logger.info(f"Comprehensive audit complete. Health Score: {results['health_score']}/100 ({results['grade']})")
    logger.info(f"Total issues found: {len(results['issues'])}")
    logger.info(f"  Critical: {len(critical_issues)}")
    logger.info(f"  High: {len(high_issues)}")

    # Send email notification
    if critical_issues or results['health_score'] < 70:
        logger.info("Sending audit summary email...")
        email_handler.send_daily_summary(
            account_name=Config.AD_ACCOUNT_ID,
            health_score=int(results['health_score']),
            critical_issues=critical_issues,
            high_issues=high_issues,
            summary=f"Comprehensive audit complete. Health score: {results['health_score']}/100"
        )

    # Write to Google Sheets
    if sheets_writer.service:
        logger.info("Writing results to Google Sheets...")
        sheets_writer.write_dashboard(
            health_score=int(results['health_score']),
            account_name=Config.AD_ACCOUNT_ID,
            issues_summary={
                'critical': len(critical_issues),
                'high': len(high_issues),
                'medium': len([i for i in results['issues'] if i['severity'] == 'medium']),
                'low': len([i for i in results['issues'] if i['severity'] == 'low'])
            },
            last_run=results['timestamp']
        )
        sheets_writer.write_campaign_health(results['campaigns'])
        sheets_writer.write_creative_fatigue(results['ads'])
        sheets_writer.write_audience_analysis(results['adsets'])
        sheets_writer.write_issues_log(results['issues'])

    return results


def audit_account_setup(api_client: MetaAPIClient) -> Tuple[float, List[Dict]]:
    """Audit account setup (15 points max)"""
    score = 15.0
    issues = []

    try:
        # Check account quality
        account_info = api_client.check_account_quality()

        # Check for pixels
        pixels = api_client.get_pixels()
        if not pixels:
            score -= 5
            issue = categorize_issue('no_pixel', severity='critical')
            issue.update({
                'description': 'No Meta Pixel configured',
                'affected_item': 'Account',
                'timestamp': datetime.now().isoformat()
            })
            issues.append(issue)

        # Check account status
        if account_info.get('account_status') != 1:  # 1 = Active
            score -= 10
            issue = categorize_issue('account_status', severity='critical')
            issue.update({
                'description': f"Account status issue: {account_info.get('disable_reason', 'Unknown')}",
                'affected_item': 'Account',
                'timestamp': datetime.now().isoformat(),
                'recommendation': 'Review account status in Business Manager'
            })
            issues.append(issue)

    except Exception as e:
        logger.error(f"Error auditing account setup: {e}")

    return max(0, score), issues


def audit_campaign_structure(api_client: MetaAPIClient) -> Tuple[float, List[Dict], List[Dict]]:
    """Audit campaign structure (20 points max)"""
    score = 20.0
    issues = []
    campaign_data = []

    try:
        campaigns = api_client.get_campaigns(statuses=['ACTIVE', 'PAUSED'])
        time_range = api_client.get_date_range(Config.DAYS_TO_ANALYZE)

        for campaign in campaigns:
            campaign_info = {
                'name': campaign['name'],
                'status': campaign['status'],
                'objective': campaign.get('objective', 'N/A'),
                'spend': 0,
                'impressions': 0,
                'clicks': 0,
                'conversions': 0,
                'cpa': 0,
                'roas': 0,
                'frequency': 0,
                'health_status': 'Good',
                'issues': []
            }

            # Get insights
            insights = api_client.get_insights(
                level='campaign',
                object_id=campaign['id'],
                time_range=time_range
            )

            if insights:
                insight = insights[0]
                campaign_info['spend'] = float(insight.get('spend', 0))
                campaign_info['impressions'] = int(insight.get('impressions', 0))
                campaign_info['clicks'] = int(insight.get('clicks', 0))

                # Extract conversions
                actions = insight.get('actions', [])
                conversions = extract_metric_from_actions(actions, 'purchase')
                campaign_info['conversions'] = conversions

                # Calculate metrics
                if conversions > 0:
                    campaign_info['cpa'] = campaign_info['spend'] / conversions

                # Extract revenue for ROAS
                action_values = insight.get('action_values', [])
                revenue = extract_value_from_action_values(action_values, 'purchase')
                if campaign_info['spend'] > 0:
                    campaign_info['roas'] = revenue / campaign_info['spend']

                campaign_info['frequency'] = float(insight.get('frequency', 0))

            # Check for issues
            campaign_issues = []

            # Check naming convention
            if not campaign['name'].strip():
                score -= 1
                campaign_issues.append('Poor naming')

            # Check budget configuration
            if not campaign.get('daily_budget') and not campaign.get('lifetime_budget'):
                score -= 2
                campaign_issues.append('No budget set')

            # Check special ad categories if required
            if campaign.get('special_ad_categories') and not campaign['special_ad_categories']:
                campaign_issues.append('Special categories not set')

            if campaign_issues:
                campaign_info['health_status'] = 'Needs Attention'
                campaign_info['issues'] = ', '.join(campaign_issues)

            campaign_data.append(campaign_info)

    except Exception as e:
        logger.error(f"Error auditing campaign structure: {e}")

    return max(0, score), issues, campaign_data


def audit_creative_health(api_client: MetaAPIClient) -> Tuple[float, List[Dict], List[Dict]]:
    """Audit creative health (25 points max)"""
    score = 25.0
    issues = []
    ad_data = []

    try:
        ads = api_client.get_ads(statuses=['ACTIVE'])
        time_range = api_client.get_date_range(Config.DAYS_TO_ANALYZE)

        for ad in ads:
            ad_info = {
                'name': ad['name'],
                'campaign_name': 'N/A',
                'status': ad['status'],
                'frequency': 0,
                'impressions': 0,
                'reach': 0,
                'days_running': 0,
                'fatigue_level': 'Good',
                'action_required': 'None'
            }

            # Get insights
            insights = api_client.get_insights(
                level='ad',
                object_id=ad['id'],
                time_range=time_range
            )

            if insights:
                insight = insights[0]
                ad_info['impressions'] = int(insight.get('impressions', 0))
                ad_info['reach'] = int(insight.get('reach', 0))
                ad_info['frequency'] = float(insight.get('frequency', 0))

                # Check creative fatigue
                if ad_info['frequency'] >= Config.FREQUENCY_CRITICAL_THRESHOLD:
                    score -= 5
                    ad_info['fatigue_level'] = 'Critical'
                    ad_info['action_required'] = 'Refresh creative immediately'

                    issue = categorize_issue('critical_frequency', severity='critical')
                    issue.update({
                        'description': f"Ad '{ad['name']}' has critical frequency: {ad_info['frequency']:.2f}",
                        'affected_item': ad['name'],
                        'timestamp': datetime.now().isoformat()
                    })
                    issues.append(issue)

                elif ad_info['frequency'] >= Config.FREQUENCY_ALERT_THRESHOLD:
                    score -= 2
                    ad_info['fatigue_level'] = 'Warning'
                    ad_info['action_required'] = 'Consider refreshing'

            ad_data.append(ad_info)

    except Exception as e:
        logger.error(f"Error auditing creative health: {e}")

    return max(0, score), issues, ad_data


def audit_audience_quality(api_client: MetaAPIClient) -> Tuple[float, List[Dict], List[Dict]]:
    """Audit audience quality (15 points max)"""
    score = 15.0
    issues = []
    adset_data = []

    try:
        adsets = api_client.get_adsets(statuses=['ACTIVE'])
        time_range = api_client.get_date_range(Config.DAYS_TO_ANALYZE)

        for adset in adsets:
            adset_info = {
                'name': adset['name'],
                'campaign_name': 'N/A',
                'status': adset['status'],
                'audience_size': 0,
                'spend': 0,
                'results': 0,
                'cost_per_result': 0,
                'audience_health': 'Good',
                'issues': []
            }

            # Check audience size via delivery estimate
            targeting = adset.get('targeting', {})
            if targeting:
                estimate = api_client.get_delivery_estimate(
                    targeting=targeting,
                    optimization_goal=adset.get('optimization_goal', 'CONVERSIONS')
                )

                if estimate:
                    audience_size = estimate.get('estimate_ready', {}).get('users', 0)
                    adset_info['audience_size'] = audience_size

                    # Check if audience too small or large
                    if audience_size < Config.MIN_AUDIENCE_SIZE:
                        score -= 2
                        adset_info['audience_health'] = 'Too Small'
                        adset_info['issues'].append('Audience too narrow')
                    elif audience_size > Config.MAX_AUDIENCE_SIZE:
                        score -= 1
                        adset_info['audience_health'] = 'Too Broad'
                        adset_info['issues'].append('Audience too broad')

            # Get performance
            insights = api_client.get_insights(
                level='adset',
                object_id=adset['id'],
                time_range=time_range
            )

            if insights:
                insight = insights[0]
                adset_info['spend'] = float(insight.get('spend', 0))
                actions = insight.get('actions', [])
                adset_info['results'] = extract_metric_from_actions(actions, 'purchase')

                if adset_info['results'] > 0:
                    adset_info['cost_per_result'] = adset_info['spend'] / adset_info['results']

            adset_data.append(adset_info)

    except Exception as e:
        logger.error(f"Error auditing audience quality: {e}")

    return max(0, score), issues, adset_data


def audit_conversion_tracking(api_client: MetaAPIClient) -> Tuple[float, List[Dict]]:
    """Audit conversion tracking (15 points max)"""
    score = 15.0
    issues = []

    try:
        # Check pixels
        pixels = api_client.get_pixels()

        if not pixels:
            score -= 15
            issue = categorize_issue('no_pixel', severity='critical')
            issue.update({
                'description': 'No Meta Pixel configured',
                'affected_item': 'Account',
                'timestamp': datetime.now().isoformat()
            })
            issues.append(issue)
        else:
            for pixel in pixels:
                if pixel.get('is_unavailable'):
                    score -= 10
                    issue = categorize_issue('pixel_not_firing', severity='critical')
                    issue.update({
                        'description': f"Pixel '{pixel['name']}' not firing",
                        'affected_item': pixel['name'],
                        'timestamp': datetime.now().isoformat()
                    })
                    issues.append(issue)

        # Check conversion events
        events = api_client.get_conversion_events()
        if not events:
            score -= 5
            issues.append({
                'type': 'no_conversion_events',
                'category': 'Tracking',
                'severity': 'high',
                'description': 'No conversion events configured',
                'affected_item': 'Account',
                'recommendation': 'Configure conversion events in Events Manager',
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"Error auditing conversion tracking: {e}")

    return max(0, score), issues


def audit_performance(api_client: MetaAPIClient, campaigns: List[Dict]) -> Tuple[float, List[Dict]]:
    """Audit performance against targets (10 points max)"""
    score = 10.0
    issues = []

    try:
        for campaign in campaigns:
            # Check CPA if conversions exist
            if campaign['conversions'] > 0:
                if campaign['cpa'] > Config.CPA_THRESHOLD:
                    score -= 2
                    issue = categorize_issue('high_cpa', severity='high')
                    issue.update({
                        'description': f"Campaign '{campaign['name']}' has high CPA: ${campaign['cpa']:.2f}",
                        'affected_item': campaign['name'],
                        'timestamp': datetime.now().isoformat()
                    })
                    issues.append(issue)

            # Check ROAS if available
            if campaign['roas'] > 0 and campaign['roas'] < Config.MIN_ROAS:
                score -= 2
                issue = categorize_issue('low_roas', severity='high')
                issue.update({
                    'description': f"Campaign '{campaign['name']}' has low ROAS: {campaign['roas']:.2f}",
                    'affected_item': campaign['name'],
                    'timestamp': datetime.now().isoformat()
                })
                issues.append(issue)

    except Exception as e:
        logger.error(f"Error auditing performance: {e}")

    return max(0, score), issues


if __name__ == '__main__':
    # Run comprehensive quality check
    results = run_comprehensive_quality_check()

    # Print results
    print("\n" + "=" * 60)
    print("COMPREHENSIVE QUALITY CHECK RESULTS")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Health Score: {results['health_score']}/100 (Grade: {results['grade']})")
    print(f"Status: {results['status_text']}")
    print(f"\nComponent Scores:")
    for component, score in results['component_scores'].items():
        print(f"  {component.replace('_', ' ').title()}: {score:.1f}")
    print(f"\nTotal Issues: {len(results['issues'])}")

    if results['issues']:
        print("\nCritical/High Priority Issues:")
        for issue in results['issues']:
            if issue['severity'] in ['critical', 'high']:
                print(f"\n  [{issue['severity'].upper()}] {issue['category']}")
                print(f"  {issue['description']}")
                print(f"  Recommendation: {issue['recommendation']}")

    print("\n" + "=" * 60)
