"""
Email Alert Handler for Meta Ads Quality Control
Sends email notifications for critical issues
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from _config import Config

logger = logging.getLogger(__name__)


class EmailAlertHandler:
    """Handler for sending email alerts"""

    def __init__(self):
        """Initialize email handler with config settings"""
        self.email_address = Config.EMAIL_ADDRESS
        self.sendgrid_api_key = Config.SENDGRID_API_KEY
        self.enabled = Config.ENABLE_EMAIL_ALERTS
        self.slack_webhook_url = Config.SLACK_WEBHOOK_URL
        self.slack_enabled = Config.ENABLE_SLACK_ALERTS

        if self.enabled and not self.email_address:
            logger.warning("Email alerts enabled but no email address configured")
            self.enabled = False

    def send_alert(
        self,
        subject: str,
        body: str,
        issues: Optional[List[Dict]] = None,
        health_score: Optional[int] = None,
    ) -> bool:
        """
        Send email alert

        Args:
            subject: Email subject line
            body: Email body text
            issues: Optional list of issues to include
            health_score: Optional health score to include

        Returns:
            True if email sent successfully
        """
        if not self.enabled:
            logger.info("Email alerts disabled, skipping notification")
            return False

        try:
            # Build email content
            html_body = self._build_html_email(body, issues, health_score)

            # Send via SendGrid if configured, otherwise fall back to SMTP
            email_sent = False
            if self.sendgrid_api_key:
                email_sent = self._send_via_sendgrid(subject, html_body)
            else:
                email_sent = self._send_via_smtp(subject, html_body)

            # Also send via Slack if configured
            if self.slack_enabled and self.slack_webhook_url:
                self._send_via_slack(subject, body)

            return email_sent

        except (ConnectionError, TimeoutError, ValueError) as e:
            logger.error(f"Error sending email alert: {e}")
            return False

    def _build_html_email(
        self,
        body: str,
        issues: Optional[List[Dict]] = None,
        health_score: Optional[int] = None,
    ) -> str:
        """Build HTML email content"""

        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #1877f2;
                    color: white;
                    padding: 20px;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .score {{
                    font-size: 48px;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
                }}
                .score.excellent {{ color: #28a745; }}
                .score.good {{ color: #5cb85c; }}
                .score.fair {{ color: #ffc107; }}
                .score.poor {{ color: #fd7e14; }}
                .score.critical {{ color: #dc3545; }}
                .issue {{
                    background-color: white;
                    border-left: 4px solid #dc3545;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 3px;
                }}
                .issue.critical {{ border-left-color: #dc3545; }}
                .issue.high {{ border-left-color: #fd7e14; }}
                .issue.medium {{ border-left-color: #ffc107; }}
                .issue.low {{ border-left-color: #6c757d; }}
                .issue-title {{
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .issue-recommendation {{
                    color: #666;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Meta Ads Quality Control Alert</h1>
                    <p>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                <div class="content">
                    <p>{body}</p>
        """

        # Add health score if provided
        if health_score is not None:
            score_class = self._get_score_class(health_score)
            html += f"""
                    <div class="score {score_class}">
                        {health_score}/100
                    </div>
            """

        # Add issues if provided
        if issues:
            html += """
                    <h2>Issues Detected</h2>
            """
            for issue in issues:
                severity = issue.get("severity", "medium")
                html += f"""
                    <div class="issue {severity}">
                        <div class="issue-title">
                            {issue.get('category', 'Issue')}: {issue.get('description', 'No description')}
                        </div>
                        <div class="issue-recommendation">
                            {issue.get('recommendation', 'Review this issue')}
                        </div>
                    </div>
                """

        html += """
                </div>
                <div class="footer">
                    <p>This is an automated alert from Meta Ads Quality Control</p>
                    <p>Empire Amplify | Melbourne, Australia</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _get_score_class(self, score: int) -> str:
        """Get CSS class based on health score"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        elif score >= 60:
            return "poor"
        else:
            return "critical"

    def _send_via_sendgrid(self, subject: str, html_body: str) -> bool:
        """
        Send email via SendGrid API

        Args:
            subject: Email subject
            html_body: HTML email body

        Returns:
            True if sent successfully
        """
        try:
            import requests

            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "personalizations": [{"to": [{"email": self.email_address}], "subject": subject}],
                "from": {
                    "email": Config.SENDGRID_FROM_EMAIL,
                    "name": "Meta Ads Quality Control",
                },
                "content": [{"type": "text/html", "value": html_body}],
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 202:
                logger.info("Email sent successfully via SendGrid")
                return True
            else:
                logger.error(f"SendGrid API error: {response.status_code} - {response.text}")
                return False

        except (ConnectionError, TimeoutError, ValueError) as e:
            logger.error(f"Error sending via SendGrid: {e}")
            return False

    def _send_via_smtp(self, subject: str, html_body: str) -> bool:
        """
        Send email via SMTP as fallback when SendGrid is not configured.

        Args:
            subject: Email subject
            html_body: HTML email body

        Returns:
            True if sent successfully
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = Config.SENDGRID_FROM_EMAIL
            msg["To"] = self.email_address

            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
                server.sendmail(Config.SENDGRID_FROM_EMAIL, [self.email_address], msg.as_string())

            logger.info("Email sent successfully via SMTP")
            return True

        except (smtplib.SMTPException, ConnectionError, OSError) as e:
            logger.error(f"Error sending via SMTP: {e}")
            return False

    def _send_via_slack(self, subject: str, body: str) -> bool:
        """
        Send notification via Slack webhook.

        Args:
            subject: Alert subject
            body: Alert body text

        Returns:
            True if sent successfully
        """
        try:
            import requests

            payload = {
                "text": subject,
                "blocks": [
                    {"type": "header", "text": {"type": "plain_text", "text": subject}},
                    {"type": "section", "text": {"type": "mrkdwn", "text": body}},
                ],
            }

            response = requests.post(self.slack_webhook_url, json=payload)

            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack webhook error: {response.status_code}")
                return False

        except (ConnectionError, TimeoutError, ValueError) as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False

    def send_daily_summary(
        self,
        account_name: str,
        health_score: int,
        critical_issues: List[Dict],
        high_issues: List[Dict],
        summary: str,
    ) -> bool:
        """
        Send daily health check summary

        Args:
            account_name: Name of ad account
            health_score: Overall health score
            critical_issues: List of critical issues
            high_issues: List of high priority issues
            summary: Summary text

        Returns:
            True if sent successfully
        """
        subject = f"Meta Ads Daily Health Check - Score: {health_score}/100"

        if critical_issues:
            subject = f"🚨 {subject} - {len(critical_issues)} Critical Issues"

        body = f"""
        <h2>Daily Health Check Summary</h2>
        <p><strong>Account:</strong> {account_name}</p>
        <p>{summary}</p>
        """

        all_issues = critical_issues + high_issues

        return self.send_alert(subject=subject, body=body, issues=all_issues, health_score=health_score)

    def send_critical_alert(
        self,
        issue_type: str,
        description: str,
        recommendation: str,
        affected_items: List[str],
    ) -> bool:
        """
        Send immediate critical alert

        Args:
            issue_type: Type of critical issue
            description: Issue description
            recommendation: Recommended action
            affected_items: List of affected campaigns/ads

        Returns:
            True if sent successfully
        """
        subject = f"🚨 CRITICAL: {issue_type} - Immediate Action Required"

        body = f"""
        <h2>Critical Issue Detected</h2>
        <p><strong>Issue Type:</strong> {issue_type}</p>
        <p><strong>Description:</strong> {description}</p>
        <p><strong>Recommendation:</strong> {recommendation}</p>
        """

        if affected_items:
            body += "<h3>Affected Items:</h3><ul>"
            for item in affected_items[:10]:  # Limit to first 10
                body += f"<li>{item}</li>"
            if len(affected_items) > 10:
                body += f"<li>... and {len(affected_items) - 10} more</li>"
            body += "</ul>"

        issues = [
            {
                "category": issue_type,
                "description": description,
                "recommendation": recommendation,
                "severity": "critical",
            }
        ]

        return self.send_alert(subject=subject, body=body, issues=issues)


# Convenience function for simple alerts
def send_simple_alert(subject: str, body: str) -> bool:
    """
    Send a simple text alert

    Args:
        subject: Email subject
        body: Email body

    Returns:
        True if sent successfully
    """
    handler = EmailAlertHandler()
    return handler.send_alert(subject, body)
