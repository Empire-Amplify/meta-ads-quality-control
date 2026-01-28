"""
Shared Utilities for Meta Ads Quality Control Scripts
Common functions used across multiple scripts
"""

from typing import Dict, List, Optional, Any
import statistics
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def calculate_cpa(spend: float, conversions: int) -> Optional[float]:
    """
    Calculate Cost Per Action (CPA)

    Args:
        spend: Total spend
        conversions: Number of conversions

    Returns:
        CPA value or None if no conversions
    """
    if conversions == 0:
        return None
    return spend / conversions


def calculate_roas(revenue: float, spend: float) -> Optional[float]:
    """
    Calculate Return on Ad Spend (ROAS)

    Args:
        revenue: Total revenue/conversion value
        spend: Total spend

    Returns:
        ROAS value or None if no spend
    """
    if spend == 0:
        return None
    return revenue / spend


def calculate_ctr(clicks: int, impressions: int) -> Optional[float]:
    """
    Calculate Click-Through Rate (CTR)

    Args:
        clicks: Number of clicks
        impressions: Number of impressions

    Returns:
        CTR as percentage or None if no impressions
    """
    if impressions == 0:
        return None
    return (clicks / impressions) * 100


def calculate_frequency(impressions: int, reach: int) -> Optional[float]:
    """
    Calculate frequency (average impressions per user)

    Args:
        impressions: Total impressions
        reach: Unique reach

    Returns:
        Frequency value or None if no reach
    """
    if reach == 0:
        return None
    return impressions / reach


def extract_metric_from_actions(actions: List[Dict], action_type: str) -> int:
    """
    Extract specific metric from Meta's actions array

    Args:
        actions: List of action dictionaries from Meta API
        action_type: Type of action to extract (e.g., 'purchase', 'link_click')

    Returns:
        Count of specified action type
    """
    if not actions:
        return 0

    for action in actions:
        if action.get("action_type") == action_type:
            return int(action.get("value", 0))

    return 0


def extract_value_from_action_values(
    action_values: List[Dict], action_type: str
) -> float:
    """
    Extract conversion value from Meta's action_values array

    Args:
        action_values: List of action value dictionaries from Meta API
        action_type: Type of action to extract value for

    Returns:
        Value of specified action type
    """
    if not action_values:
        return 0.0

    for action_value in action_values:
        if action_value.get("action_type") == action_type:
            return float(action_value.get("value", 0))

    return 0.0


def calculate_budget_pacing(
    spent: float, budget: float, days_elapsed: int, total_days: int
) -> Dict[str, Any]:
    """
    Calculate budget pacing metrics

    Args:
        spent: Amount spent so far
        budget: Total budget
        days_elapsed: Number of days elapsed
        total_days: Total days in period

    Returns:
        Dictionary with pacing metrics
    """
    if total_days == 0 or budget == 0:
        return {
            "pacing_rate": 0,
            "expected_spend": 0,
            "variance": 0,
            "status": "unknown",
        }

    expected_spend = (budget / total_days) * days_elapsed
    variance = (
        ((spent - expected_spend) / expected_spend * 100) if expected_spend > 0 else 0
    )

    # Determine status
    if variance < -20:
        status = "underpacing"
    elif variance > 20:
        status = "overpacing"
    else:
        status = "on_track"

    return {
        "pacing_rate": (spent / budget * 100) if budget > 0 else 0,
        "expected_spend": expected_spend,
        "variance": variance,
        "status": status,
        "projected_total": (
            (spent / days_elapsed * total_days) if days_elapsed > 0 else 0
        ),
    }


def detect_anomaly(
    current_value: float, historical_values: List[float], threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Detect if current value is an anomaly compared to historical data

    Args:
        current_value: Current metric value
        historical_values: List of historical values
        threshold: Threshold for anomaly detection (0.5 = 50% deviation)

    Returns:
        Dictionary with anomaly detection results
    """
    if not historical_values or len(historical_values) < 2:
        return {
            "is_anomaly": False,
            "deviation": 0,
            "severity": "normal",
        }

    mean = statistics.mean(historical_values)
    stdev = statistics.stdev(historical_values) if len(historical_values) > 1 else 0

    if mean == 0:
        deviation = 0
    else:
        deviation = (current_value - mean) / mean

    is_anomaly = abs(deviation) > threshold

    # Determine severity
    if abs(deviation) > 1.0:
        severity = "critical"
    elif abs(deviation) > threshold:
        severity = "warning"
    else:
        severity = "normal"

    return {
        "is_anomaly": is_anomaly,
        "deviation": deviation,
        "deviation_percent": deviation * 100,
        "severity": severity,
        "mean": mean,
        "stdev": stdev,
        "direction": "increase" if deviation > 0 else "decrease",
    }


def calculate_health_score(
    account_setup_score: float,
    campaign_structure_score: float,
    creative_health_score: float,
    audience_quality_score: float,
    conversion_tracking_score: float,
    performance_score: float,
) -> Dict[str, Any]:
    """
    Calculate overall health score from component scores

    Args:
        account_setup_score: Score for account setup (max 15)
        campaign_structure_score: Score for campaign structure (max 20)
        creative_health_score: Score for creative health (max 25)
        audience_quality_score: Score for audience quality (max 15)
        conversion_tracking_score: Score for conversion tracking (max 15)
        performance_score: Score for performance (max 10)

    Returns:
        Dictionary with health score and grade
    """
    total_score = (
        account_setup_score
        + campaign_structure_score
        + creative_health_score
        + audience_quality_score
        + conversion_tracking_score
        + performance_score
    )

    # Determine grade
    if total_score >= 90:
        grade = "A"
        status = "Excellent"
    elif total_score >= 80:
        grade = "B"
        status = "Good"
    elif total_score >= 70:
        grade = "C"
        status = "Fair"
    elif total_score >= 60:
        grade = "D"
        status = "Poor"
    else:
        grade = "F"
        status = "Critical"

    return {
        "total_score": round(total_score, 1),
        "grade": grade,
        "status": status,
        "components": {
            "account_setup": account_setup_score,
            "campaign_structure": campaign_structure_score,
            "creative_health": creative_health_score,
            "audience_quality": audience_quality_score,
            "conversion_tracking": conversion_tracking_score,
            "performance": performance_score,
        },
    }


def categorize_issue(issue_type: str, severity: str = "medium") -> Dict[str, str]:
    """
    Categorize and provide recommendations for issues

    Args:
        issue_type: Type of issue detected
        severity: Severity level (critical, high, medium, low)

    Returns:
        Dictionary with issue details and recommendations
    """
    issue_catalog = {
        "high_frequency": {
            "category": "Creative Fatigue",
            "recommendation": "Refresh creative assets or pause ad to prevent audience burnout",
            "default_severity": "high",
        },
        "critical_frequency": {
            "category": "Creative Fatigue",
            "recommendation": "Immediate creative refresh required - audience is severely fatigued",
            "default_severity": "critical",
        },
        "high_cpa": {
            "category": "Performance",
            "recommendation": "Review targeting, creative, or pause campaign if CPA remains high",
            "default_severity": "high",
        },
        "low_roas": {
            "category": "Performance",
            "recommendation": "Optimize targeting, creative, or bid strategy to improve returns",
            "default_severity": "high",
        },
        "small_audience": {
            "category": "Audience",
            "recommendation": "Expand targeting to increase potential reach",
            "default_severity": "medium",
        },
        "large_audience": {
            "category": "Audience",
            "recommendation": "Narrow targeting for better performance and efficiency",
            "default_severity": "medium",
        },
        "no_pixel": {
            "category": "Tracking",
            "recommendation": "Install Meta Pixel to track conversions and optimize delivery",
            "default_severity": "critical",
        },
        "pixel_not_firing": {
            "category": "Tracking",
            "recommendation": "Check pixel implementation - no recent events detected",
            "default_severity": "critical",
        },
        "low_match_quality": {
            "category": "Tracking",
            "recommendation": "Improve event match quality by sending more customer information",
            "default_severity": "high",
        },
        "no_conversions": {
            "category": "Performance",
            "recommendation": "Review conversion setup, targeting, and creative effectiveness",
            "default_severity": "high",
        },
        "budget_exhausted": {
            "category": "Budget",
            "recommendation": "Increase budget or pause low-performing campaigns",
            "default_severity": "high",
        },
        "underspending": {
            "category": "Budget",
            "recommendation": "Check delivery issues, increase bids, or expand targeting",
            "default_severity": "medium",
        },
        "disapproved_ads": {
            "category": "Compliance",
            "recommendation": "Review ad content against Meta policies and resubmit",
            "default_severity": "critical",
        },
    }

    issue_info = issue_catalog.get(
        issue_type,
        {
            "category": "Other",
            "recommendation": "Review and address issue",
            "default_severity": severity,
        },
    )

    return {
        "type": issue_type,
        "category": issue_info["category"],
        "severity": severity or issue_info["default_severity"],
        "recommendation": issue_info["recommendation"],
    }


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    elif currency == "AUD":
        return f"A${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage

    Args:
        value: Value to format
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def parse_date_range(date_preset: str) -> Dict[str, str]:
    """
    Parse date preset into start and end dates

    Args:
        date_preset: Date preset string (last_7d, last_30d, etc.)

    Returns:
        Dictionary with 'since' and 'until' dates
    """
    end_date = datetime.now()

    days_map = {
        "today": 0,
        "yesterday": 1,
        "last_3d": 3,
        "last_7d": 7,
        "last_14d": 14,
        "last_30d": 30,
        "last_90d": 90,
    }

    days = days_map.get(date_preset, 7)
    start_date = end_date - timedelta(days=days)

    return {
        "since": start_date.strftime("%Y-%m-%d"),
        "until": end_date.strftime("%Y-%m-%d"),
    }


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if denominator is zero

    Returns:
        Division result or default
    """
    if denominator == 0:
        return default
    return numerator / denominator
