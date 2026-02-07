# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ARCHITECTURE.md documentation
- CHANGELOG.md for version tracking
- CONTRIBUTING.md for contribution guidelines
- SECURITY.md for security policies
- API pagination support via `fetchAllPages()` for campaigns, ad sets, and ads
- Real pixel health check querying `/adspixels` endpoint with `last_fired_time` validation

### Changed
- GAS script now 1000+ lines (up from 600+)

### Fixed
- `checkPixelHealth()` no longer returns hardcoded `{healthy: true}` - now queries live pixel data
- `countBySeverity` typo (previously `countBySerity`) corrected
- ROAS calculation uses `action_values` instead of `actions` for revenue data
- Date range format uses proper `yyyy-MM-dd` instead of relative string
- README removed references to 9 non-existent Python scripts

## [1.0.0] - 2026-01-27

### Added
- Meta Ads quality control system
- Python scripts for automated monitoring
- Google Apps Script integration
- Comprehensive quality check script
- Daily health check script
- Meta API client module
- Google Sheets writer module
- Email alerts module
- Shared utilities module
- Configuration management
- Google Sheets templates
- Documentation and implementation guides

### Performance
- Type hints throughout codebase
- Comprehensive error handling
- Async HTTP requests support
- Efficient data processing with pandas

### Security
- OAuth 2.0 authentication for Meta API
- Service account authentication for Google Sheets
- Environment variable configuration
- No hard-coded credentials
- Secure email handling

[Unreleased]: https://github.com/Empire-Amplify/meta-ads-quality-control/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Empire-Amplify/meta-ads-quality-control/releases/tag/v1.0.0
