"""
Google Sheets Writer for Meta Ads Quality Control
Writes results to Google Sheets for reporting
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from _config import Config

logger = logging.getLogger(__name__)


class GoogleSheetsWriter:
    """Writer for Google Sheets output"""

    def __init__(self, spreadsheet_id: Optional[str] = None, credentials_path: Optional[str] = None):
        """
        Initialize Google Sheets writer

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            credentials_path: Path to service account credentials JSON
        """
        self.spreadsheet_id = spreadsheet_id or Config.SPREADSHEET_ID
        self.credentials_path = credentials_path or Config.GOOGLE_SHEETS_CREDENTIALS

        if not self.spreadsheet_id or not self.credentials_path:
            logger.warning("Google Sheets not configured, output will be skipped")
            self.service = None
            return

        try:
            # Load credentials and build service
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info(f"Initialized Google Sheets writer for spreadsheet: {self.spreadsheet_id}")
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
            self.service = None

    def write_dashboard(
        self,
        health_score: int,
        account_name: str,
        issues_summary: Dict[str, int],
        last_run: str
    ) -> bool:
        """
        Write dashboard summary

        Args:
            health_score: Overall health score
            account_name: Name of ad account
            issues_summary: Dictionary with count of issues by severity
            last_run: Timestamp of last run

        Returns:
            True if written successfully
        """
        if not self.service:
            return False

        try:
            # Prepare data
            data = [
                ['Meta Ads Quality Control Dashboard'],
                [''],
                ['Last Updated', last_run],
                ['Account', account_name],
                ['Health Score', health_score],
                [''],
                ['Issues Summary'],
                ['Critical Issues', issues_summary.get('critical', 0)],
                ['High Priority', issues_summary.get('high', 0)],
                ['Medium Priority', issues_summary.get('medium', 0)],
                ['Low Priority', issues_summary.get('low', 0)],
            ]

            # Write to Dashboard sheet
            self._write_to_sheet('Dashboard', data, 'A1')

            # Format dashboard
            self._format_dashboard()

            return True
        except Exception as e:
            logger.error(f"Error writing dashboard: {e}")
            return False

    def write_campaign_health(self, campaigns: List[Dict]) -> bool:
        """
        Write campaign health data

        Args:
            campaigns: List of campaign dictionaries with health metrics

        Returns:
            True if written successfully
        """
        if not self.service:
            return False

        try:
            # Prepare headers
            headers = [
                'Campaign Name',
                'Status',
                'Objective',
                'Spend',
                'Impressions',
                'Clicks',
                'Conversions',
                'CPA',
                'ROAS',
                'Frequency',
                'Health Status',
                'Issues'
            ]

            # Prepare data rows
            data = [headers]
            for campaign in campaigns:
                row = [
                    campaign.get('name', ''),
                    campaign.get('status', ''),
                    campaign.get('objective', ''),
                    campaign.get('spend', 0),
                    campaign.get('impressions', 0),
                    campaign.get('clicks', 0),
                    campaign.get('conversions', 0),
                    campaign.get('cpa', 0),
                    campaign.get('roas', 0),
                    campaign.get('frequency', 0),
                    campaign.get('health_status', ''),
                    campaign.get('issues', ''),
                ]
                data.append(row)

            # Write to Campaign Health sheet
            self._write_to_sheet('Campaign Health', data, 'A1')

            return True
        except Exception as e:
            logger.error(f"Error writing campaign health: {e}")
            return False

    def write_creative_fatigue(self, ads: List[Dict]) -> bool:
        """
        Write creative fatigue data

        Args:
            ads: List of ad dictionaries with frequency metrics

        Returns:
            True if written successfully
        """
        if not self.service:
            return False

        try:
            headers = [
                'Ad Name',
                'Campaign',
                'Status',
                'Frequency',
                'Impressions',
                'Reach',
                'Days Running',
                'Fatigue Level',
                'Action Required'
            ]

            data = [headers]
            for ad in ads:
                row = [
                    ad.get('name', ''),
                    ad.get('campaign_name', ''),
                    ad.get('status', ''),
                    ad.get('frequency', 0),
                    ad.get('impressions', 0),
                    ad.get('reach', 0),
                    ad.get('days_running', 0),
                    ad.get('fatigue_level', ''),
                    ad.get('action_required', ''),
                ]
                data.append(row)

            self._write_to_sheet('Creative Fatigue', data, 'A1')

            return True
        except Exception as e:
            logger.error(f"Error writing creative fatigue: {e}")
            return False

    def write_audience_analysis(self, adsets: List[Dict]) -> bool:
        """
        Write audience analysis data

        Args:
            adsets: List of ad set dictionaries with audience metrics

        Returns:
            True if written successfully
        """
        if not self.service:
            return False

        try:
            headers = [
                'Ad Set Name',
                'Campaign',
                'Status',
                'Audience Size',
                'Spend',
                'Results',
                'Cost per Result',
                'Audience Health',
                'Issues'
            ]

            data = [headers]
            for adset in adsets:
                row = [
                    adset.get('name', ''),
                    adset.get('campaign_name', ''),
                    adset.get('status', ''),
                    adset.get('audience_size', 0),
                    adset.get('spend', 0),
                    adset.get('results', 0),
                    adset.get('cost_per_result', 0),
                    adset.get('audience_health', ''),
                    adset.get('issues', ''),
                ]
                data.append(row)

            self._write_to_sheet('Audience Analysis', data, 'A1')

            return True
        except Exception as e:
            logger.error(f"Error writing audience analysis: {e}")
            return False

    def write_conversion_events(self, events: List[Dict]) -> bool:
        """
        Write conversion events data

        Args:
            events: List of conversion event dictionaries

        Returns:
            True if written successfully
        """
        if not self.service:
            return False

        try:
            headers = [
                'Event Name',
                'Event Type',
                'Status',
                'Pixel ID',
                'Last Fired',
                'Match Quality',
                'Issues'
            ]

            data = [headers]
            for event in events:
                row = [
                    event.get('name', ''),
                    event.get('event_type', ''),
                    event.get('status', ''),
                    event.get('pixel_id', ''),
                    event.get('last_fired', ''),
                    event.get('match_quality', ''),
                    event.get('issues', ''),
                ]
                data.append(row)

            self._write_to_sheet('Conversion Events', data, 'A1')

            return True
        except Exception as e:
            logger.error(f"Error writing conversion events: {e}")
            return False

    def write_issues_log(self, issues: List[Dict]) -> bool:
        """
        Write issues log

        Args:
            issues: List of issue dictionaries

        Returns:
            True if written successfully
        """
        if not self.service:
            return False

        try:
            headers = [
                'Timestamp',
                'Severity',
                'Category',
                'Issue Type',
                'Description',
                'Affected Item',
                'Recommendation',
                'Status'
            ]

            data = [headers]
            for issue in issues:
                row = [
                    issue.get('timestamp', datetime.now().isoformat()),
                    issue.get('severity', ''),
                    issue.get('category', ''),
                    issue.get('type', ''),
                    issue.get('description', ''),
                    issue.get('affected_item', ''),
                    issue.get('recommendation', ''),
                    issue.get('status', 'Open'),
                ]
                data.append(row)

            self._write_to_sheet('Issues Log', data, 'A1')

            return True
        except Exception as e:
            logger.error(f"Error writing issues log: {e}")
            return False

    def _write_to_sheet(self, sheet_name: str, data: List[List[Any]], range_start: str = 'A1') -> bool:
        """
        Write data to specific sheet

        Args:
            sheet_name: Name of sheet to write to
            data: 2D list of data to write
            range_start: Starting cell (default A1)

        Returns:
            True if written successfully
        """
        try:
            # Ensure sheet exists
            self._ensure_sheet_exists(sheet_name)

            # Clear existing data
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1:Z1000"
            ).execute()

            # Write new data
            body = {
                'values': data
            }
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_start}",
                valueInputOption='RAW',
                body=body
            ).execute()

            logger.info(f"Successfully wrote {len(data)} rows to {sheet_name}")
            return True

        except HttpError as e:
            logger.error(f"HTTP error writing to sheet {sheet_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error writing to sheet {sheet_name}: {e}")
            return False

    def _ensure_sheet_exists(self, sheet_name: str) -> bool:
        """
        Ensure sheet with given name exists, create if not

        Args:
            sheet_name: Name of sheet

        Returns:
            True if sheet exists or was created
        """
        try:
            # Get existing sheets
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()

            sheets = sheet_metadata.get('sheets', [])
            sheet_names = [sheet['properties']['title'] for sheet in sheets]

            if sheet_name not in sheet_names:
                # Create sheet
                request_body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    }]
                }
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=request_body
                ).execute()
                logger.info(f"Created new sheet: {sheet_name}")

            return True

        except Exception as e:
            logger.error(f"Error ensuring sheet exists: {e}")
            return False

    def _format_dashboard(self) -> bool:
        """Apply formatting to dashboard sheet"""
        try:
            requests = [
                # Bold header
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': self._get_sheet_id('Dashboard'),
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {
                                    'bold': True,
                                    'fontSize': 14
                                }
                            }
                        },
                        'fields': 'userEnteredFormat.textFormat'
                    }
                },
                # Auto-resize columns
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': self._get_sheet_id('Dashboard'),
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 10
                        }
                    }
                }
            ]

            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()

            return True
        except Exception as e:
            logger.error(f"Error formatting dashboard: {e}")
            return False

    def _get_sheet_id(self, sheet_name: str) -> int:
        """Get sheet ID by name"""
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()

            sheets = sheet_metadata.get('sheets', [])
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']

            return 0
        except Exception as e:
            logger.error(f"Error getting sheet ID: {e}")
            return 0
