"""
Test suite for _shared_utilities.py
Tests core utility functions for Meta Ads Quality Control
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pytest
from _shared_utilities import (
    calculate_budget_pacing,
    calculate_cpa,
    calculate_ctr,
    calculate_frequency,
    calculate_roas,
    detect_anomaly,
    extract_metric_from_actions,
    extract_value_from_action_values,
)


class TestMetricCalculations:
    """Test basic metric calculation functions"""

    def test_calculate_cpa_with_conversions(self):
        """Test CPA calculation with valid conversions"""
        assert calculate_cpa(100.0, 10) == 10.0
        assert calculate_cpa(250.0, 5) == 50.0

    def test_calculate_cpa_no_conversions(self):
        """Test CPA returns None when no conversions"""
        assert calculate_cpa(100.0, 0) is None

    def test_calculate_cpa_zero_spend(self):
        """Test CPA with zero spend"""
        assert calculate_cpa(0.0, 10) == 0.0

    def test_calculate_roas_valid(self):
        """Test ROAS calculation with valid inputs"""
        assert calculate_roas(500.0, 100.0) == 5.0
        assert calculate_roas(300.0, 150.0) == 2.0

    def test_calculate_roas_no_spend(self):
        """Test ROAS returns None when no spend"""
        assert calculate_roas(500.0, 0.0) is None

    def test_calculate_roas_zero_revenue(self):
        """Test ROAS with zero revenue"""
        assert calculate_roas(0.0, 100.0) == 0.0

    def test_calculate_ctr_valid(self):
        """Test CTR calculation with valid inputs"""
        assert calculate_ctr(100, 1000) == 10.0
        assert calculate_ctr(25, 500) == 5.0

    def test_calculate_ctr_no_impressions(self):
        """Test CTR returns None when no impressions"""
        assert calculate_ctr(100, 0) is None

    def test_calculate_ctr_zero_clicks(self):
        """Test CTR with zero clicks"""
        assert calculate_ctr(0, 1000) == 0.0

    def test_calculate_frequency_valid(self):
        """Test frequency calculation with valid inputs"""
        assert calculate_frequency(5000, 1000) == 5.0
        assert calculate_frequency(10000, 5000) == 2.0

    def test_calculate_frequency_no_reach(self):
        """Test frequency returns None when no reach"""
        assert calculate_frequency(5000, 0) is None


class TestMetaAPIExtraction:
    """Test extraction functions for Meta API response data"""

    def test_extract_metric_from_actions_found(self):
        """Test extracting metric when action type exists"""
        actions = [
            {"action_type": "link_click", "value": "50"},
            {"action_type": "purchase", "value": "10"},
        ]
        assert extract_metric_from_actions(actions, "purchase") == 10

    def test_extract_metric_from_actions_not_found(self):
        """Test extracting metric when action type doesn't exist"""
        actions = [
            {"action_type": "link_click", "value": "50"},
        ]
        assert extract_metric_from_actions(actions, "purchase") == 0

    def test_extract_metric_from_actions_empty(self):
        """Test extracting metric from empty actions list"""
        assert extract_metric_from_actions([], "purchase") == 0
        assert extract_metric_from_actions(None, "purchase") == 0

    def test_extract_value_from_action_values_found(self):
        """Test extracting value when action type exists"""
        action_values = [
            {"action_type": "purchase", "value": "250.50"},
            {"action_type": "add_to_cart", "value": "100.00"},
        ]
        assert extract_value_from_action_values(action_values, "purchase") == 250.50

    def test_extract_value_from_action_values_not_found(self):
        """Test extracting value when action type doesn't exist"""
        action_values = [
            {"action_type": "add_to_cart", "value": "100.00"},
        ]
        assert extract_value_from_action_values(action_values, "purchase") == 0.0

    def test_extract_value_from_action_values_empty(self):
        """Test extracting value from empty list"""
        assert extract_value_from_action_values([], "purchase") == 0.0
        assert extract_value_from_action_values(None, "purchase") == 0.0


class TestBudgetPacing:
    """Test budget pacing calculation"""

    def test_budget_pacing_on_track(self):
        """Test budget pacing when on track"""
        result = calculate_budget_pacing(spent=500.0, budget=1000.0, days_elapsed=15, total_days=30)
        assert result["status"] == "on_track"
        assert result["pacing_rate"] == 50.0
        assert result["expected_spend"] == pytest.approx(500.0, rel=1e-6)
        assert result["variance"] == pytest.approx(0.0, abs=0.1)

    def test_budget_pacing_underpacing(self):
        """Test budget pacing when underpacing"""
        result = calculate_budget_pacing(spent=300.0, budget=1000.0, days_elapsed=15, total_days=30)
        assert result["status"] == "underpacing"
        assert result["variance"] < -20

    def test_budget_pacing_overpacing(self):
        """Test budget pacing when overpacing"""
        result = calculate_budget_pacing(spent=700.0, budget=1000.0, days_elapsed=15, total_days=30)
        assert result["status"] == "overpacing"
        assert result["variance"] > 20

    def test_budget_pacing_zero_days(self):
        """Test budget pacing with zero days"""
        result = calculate_budget_pacing(spent=500.0, budget=1000.0, days_elapsed=0, total_days=0)
        assert result["status"] == "unknown"
        assert result["pacing_rate"] == 0

    def test_budget_pacing_zero_budget(self):
        """Test budget pacing with zero budget"""
        result = calculate_budget_pacing(spent=500.0, budget=0.0, days_elapsed=15, total_days=30)
        assert result["status"] == "unknown"


class TestAnomalyDetection:
    """Test anomaly detection functionality"""

    def test_detect_anomaly_normal(self):
        """Test anomaly detection with normal value"""
        result = detect_anomaly(
            current_value=105.0,
            historical_values=[100.0, 102.0, 98.0, 101.0, 99.0],
            threshold=0.5,
        )
        assert result["is_anomaly"] is False
        assert result["severity"] == "normal"

    def test_detect_anomaly_warning(self):
        """Test anomaly detection with warning-level deviation"""
        result = detect_anomaly(
            current_value=160.0,
            historical_values=[100.0, 102.0, 98.0, 101.0, 99.0],
            threshold=0.5,
        )
        assert result["is_anomaly"] is True
        assert result["severity"] == "warning"
        assert result["direction"] == "increase"

    def test_detect_anomaly_critical(self):
        """Test anomaly detection with critical-level deviation"""
        result = detect_anomaly(
            current_value=250.0,
            historical_values=[100.0, 102.0, 98.0, 101.0, 99.0],
            threshold=0.5,
        )
        assert result["is_anomaly"] is True
        assert result["severity"] == "critical"
        assert result["direction"] == "increase"

    def test_detect_anomaly_decrease(self):
        """Test anomaly detection with decrease"""
        result = detect_anomaly(
            current_value=40.0,
            historical_values=[100.0, 102.0, 98.0, 101.0, 99.0],
            threshold=0.5,
        )
        assert result["is_anomaly"] is True
        assert result["direction"] == "decrease"

    def test_detect_anomaly_insufficient_data(self):
        """Test anomaly detection with insufficient historical data"""
        result = detect_anomaly(current_value=100.0, historical_values=[], threshold=0.5)
        assert result["is_anomaly"] is False
        assert result["deviation"] == 0

    def test_detect_anomaly_single_historical_value(self):
        """Test anomaly detection with single historical value"""
        result = detect_anomaly(current_value=150.0, historical_values=[100.0], threshold=0.5)
        # With single value (< 2), function returns early with no anomaly
        assert result["is_anomaly"] is False
        assert result["deviation"] == 0
        assert result["severity"] == "normal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
