"""
Meta Marketing API Client
Wrapper for Meta Marketing API operations
"""

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

from _config import Config

logger = logging.getLogger(__name__)


class MetaAPIClient:
    """Client for interacting with Meta Marketing API"""

    def __init__(
        self, account_id: Optional[str] = None, access_token: Optional[str] = None
    ):
        """
        Initialize Meta API client

        Args:
            account_id: Meta ad account ID (e.g., act_123456789)
            access_token: Meta access token
        """
        self.account_id = account_id or Config.AD_ACCOUNT_ID
        self.access_token = access_token or Config.ACCESS_TOKEN

        if not self.account_id or not self.access_token:
            raise ValueError("Account ID and Access Token are required")

        # Initialize Facebook API
        FacebookAdsApi.init(access_token=self.access_token)
        self.account = AdAccount(self.account_id)

        logger.info(f"Initialized Meta API client for account: {self.account_id}")

    def get_campaigns(
        self, statuses: Optional[List[str]] = None, fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Fetch campaigns from ad account

        Args:
            statuses: List of campaign statuses to filter (ACTIVE, PAUSED, ARCHIVED)
            fields: List of fields to retrieve

        Returns:
            List of campaign dictionaries
        """
        if fields is None:
            fields = [
                Campaign.Field.id,
                Campaign.Field.name,
                Campaign.Field.status,
                Campaign.Field.objective,
                Campaign.Field.daily_budget,
                Campaign.Field.lifetime_budget,
                Campaign.Field.bid_strategy,
                Campaign.Field.special_ad_categories,
                Campaign.Field.created_time,
                Campaign.Field.updated_time,
            ]

        params = {}
        if statuses:
            params["effective_status"] = statuses

        try:
            campaigns = self.account.get_campaigns(fields=fields, params=params)
            return [dict(campaign) for campaign in campaigns]
        except Exception as e:
            logger.error(f"Error fetching campaigns: {e}")
            return []

    def get_adsets(
        self,
        campaign_id: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Fetch ad sets from campaign or account

        Args:
            campaign_id: Optional campaign ID to filter
            statuses: List of ad set statuses to filter
            fields: List of fields to retrieve

        Returns:
            List of ad set dictionaries
        """
        if fields is None:
            fields = [
                AdSet.Field.id,
                AdSet.Field.name,
                AdSet.Field.status,
                AdSet.Field.campaign_id,
                AdSet.Field.daily_budget,
                AdSet.Field.lifetime_budget,
                AdSet.Field.bid_amount,
                AdSet.Field.billing_event,
                AdSet.Field.optimization_goal,
                AdSet.Field.targeting,
                AdSet.Field.promoted_object,
                AdSet.Field.created_time,
                AdSet.Field.updated_time,
            ]

        params = {}
        if statuses:
            params["effective_status"] = statuses

        try:
            if campaign_id:
                campaign = Campaign(campaign_id)
                adsets = campaign.get_ad_sets(fields=fields, params=params)
            else:
                adsets = self.account.get_ad_sets(fields=fields, params=params)

            return [dict(adset) for adset in adsets]
        except Exception as e:
            logger.error(f"Error fetching ad sets: {e}")
            return []

    def get_ads(
        self,
        adset_id: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Fetch ads from ad set or account

        Args:
            adset_id: Optional ad set ID to filter
            statuses: List of ad statuses to filter
            fields: List of fields to retrieve

        Returns:
            List of ad dictionaries
        """
        if fields is None:
            fields = [
                Ad.Field.id,
                Ad.Field.name,
                Ad.Field.status,
                Ad.Field.adset_id,
                Ad.Field.campaign_id,
                Ad.Field.creative,
                Ad.Field.tracking_specs,
                Ad.Field.conversion_specs,
                Ad.Field.created_time,
                Ad.Field.updated_time,
            ]

        params = {}
        if statuses:
            params["effective_status"] = statuses

        try:
            if adset_id:
                adset = AdSet(adset_id)
                ads = adset.get_ads(fields=fields, params=params)
            else:
                ads = self.account.get_ads(fields=fields, params=params)

            return [dict(ad) for ad in ads]
        except Exception as e:
            logger.error(f"Error fetching ads: {e}")
            return []

    def get_insights(
        self,
        level: str = "account",
        object_id: Optional[str] = None,
        date_preset: str = "last_7d",
        time_range: Optional[Dict] = None,
        fields: Optional[List[str]] = None,
        breakdowns: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Fetch insights/metrics

        Args:
            level: Reporting level (account, campaign, adset, ad)
            object_id: ID of specific object (campaign/adset/ad)
            date_preset: Date range preset (last_7d, last_30d, etc.)
            time_range: Custom time range dict with 'since' and 'until'
            fields: Metrics to retrieve
            breakdowns: Dimension breakdowns

        Returns:
            List of insight dictionaries
        """
        if fields is None:
            fields = [
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.reach,
                AdsInsights.Field.frequency,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpc,
                AdsInsights.Field.cpm,
                AdsInsights.Field.cpp,
                AdsInsights.Field.actions,
                AdsInsights.Field.action_values,
                AdsInsights.Field.cost_per_action_type,
                AdsInsights.Field.conversions,
                AdsInsights.Field.conversion_values,
            ]

        params = {
            "level": level,
        }

        if time_range:
            params["time_range"] = time_range
        else:
            params["date_preset"] = date_preset

        if breakdowns:
            params["breakdowns"] = breakdowns

        try:
            if object_id:
                # Get insights for specific object
                if level == "campaign":
                    obj = Campaign(object_id)
                elif level == "adset":
                    obj = AdSet(object_id)
                elif level == "ad":
                    obj = Ad(object_id)
                else:
                    obj = self.account
                insights = obj.get_insights(fields=fields, params=params)
            else:
                # Get insights at account level
                insights = self.account.get_insights(fields=fields, params=params)

            return [dict(insight) for insight in insights]
        except Exception as e:
            logger.error(f"Error fetching insights: {e}")
            return []

    def get_conversion_events(self) -> List[Dict]:
        """
        Fetch conversion events (pixels, custom conversions)

        Returns:
            List of conversion event dictionaries
        """
        try:
            params = {
                "fields": [
                    "id",
                    "name",
                    "status",
                    "event_type",
                    "custom_event_type",
                    "pixel",
                    "is_archived",
                ]
            }
            events = self.account.get_custom_conversions(params=params)
            return [dict(event) for event in events]
        except Exception as e:
            logger.error(f"Error fetching conversion events: {e}")
            return []

    def get_pixels(self) -> List[Dict]:
        """
        Fetch pixels configured for account

        Returns:
            List of pixel dictionaries
        """
        try:
            params = {
                "fields": [
                    "id",
                    "name",
                    "code",
                    "is_unavailable",
                    "last_fired_time",
                ]
            }
            pixels = self.account.get_ads_pixels(params=params)
            return [dict(pixel) for pixel in pixels]
        except Exception as e:
            logger.error(f"Error fetching pixels: {e}")
            return []

    def get_delivery_estimate(self, targeting: Dict, optimization_goal: str) -> Dict:
        """
        Get delivery estimate for targeting spec

        Args:
            targeting: Targeting specification
            optimization_goal: Campaign optimization goal

        Returns:
            Delivery estimate dictionary
        """
        try:
            params = {
                "targeting_spec": targeting,
                "optimization_goal": optimization_goal,
            }
            estimate = self.account.get_delivery_estimate(params=params)
            return dict(estimate[0]) if estimate else {}
        except Exception as e:
            logger.error(f"Error fetching delivery estimate: {e}")
            return {}

    def check_account_quality(self) -> Dict:
        """
        Check account quality metrics

        Returns:
            Account quality dictionary
        """
        try:
            fields = [
                "account_status",
                "disable_reason",
                "business_country_code",
                "currency",
                "timezone_name",
                "amount_spent",
                "balance",
                "spend_cap",
            ]
            account_info = self.account.api_get(fields=fields)
            return dict(account_info)
        except Exception as e:
            logger.error(f"Error checking account quality: {e}")
            return {}

    def get_date_range(self, days: int) -> Dict:
        """
        Helper to create date range dict

        Args:
            days: Number of days to look back

        Returns:
            Time range dictionary with 'since' and 'until'
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return {
            "since": start_date.strftime("%Y-%m-%d"),
            "until": end_date.strftime("%Y-%m-%d"),
        }
