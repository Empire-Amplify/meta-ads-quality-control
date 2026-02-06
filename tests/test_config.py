"""
Test suite for _config.py
Tests configuration validation, safe parsing, and utility functions
"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pytest


class TestSafeParsing:
    """Test _safe_int and _safe_float helpers"""

    def test_safe_int_valid(self):
        from _config import _safe_int

        assert _safe_int("42", 0) == 42
        assert _safe_int("0", 10) == 0
        assert _safe_int("-5", 0) == -5

    def test_safe_int_invalid(self):
        from _config import _safe_int

        assert _safe_int("abc", 7) == 7
        assert _safe_int("", 10) == 10
        assert _safe_int("3.14", 0) == 0  # float string is invalid for int

    def test_safe_int_none(self):
        from _config import _safe_int

        assert _safe_int(None, 5) == 5

    def test_safe_float_valid(self):
        from _config import _safe_float

        assert _safe_float("3.14", 0.0) == 3.14
        assert _safe_float("42", 0.0) == 42.0
        assert _safe_float("0", 1.0) == 0.0

    def test_safe_float_invalid(self):
        from _config import _safe_float

        assert _safe_float("abc", 2.5) == 2.5
        assert _safe_float("", 1.0) == 1.0

    def test_safe_float_none(self):
        from _config import _safe_float

        assert _safe_float(None, 5.0) == 5.0


class TestConfigValidation:
    """Test Config.validate() method"""

    def test_valid_config(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", "act_123"), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", False), patch.object(
            Config, "ENABLE_SLACK_ALERTS", False
        ), patch.object(Config, "GOOGLE_SHEETS_CREDENTIALS", ""), patch.object(
            Config, "FREQUENCY_ALERT_THRESHOLD", 2.5
        ), patch.object(Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.5), patch.object(
            Config, "MIN_AUDIENCE_SIZE", 1000
        ), patch.object(Config, "MAX_AUDIENCE_SIZE", 50000000):
            is_valid, errors = Config.validate()
            assert is_valid is True
            assert errors == []

    def test_missing_account_id(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", ""), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", False), patch.object(
            Config, "ENABLE_SLACK_ALERTS", False
        ), patch.object(Config, "GOOGLE_SHEETS_CREDENTIALS", ""), patch.object(
            Config, "FREQUENCY_ALERT_THRESHOLD", 2.5
        ), patch.object(Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.5), patch.object(
            Config, "MIN_AUDIENCE_SIZE", 1000
        ), patch.object(Config, "MAX_AUDIENCE_SIZE", 50000000):
            is_valid, errors = Config.validate()
            assert is_valid is False
            assert any("META_AD_ACCOUNT_ID" in e for e in errors)

    def test_invalid_account_id_prefix(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", "123"), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", False), patch.object(
            Config, "ENABLE_SLACK_ALERTS", False
        ), patch.object(Config, "GOOGLE_SHEETS_CREDENTIALS", ""), patch.object(
            Config, "FREQUENCY_ALERT_THRESHOLD", 2.5
        ), patch.object(Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.5), patch.object(
            Config, "MIN_AUDIENCE_SIZE", 1000
        ), patch.object(Config, "MAX_AUDIENCE_SIZE", 50000000):
            is_valid, errors = Config.validate()
            assert is_valid is False
            assert any("act_" in e for e in errors)

    def test_frequency_threshold_ordering(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", "act_123"), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", False), patch.object(
            Config, "ENABLE_SLACK_ALERTS", False
        ), patch.object(Config, "GOOGLE_SHEETS_CREDENTIALS", ""), patch.object(
            Config, "FREQUENCY_ALERT_THRESHOLD", 5.0
        ), patch.object(Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.0), patch.object(
            Config, "MIN_AUDIENCE_SIZE", 1000
        ), patch.object(Config, "MAX_AUDIENCE_SIZE", 50000000):
            is_valid, errors = Config.validate()
            assert is_valid is False
            assert any("FREQUENCY_ALERT_THRESHOLD must be less" in e for e in errors)

    def test_audience_size_ordering(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", "act_123"), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", False), patch.object(
            Config, "ENABLE_SLACK_ALERTS", False
        ), patch.object(Config, "GOOGLE_SHEETS_CREDENTIALS", ""), patch.object(
            Config, "FREQUENCY_ALERT_THRESHOLD", 2.5
        ), patch.object(Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.5), patch.object(
            Config, "MIN_AUDIENCE_SIZE", 50000000
        ), patch.object(Config, "MAX_AUDIENCE_SIZE", 1000):
            is_valid, errors = Config.validate()
            assert is_valid is False
            assert any("MAX_AUDIENCE_SIZE" in e for e in errors)

    def test_email_alerts_require_email(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", "act_123"), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", True), patch.object(
            Config, "EMAIL_ADDRESS", ""
        ), patch.object(Config, "ENABLE_SLACK_ALERTS", False), patch.object(
            Config, "GOOGLE_SHEETS_CREDENTIALS", ""
        ), patch.object(Config, "FREQUENCY_ALERT_THRESHOLD", 2.5), patch.object(
            Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.5
        ), patch.object(Config, "MIN_AUDIENCE_SIZE", 1000), patch.object(
            Config, "MAX_AUDIENCE_SIZE", 50000000
        ):
            is_valid, errors = Config.validate()
            assert is_valid is False
            assert any("EMAIL_ADDRESS" in e for e in errors)

    def test_slack_alerts_require_webhook(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", "act_123"), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", False), patch.object(
            Config, "ENABLE_SLACK_ALERTS", True
        ), patch.object(Config, "SLACK_WEBHOOK_URL", ""), patch.object(
            Config, "GOOGLE_SHEETS_CREDENTIALS", ""
        ), patch.object(Config, "FREQUENCY_ALERT_THRESHOLD", 2.5), patch.object(
            Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.5
        ), patch.object(Config, "MIN_AUDIENCE_SIZE", 1000), patch.object(
            Config, "MAX_AUDIENCE_SIZE", 50000000
        ):
            is_valid, errors = Config.validate()
            assert is_valid is False
            assert any("SLACK_WEBHOOK_URL" in e for e in errors)

    def test_invalid_credentials_path(self):
        from _config import Config

        with patch.object(Config, "AD_ACCOUNT_ID", "act_123"), patch.object(
            Config, "ACCESS_TOKEN", "token"
        ), patch.object(Config, "ENABLE_EMAIL_ALERTS", False), patch.object(
            Config, "ENABLE_SLACK_ALERTS", False
        ), patch.object(
            Config, "GOOGLE_SHEETS_CREDENTIALS", "/nonexistent/path/creds.json"
        ), patch.object(Config, "FREQUENCY_ALERT_THRESHOLD", 2.5), patch.object(
            Config, "FREQUENCY_CRITICAL_THRESHOLD", 3.5
        ), patch.object(Config, "MIN_AUDIENCE_SIZE", 1000), patch.object(
            Config, "MAX_AUDIENCE_SIZE", 50000000
        ):
            is_valid, errors = Config.validate()
            assert is_valid is False
            assert any("credentials file not found" in e for e in errors)


class TestCredentialMasking:
    """Test credential masking in print_config"""

    def test_mask_shows_last_4_chars(self):
        from _config import Config

        # Access the mask function via print_config's inner scope
        # Test indirectly by checking Config.print_config doesn't crash
        import io
        from contextlib import redirect_stdout

        with patch.object(Config, "AD_ACCOUNT_ID", "act_1234567890"), patch.object(
            Config, "ACCESS_TOKEN", "abcdefghijklmnop"
        ), patch.object(Config, "EMAIL_ADDRESS", "test@test.com"), patch.object(
            Config, "ENABLE_EMAIL_ALERTS", True
        ), patch.object(Config, "ENABLE_SLACK_ALERTS", False):
            f = io.StringIO()
            with redirect_stdout(f):
                Config.print_config(hide_sensitive=True)
            output = f.getvalue()
            # Should show last 4 chars of access token
            assert "mnop" in output
            # Should NOT show full token
            assert "abcdefghijklmnop" not in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
