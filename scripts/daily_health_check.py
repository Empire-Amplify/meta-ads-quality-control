"""
Daily Health Check for Meta Ads
Quick validation of account health - run daily
"""

import logging
from datetime import datetime
from typing import Dict, List

from _config import Config
from _meta_api_client import MetaAPIClient
from _shared_utilities import (
    calculate_frequency,
    calculate_cpa,
    extract_metric_from_actions,
    categorize_issue,
)
from _email_alerts import EmailAlertHandler
from _sheets_writer import GoogleSheetsWriter

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_daily_health_check() -> Dict:
    """
    Run daily health check

    Returns:
        Dictionary with health check results
    """
    logger.info("Starting daily health check...")

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
        return {"status": "error", "errors": errors}

    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "checks_performed": [],
        "issues": [],
        "summary": {},
    }

    # Check 1: Active campaigns spending
    logger.info("Checking active campaigns...")
    spending_issues = check_active_campaigns_spending(api_client)
    results["checks_performed"].append("active_campaigns_spending")
    results["issues"].extend(spending_issues)

    # Check 2: Ad disapprovals
    logger.info("Checking for ad disapprovals...")
    disapproval_issues = check_ad_disapprovals(api_client)
    results["checks_performed"].append("ad_disapprovals")
    results["issues"].extend(disapproval_issues)

    # Check 3: Creative fatigue (high frequency)
    logger.info("Checking creative fatigue...")
    fatigue_issues = check_creative_fatigue(api_client)
    results["checks_performed"].append("creative_fatigue")
    results["issues"].extend(fatigue_issues)

    # Check 4: Budget exhaustion
    logger.info("Checking budget status...")
    budget_issues = check_budget_exhaustion(api_client)
    results["checks_performed"].append("budget_exhaustion")
    results["issues"].extend(budget_issues)

    # Check 5: Pixel health
    logger.info("Checking pixel health...")
    pixel_issues = check_pixel_health(api_client)
    results["checks_performed"].append("pixel_health")
    results["issues"].extend(pixel_issues)

    # Categorize issues by severity
    critical_issues = [i for i in results["issues"] if i["severity"] == "critical"]
    high_issues = [i for i in results["issues"] if i["severity"] == "high"]
    medium_issues = [i for i in results["issues"] if i["severity"] == "medium"]

    results["summary"] = {
        "total_issues": len(results["issues"]),
        "critical": len(critical_issues),
        "high": len(high_issues),
        "medium": len(medium_issues),
    }

    # Calculate quick health score
    health_score = calculate_quick_health_score(results["summary"])
    results["health_score"] = health_score

    # Log summary
    logger.info(f"Health check complete. Score: {health_score}/100")
    logger.info(f"Issues found: {results['summary']['total_issues']}")
    logger.info(f"  Critical: {results['summary']['critical']}")
    logger.info(f"  High: {results['summary']['high']}")
    logger.info(f"  Medium: {results['summary']['medium']}")

    # Send email alert if critical issues found
    if critical_issues:
        logger.info("Sending critical issue alert...")
        email_handler.send_daily_summary(
            account_name=Config.AD_ACCOUNT_ID,
            health_score=health_score,
            critical_issues=critical_issues,
            high_issues=high_issues,
            summary=f"Daily health check found {len(critical_issues)} critical issues requiring immediate attention.",
        )

    # Write to Google Sheets
    if sheets_writer.service:
        logger.info("Writing results to Google Sheets...")
        sheets_writer.write_dashboard(
            health_score=health_score,
            account_name=Config.AD_ACCOUNT_ID,
            issues_summary=results["summary"],
            last_run=results["timestamp"],
        )
        sheets_writer.write_issues_log(results["issues"])

    return results


def check_active_campaigns_spending(api_client: MetaAPIClient) -> List[Dict]:
    """Check if active campaigns are spending"""
    issues = []

    try:
        # Get active campaigns
        campaigns = api_client.get_campaigns(statuses=["ACTIVE"])

        # Get insights for past 24 hours
        time_range = api_client.get_date_range(1)

        for campaign in campaigns:
            insights = api_client.get_insights(
                level="campaign",
                object_id=campaign["id"],
                time_range=time_range,
                fields=["spend", "impressions"],
            )

            if insights:
                spend = float(insights[0].get("spend", 0))
                impressions = int(insights[0].get("impressions", 0))

                # Campaign active but not spending
                if spend < Config.MIN_DAILY_SPEND and impressions == 0:
                    issue = categorize_issue("underspending", severity="medium")
                    issue.update(
                        {
                            "description": f"Campaign '{campaign['name']}' is active but not spending",
                            "affected_item": campaign["name"],
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    issues.append(issue)

    except Exception as e:
        logger.error(f"Error checking campaign spending: {e}")

    return issues


def check_ad_disapprovals(api_client: MetaAPIClient) -> List[Dict]:
    """Check for disapproved ads"""
    issues = []

    try:
        # Get ads with any status
        ads = api_client.get_ads(statuses=["DISAPPROVED", "PENDING_REVIEW"])

        for ad in ads:
            if ad.get("status") == "DISAPPROVED":
                issue = categorize_issue("disapproved_ads", severity="critical")
                issue.update(
                    {
                        "description": f"Ad '{ad['name']}' has been disapproved",
                        "affected_item": ad["name"],
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                issues.append(issue)

    except Exception as e:
        logger.error(f"Error checking ad disapprovals: {e}")

    return issues


def check_creative_fatigue(api_client: MetaAPIClient) -> List[Dict]:
    """Check for creative fatigue (high frequency)"""
    issues = []

    try:
        # Get active ads
        ads = api_client.get_ads(statuses=["ACTIVE"])

        # Get insights with frequency
        time_range = api_client.get_date_range(Config.DAYS_TO_ANALYZE)

        for ad in ads:
            insights = api_client.get_insights(
                level="ad",
                object_id=ad["id"],
                time_range=time_range,
                fields=["impressions", "reach", "frequency", "spend"],
            )

            if insights:
                frequency = float(insights[0].get("frequency", 0))
                spend = float(insights[0].get("spend", 0))

                # Only check ads with meaningful spend
                if spend >= Config.MIN_SPEND_FOR_ANALYSIS:
                    if frequency >= Config.FREQUENCY_CRITICAL_THRESHOLD:
                        issue = categorize_issue(
                            "critical_frequency", severity="critical"
                        )
                        issue.update(
                            {
                                "description": f"Ad '{ad['name']}' has critical frequency: {frequency:.2f}",
                                "affected_item": ad["name"],
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        issues.append(issue)
                    elif frequency >= Config.FREQUENCY_ALERT_THRESHOLD:
                        issue = categorize_issue("high_frequency", severity="high")
                        issue.update(
                            {
                                "description": f"Ad '{ad['name']}' has high frequency: {frequency:.2f}",
                                "affected_item": ad["name"],
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        issues.append(issue)

    except Exception as e:
        logger.error(f"Error checking creative fatigue: {e}")

    return issues


def check_budget_exhaustion(api_client: MetaAPIClient) -> List[Dict]:
    """Check for campaigns hitting budget limits"""
    issues = []

    try:
        # Get active campaigns
        campaigns = api_client.get_campaigns(statuses=["ACTIVE"])

        # Get insights for today
        time_range = api_client.get_date_range(1)

        for campaign in campaigns:
            daily_budget = campaign.get("daily_budget")

            if daily_budget:
                daily_budget = float(daily_budget) / 100  # Convert from cents

                insights = api_client.get_insights(
                    level="campaign",
                    object_id=campaign["id"],
                    time_range=time_range,
                    fields=["spend"],
                )

                if insights:
                    spend = float(insights[0].get("spend", 0))

                    # Campaign hitting budget limit
                    if spend >= daily_budget * 0.95:
                        issue = categorize_issue("budget_exhausted", severity="high")
                        issue.update(
                            {
                                "description": f"Campaign '{campaign['name']}' has exhausted budget (${spend:.2f} of ${daily_budget:.2f})",
                                "affected_item": campaign["name"],
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        issues.append(issue)

    except Exception as e:
        logger.error(f"Error checking budget exhaustion: {e}")

    return issues


def check_pixel_health(api_client: MetaAPIClient) -> List[Dict]:
    """Check pixel health"""
    issues = []

    try:
        # Get pixels
        pixels = api_client.get_pixels()

        if not pixels:
            issue = categorize_issue("no_pixel", severity="critical")
            issue.update(
                {
                    "description": "No Meta Pixel found on account",
                    "affected_item": "Account",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            issues.append(issue)
        else:
            for pixel in pixels:
                if pixel.get("is_unavailable"):
                    issue = categorize_issue("pixel_not_firing", severity="critical")
                    issue.update(
                        {
                            "description": f"Pixel '{pixel['name']}' is not firing",
                            "affected_item": pixel["name"],
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    issues.append(issue)

    except Exception as e:
        logger.error(f"Error checking pixel health: {e}")

    return issues


def calculate_quick_health_score(summary: Dict) -> int:
    """
    Calculate quick health score based on issues

    Args:
        summary: Summary of issues by severity

    Returns:
        Health score from 0-100
    """
    base_score = 100

    # Deduct points for issues
    base_score -= summary["critical"] * 20  # -20 per critical issue
    base_score -= summary["high"] * 10  # -10 per high issue
    base_score -= summary["medium"] * 5  # -5 per medium issue

    # Minimum score is 0
    return max(0, base_score)


if __name__ == "__main__":
    # Run daily health check
    results = run_daily_health_check()

    # Print results
    print("\n" + "=" * 60)
    print("DAILY HEALTH CHECK RESULTS")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Health Score: {results['health_score']}/100")
    print(f"\nIssues Found: {results['summary']['total_issues']}")
    print(f"  Critical: {results['summary']['critical']}")
    print(f"  High: {results['summary']['high']}")
    print(f"  Medium: {results['summary']['medium']}")

    if results["issues"]:
        print("\nIssue Details:")
        for issue in results["issues"]:
            print(f"\n  [{issue['severity'].upper()}] {issue['category']}")
            print(f"  {issue['description']}")
            print(f"  Recommendation: {issue['recommendation']}")

    print("\n" + "=" * 60)
