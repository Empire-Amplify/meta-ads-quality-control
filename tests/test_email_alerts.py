"""
Test suite for _email_alerts.py
Tests email, SMTP, and Slack alert functionality
"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pytest


@pytest.fixture
def mock_config():
    """Patch Config for email handler tests."""
    with patch("_email_alerts.Config") as cfg:
        cfg.EMAIL_ADDRESS = "test@example.com"
        cfg.SENDGRID_API_KEY = ""
        cfg.ENABLE_EMAIL_ALERTS = True
        cfg.ENABLE_SLACK_ALERTS = False
        cfg.SLACK_WEBHOOK_URL = ""
        cfg.SENDGRID_FROM_EMAIL = "noreply@example.com"
        cfg.SMTP_HOST = "localhost"
        cfg.SMTP_PORT = 25
        cfg.SMTP_USE_TLS = False
        cfg.SMTP_USERNAME = ""
        cfg.SMTP_PASSWORD = ""
        yield cfg


@pytest.fixture
def handler(mock_config):
    """Create an EmailAlertHandler with mocked config."""
    from _email_alerts import EmailAlertHandler

    return EmailAlertHandler()


class TestEmailAlertHandlerInit:
    """Test handler initialization"""

    def test_init_enabled(self, handler):
        assert handler.enabled is True
        assert handler.email_address == "test@example.com"

    def test_init_disabled_no_email(self, mock_config):
        mock_config.EMAIL_ADDRESS = ""
        from _email_alerts import EmailAlertHandler

        h = EmailAlertHandler()
        assert h.enabled is False

    def test_init_disabled_by_config(self, mock_config):
        mock_config.ENABLE_EMAIL_ALERTS = False
        from _email_alerts import EmailAlertHandler

        h = EmailAlertHandler()
        assert h.enabled is False


class TestSendAlert:
    """Test send_alert method"""

    def test_disabled_returns_false(self, handler):
        handler.enabled = False
        assert handler.send_alert("Subject", "Body") is False

    def test_sends_via_smtp_when_no_sendgrid(self, handler):
        handler._send_via_smtp = MagicMock(return_value=True)
        result = handler.send_alert("Subject", "Body")
        assert result is True
        handler._send_via_smtp.assert_called_once()

    def test_sends_via_sendgrid_when_configured(self, handler):
        handler.sendgrid_api_key = "sg_key"
        handler._send_via_sendgrid = MagicMock(return_value=True)
        result = handler.send_alert("Subject", "Body")
        assert result is True
        handler._send_via_sendgrid.assert_called_once()

    def test_sends_slack_alongside_email(self, handler):
        handler.slack_enabled = True
        handler.slack_webhook_url = "https://hooks.slack.com/test"
        handler._send_via_smtp = MagicMock(return_value=True)
        handler._send_via_slack = MagicMock(return_value=True)
        result = handler.send_alert("Subject", "Body")
        assert result is True
        handler._send_via_slack.assert_called_once_with("Subject", "Body")

    def test_slack_not_sent_when_disabled(self, handler):
        handler.slack_enabled = False
        handler._send_via_smtp = MagicMock(return_value=True)
        handler._send_via_slack = MagicMock()
        handler.send_alert("Subject", "Body")
        handler._send_via_slack.assert_not_called()


class TestBuildHtmlEmail:
    """Test HTML email building"""

    def test_basic_email(self, handler):
        html = handler._build_html_email("Test body")
        assert "Test body" in html
        assert "Meta Ads Quality Control Alert" in html

    def test_email_with_health_score(self, handler):
        html = handler._build_html_email("Body", health_score=85)
        assert "85/100" in html
        assert "good" in html

    def test_email_with_critical_score(self, handler):
        html = handler._build_html_email("Body", health_score=50)
        assert "50/100" in html
        assert "critical" in html

    def test_email_with_issues(self, handler):
        issues = [
            {
                "severity": "critical",
                "category": "Pixel",
                "description": "Pixel not firing",
                "recommendation": "Fix pixel",
            }
        ]
        html = handler._build_html_email("Body", issues=issues)
        assert "Pixel not firing" in html
        assert "Fix pixel" in html
        assert "Issues Detected" in html


class TestGetScoreClass:
    """Test score CSS class mapping"""

    def test_excellent(self, handler):
        assert handler._get_score_class(95) == "excellent"

    def test_good(self, handler):
        assert handler._get_score_class(85) == "good"

    def test_fair(self, handler):
        assert handler._get_score_class(75) == "fair"

    def test_poor(self, handler):
        assert handler._get_score_class(65) == "poor"

    def test_critical(self, handler):
        assert handler._get_score_class(50) == "critical"


class TestSendViaSendGrid:
    """Test SendGrid email sending"""

    def test_successful_send(self, handler, mock_config):
        handler.sendgrid_api_key = "sg_test_key"
        mock_response = MagicMock()
        mock_response.status_code = 202
        with patch("requests.post", return_value=mock_response) as mock_post:
            result = handler._send_via_sendgrid("Subject", "<html>Body</html>")
            assert result is True
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            assert "Bearer sg_test_key" in call_kwargs[1]["headers"]["Authorization"]

    def test_failed_send(self, handler, mock_config):
        handler.sendgrid_api_key = "sg_test_key"
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        with patch("requests.post", return_value=mock_response):
            result = handler._send_via_sendgrid("Subject", "<html>Body</html>")
            assert result is False

    def test_connection_error(self, handler, mock_config):
        handler.sendgrid_api_key = "sg_test_key"
        with patch("requests.post", side_effect=ConnectionError("refused")):
            result = handler._send_via_sendgrid("Subject", "<html>Body</html>")
            assert result is False


class TestSendViaSMTP:
    """Test SMTP email sending"""

    def test_successful_send(self, handler, mock_config):
        mock_server = MagicMock()
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
            result = handler._send_via_smtp("Subject", "<html>Body</html>")
            assert result is True
            mock_server.sendmail.assert_called_once()

    def test_smtp_with_tls(self, handler, mock_config):
        mock_config.SMTP_USE_TLS = True
        mock_server = MagicMock()
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
            handler._send_via_smtp("Subject", "<html>Body</html>")
            mock_server.starttls.assert_called_once()

    def test_smtp_with_auth(self, handler, mock_config):
        mock_config.SMTP_USERNAME = "user"
        mock_config.SMTP_PASSWORD = "pass"
        mock_server = MagicMock()
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
            handler._send_via_smtp("Subject", "<html>Body</html>")
            mock_server.login.assert_called_once_with("user", "pass")

    def test_smtp_no_tls_no_auth(self, handler, mock_config):
        mock_config.SMTP_USE_TLS = False
        mock_config.SMTP_USERNAME = ""
        mock_config.SMTP_PASSWORD = ""
        mock_server = MagicMock()
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
            handler._send_via_smtp("Subject", "<html>Body</html>")
            mock_server.starttls.assert_not_called()
            mock_server.login.assert_not_called()

    def test_smtp_error(self, handler, mock_config):
        import smtplib

        with patch("smtplib.SMTP", side_effect=smtplib.SMTPException("error")):
            result = handler._send_via_smtp("Subject", "<html>Body</html>")
            assert result is False


class TestSendViaSlack:
    """Test Slack webhook sending"""

    def test_successful_send(self, handler):
        handler.slack_webhook_url = "https://hooks.slack.com/test"
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch("requests.post", return_value=mock_response) as mock_post:
            result = handler._send_via_slack("Alert Title", "Alert body")
            assert result is True
            call_kwargs = mock_post.call_args
            payload = call_kwargs[1]["json"]
            assert payload["text"] == "Alert Title"
            assert len(payload["blocks"]) == 2

    def test_webhook_error(self, handler):
        handler.slack_webhook_url = "https://hooks.slack.com/test"
        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch("requests.post", return_value=mock_response):
            result = handler._send_via_slack("Alert", "Body")
            assert result is False

    def test_connection_error(self, handler):
        handler.slack_webhook_url = "https://hooks.slack.com/test"
        with patch("requests.post", side_effect=ConnectionError("refused")):
            result = handler._send_via_slack("Alert", "Body")
            assert result is False


class TestSendDailySummary:
    """Test daily summary convenience method"""

    def test_sends_with_critical_issues(self, handler):
        handler.send_alert = MagicMock(return_value=True)
        critical = [{"severity": "critical", "category": "Pixel", "description": "Down"}]
        high = [{"severity": "high", "category": "CPA", "description": "Too high"}]
        result = handler.send_daily_summary(
            account_name="act_123",
            health_score=60,
            critical_issues=critical,
            high_issues=high,
            summary="Test summary",
        )
        assert result is True
        call_kwargs = handler.send_alert.call_args[1]
        assert "Critical Issues" in call_kwargs["subject"]
        assert call_kwargs["health_score"] == 60
        assert len(call_kwargs["issues"]) == 2

    def test_sends_without_critical_issues(self, handler):
        handler.send_alert = MagicMock(return_value=True)
        result = handler.send_daily_summary(
            account_name="act_123",
            health_score=90,
            critical_issues=[],
            high_issues=[],
            summary="All good",
        )
        assert result is True
        call_kwargs = handler.send_alert.call_args[1]
        assert "Critical" not in call_kwargs["subject"]


class TestSendCriticalAlert:
    """Test critical alert convenience method"""

    def test_sends_critical_alert(self, handler):
        handler.send_alert = MagicMock(return_value=True)
        result = handler.send_critical_alert(
            issue_type="Pixel Down",
            description="Main pixel stopped firing",
            recommendation="Check installation",
            affected_items=["Campaign A", "Campaign B"],
        )
        assert result is True
        call_kwargs = handler.send_alert.call_args[1]
        assert "CRITICAL" in call_kwargs["subject"]
        assert call_kwargs["issues"][0]["severity"] == "critical"

    def test_limits_affected_items(self, handler):
        handler.send_alert = MagicMock(return_value=True)
        items = [f"Item {i}" for i in range(15)]
        handler.send_critical_alert(
            issue_type="Test",
            description="Test",
            recommendation="Fix",
            affected_items=items,
        )
        body = handler.send_alert.call_args[1]["body"]
        assert "and 5 more" in body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
