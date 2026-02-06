"""
Test suite for _meta_api_client.py
Tests API client retry logic, rate limiting, and error handling
"""

import os
import sys
import time
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pytest


@pytest.fixture
def api_client():
    """Create a MetaAPIClient with mocked external dependencies."""
    with (
        patch("_meta_api_client.Config") as mock_config,
        patch("_meta_api_client.FacebookAdsApi"),
        patch("_meta_api_client.AdAccount"),
    ):
        mock_config.AD_ACCOUNT_ID = "act_123"
        mock_config.ACCESS_TOKEN = "token"
        from _meta_api_client import MetaAPIClient

        client = MetaAPIClient(account_id="act_123", access_token="token")
        client._last_call_time = 0.0  # Prevent rate limit waits in tests
        yield client


class TestClientInit:
    """Test client initialization"""

    def test_init_with_credentials(self, api_client):
        """Test client initializes with provided credentials"""
        assert api_client.account_id == "act_123"
        assert api_client.access_token == "token"

    def test_init_missing_credentials(self):
        """Test init raises ValueError without credentials"""
        with (
            patch("_meta_api_client.Config") as mock_config,
            patch("_meta_api_client.FacebookAdsApi"),
            patch("_meta_api_client.AdAccount"),
        ):
            mock_config.AD_ACCOUNT_ID = ""
            mock_config.ACCESS_TOKEN = ""
            from _meta_api_client import MetaAPIClient

            with pytest.raises(ValueError):
                MetaAPIClient(account_id="", access_token="")


class TestRateLimiting:
    """Test rate limiting behavior"""

    def test_no_wait_on_first_call(self, api_client):
        """Test no delay when enough time has passed since last call"""
        api_client._last_call_time = 0.0
        start = time.time()
        api_client._rate_limit()
        elapsed = time.time() - start
        assert elapsed < 0.1

    def test_enforces_minimum_interval(self, api_client):
        """Test rate limiting sleeps when calls are too close together"""
        with patch("time.sleep") as mock_sleep:
            api_client._last_call_time = time.time()  # Just called
            api_client._rate_limit()
            mock_sleep.assert_called_once()


class TestCallWithRetry:
    """Test _call_with_retry method"""

    def test_success_on_first_try(self, api_client):
        """Test successful call returns without retry"""
        mock_func = MagicMock(return_value=["result"])
        result = api_client._call_with_retry(mock_func, key="value")
        assert result == ["result"]
        mock_func.assert_called_once_with(key="value")

    def test_retries_on_connection_error(self, api_client):
        """Test retry on ConnectionError"""
        with patch("time.sleep"):
            mock_func = MagicMock(
                side_effect=[ConnectionError("refused"), ["success"]]
            )
            result = api_client._call_with_retry(mock_func)
            assert result == ["success"]
            assert mock_func.call_count == 2

    def test_retries_on_timeout_error(self, api_client):
        """Test retry on TimeoutError"""
        with patch("time.sleep"):
            mock_func = MagicMock(
                side_effect=[TimeoutError("timed out"), ["success"]]
            )
            result = api_client._call_with_retry(mock_func)
            assert result == ["success"]

    def test_exhausts_max_retries(self, api_client):
        """Test raises after exhausting all retries"""
        with patch("time.sleep"):
            mock_func = MagicMock(side_effect=ConnectionError("refused"))
            with pytest.raises(ConnectionError):
                api_client._call_with_retry(mock_func, max_retries=2)
            assert mock_func.call_count == 3  # 1 initial + 2 retries

    def test_exponential_backoff(self, api_client):
        """Test backoff wait time increases exponentially"""
        with patch("time.sleep") as mock_sleep:
            mock_func = MagicMock(
                side_effect=[
                    ConnectionError("1"),
                    ConnectionError("2"),
                    ["success"],
                ]
            )
            api_client._call_with_retry(mock_func, max_retries=3)
            # ConnectionError backoff: 2^0 * 2 = 2s, 2^1 * 2 = 4s
            sleep_calls = mock_sleep.call_args_list
            assert sleep_calls[0][0][0] == 2
            assert sleep_calls[1][0][0] == 4

    def test_non_retryable_error_raises_immediately(self, api_client):
        """Test that generic exceptions are not retried"""
        mock_func = MagicMock(side_effect=ValueError("bad input"))
        with pytest.raises(ValueError):
            api_client._call_with_retry(mock_func)
        mock_func.assert_called_once()


class TestAPIMethods:
    """Test that API methods delegate to _call_with_retry"""

    def _mock_cursor(self):
        """Create a mock cursor that supports iteration."""
        cursor = MagicMock()
        cursor.__iter__ = MagicMock(return_value=iter([]))
        return cursor

    def test_get_campaigns_uses_retry(self, api_client):
        api_client._call_with_retry = MagicMock(return_value=self._mock_cursor())
        api_client.get_campaigns()
        api_client._call_with_retry.assert_called_once()

    def test_get_adsets_uses_retry(self, api_client):
        api_client._call_with_retry = MagicMock(return_value=self._mock_cursor())
        api_client.get_adsets()
        api_client._call_with_retry.assert_called_once()

    def test_get_ads_uses_retry(self, api_client):
        api_client._call_with_retry = MagicMock(return_value=self._mock_cursor())
        api_client.get_ads()
        api_client._call_with_retry.assert_called_once()

    def test_get_insights_uses_retry(self, api_client):
        api_client._call_with_retry = MagicMock(return_value=self._mock_cursor())
        api_client.get_insights()
        api_client._call_with_retry.assert_called_once()

    def test_get_pixels_uses_retry(self, api_client):
        api_client._call_with_retry = MagicMock(return_value=self._mock_cursor())
        api_client.get_pixels()
        api_client._call_with_retry.assert_called_once()

    def test_get_conversion_events_uses_retry(self, api_client):
        api_client._call_with_retry = MagicMock(return_value=self._mock_cursor())
        api_client.get_conversion_events()
        api_client._call_with_retry.assert_called_once()

    def test_check_account_quality_uses_retry(self, api_client):
        api_client._call_with_retry = MagicMock(return_value=MagicMock())
        api_client.check_account_quality()
        api_client._call_with_retry.assert_called_once()

    def test_get_date_range(self, api_client):
        """Test date range helper returns valid structure"""
        result = api_client.get_date_range(7)
        assert "since" in result
        assert "until" in result
