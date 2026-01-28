"""
Configuration Management for Meta Ads Quality Control
Loads settings from environment variables with validation
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for Meta Ads Quality Control scripts"""

    # Meta Marketing API
    AD_ACCOUNT_ID: str = os.getenv("META_AD_ACCOUNT_ID", "")
    ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    APP_ID: str = os.getenv("META_APP_ID", "")
    APP_SECRET: str = os.getenv("META_APP_SECRET", "")

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")

    # Email notifications
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")

    # Slack notifications
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    # Quality thresholds
    FREQUENCY_ALERT_THRESHOLD: float = float(
        os.getenv("FREQUENCY_ALERT_THRESHOLD", "2.5")
    )
    FREQUENCY_CRITICAL_THRESHOLD: float = float(
        os.getenv("FREQUENCY_CRITICAL_THRESHOLD", "3.5")
    )
    CPA_THRESHOLD: float = float(os.getenv("CPA_THRESHOLD", "50"))
    MIN_ROAS: float = float(os.getenv("MIN_ROAS", "2.0"))
    MIN_CTR: float = float(os.getenv("MIN_CTR", "0.8"))
    MIN_DAILY_SPEND: float = float(os.getenv("MIN_DAILY_SPEND", "10"))

    # Audience thresholds
    MIN_AUDIENCE_SIZE: int = int(os.getenv("MIN_AUDIENCE_SIZE", "1000"))
    MAX_AUDIENCE_SIZE: int = int(os.getenv("MAX_AUDIENCE_SIZE", "50000000"))
    AUDIENCE_OVERLAP_THRESHOLD: float = float(
        os.getenv("AUDIENCE_OVERLAP_THRESHOLD", "25")
    )

    # Budget pacing
    BUDGET_PACING_MIN: float = float(os.getenv("BUDGET_PACING_MIN", "0.8"))
    BUDGET_PACING_MAX: float = float(os.getenv("BUDGET_PACING_MAX", "1.2"))

    # Analysis settings
    DAYS_TO_ANALYZE: int = int(os.getenv("DAYS_TO_ANALYZE", "7"))
    MIN_SPEND_FOR_ANALYSIS: float = float(os.getenv("MIN_SPEND_FOR_ANALYSIS", "50"))

    # Anomaly detection
    ANOMALY_THRESHOLD_SPEND: float = float(os.getenv("ANOMALY_THRESHOLD_SPEND", "0.5"))
    ANOMALY_THRESHOLD_CPA: float = float(os.getenv("ANOMALY_THRESHOLD_CPA", "0.5"))
    ANOMALY_THRESHOLD_ROAS: float = float(os.getenv("ANOMALY_THRESHOLD_ROAS", "0.3"))
    ANOMALY_THRESHOLD_CTR: float = float(os.getenv("ANOMALY_THRESHOLD_CTR", "0.5"))

    # Match quality
    MIN_MATCH_QUALITY: float = float(os.getenv("MIN_MATCH_QUALITY", "7.0"))

    # Creative age
    CREATIVE_REFRESH_AGE: int = int(os.getenv("CREATIVE_REFRESH_AGE", "30"))

    # System settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_EMAIL_ALERTS: bool = (
        os.getenv("ENABLE_EMAIL_ALERTS", "true").lower() == "true"
    )
    ENABLE_SLACK_ALERTS: bool = (
        os.getenv("ENABLE_SLACK_ALERTS", "false").lower() == "true"
    )

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration settings

        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        if not cls.AD_ACCOUNT_ID:
            errors.append("META_AD_ACCOUNT_ID is required")
        elif not cls.AD_ACCOUNT_ID.startswith("act_"):
            errors.append('META_AD_ACCOUNT_ID must start with "act_"')

        if not cls.ACCESS_TOKEN:
            errors.append("META_ACCESS_TOKEN is required")

        if cls.ENABLE_EMAIL_ALERTS and not cls.EMAIL_ADDRESS:
            errors.append("EMAIL_ADDRESS required when email alerts enabled")

        if cls.ENABLE_SLACK_ALERTS and not cls.SLACK_WEBHOOK_URL:
            errors.append("SLACK_WEBHOOK_URL required when Slack alerts enabled")

        # Validate thresholds
        if cls.FREQUENCY_ALERT_THRESHOLD < 0 or cls.FREQUENCY_ALERT_THRESHOLD > 10:
            errors.append("FREQUENCY_ALERT_THRESHOLD must be between 0 and 10")

        if cls.MIN_AUDIENCE_SIZE < 0:
            errors.append("MIN_AUDIENCE_SIZE must be positive")

        if cls.MAX_AUDIENCE_SIZE < cls.MIN_AUDIENCE_SIZE:
            errors.append("MAX_AUDIENCE_SIZE must be greater than MIN_AUDIENCE_SIZE")

        return (len(errors) == 0, errors)

    @classmethod
    def print_config(cls, hide_sensitive: bool = True):
        """Print current configuration (hiding sensitive data)"""
        print("=" * 60)
        print("META ADS QUALITY CONTROL - CONFIGURATION")
        print("=" * 60)

        def mask(value: str, show_chars: int = 4) -> str:
            if not value or len(value) <= show_chars:
                return "*" * 8
            return value[:show_chars] + "*" * (len(value) - show_chars)

        print(f"\nMeta API:")
        print(
            f"  Ad Account ID: {cls.AD_ACCOUNT_ID if not hide_sensitive else mask(cls.AD_ACCOUNT_ID)}"
        )
        print(
            f"  Access Token: {mask(cls.ACCESS_TOKEN) if hide_sensitive else cls.ACCESS_TOKEN}"
        )

        print(f"\nNotifications:")
        print(f"  Email: {cls.EMAIL_ADDRESS}")
        print(f"  Email Alerts: {cls.ENABLE_EMAIL_ALERTS}")
        print(f"  Slack Alerts: {cls.ENABLE_SLACK_ALERTS}")

        print(f"\nThresholds:")
        print(f"  Frequency Alert: {cls.FREQUENCY_ALERT_THRESHOLD}")
        print(f"  Frequency Critical: {cls.FREQUENCY_CRITICAL_THRESHOLD}")
        print(f"  Max CPA: ${cls.CPA_THRESHOLD}")
        print(f"  Min ROAS: {cls.MIN_ROAS}")
        print(f"  Min CTR: {cls.MIN_CTR}%")

        print(f"\nAnalysis:")
        print(f"  Days to Analyze: {cls.DAYS_TO_ANALYZE}")
        print(f"  Min Spend: ${cls.MIN_SPEND_FOR_ANALYSIS}")

        print("=" * 60)


# Validate configuration on import
is_valid, validation_errors = Config.validate()
if not is_valid:
    print("\n⚠️  CONFIGURATION ERRORS:")
    for error in validation_errors:
        print(f"  • {error}")
    print("\nPlease check your .env file and update the required settings.\n")
