# Contributing to Meta Ads Quality Control

Thank you for your interest in contributing! This project helps automate Meta Ads quality control and monitoring.

## Code of Conduct

This project adheres to professional standards. By participating, you are expected to:
- Be respectful and professional in all interactions
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the project

## How Can I Contribute?

### Reporting Bugs

Found a bug? Help us improve by creating a detailed bug report.

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with details:
   - Description of the bug
   - Python version and environment
   - Meta API version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and stack traces
   - Configuration (anonymized)

### Suggesting Features

Have an idea for improvement?

1. **Describe the problem** it solves
2. **Explain your proposed solution**
3. **Consider alternatives** you've thought about
4. **Provide context** on why this would be valuable

### Adding New Features

Want to add a new monitoring feature or quality check?

1. **Create an issue first** to discuss the feature
2. **Follow the existing code structure**:
   - Add new checks to appropriate script
   - Use type hints
   - Add comprehensive error handling
   - Follow existing naming conventions
   - Add docstrings to all functions

### Improving Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples or use cases
- Improve setup instructions
- Add troubleshooting guides

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly** (see Testing Guidelines below)
5. **Update documentation** (README, CHANGELOG, docs/)
6. **Commit your changes**
7. **Push to your branch**
8. **Create a Pull Request**

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- Meta Business Manager account (for testing)
- Google Cloud project (for Sheets API)

### Local Setup

```bash
# Clone repository
git clone https://github.com/yourusername/meta-ads-quality-control.git
cd meta-ads-quality-control

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials (DO NOT commit this file)
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-mock pytest-cov

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=scripts --cov-report=term-missing

# Run specific test file
pytest tests/test_config.py -v
```

## Code Style Guidelines

### Python

- **PEP 8 compliance** - Follow Python style guide
- **Type hints** - Use type annotations for all functions
- **Docstrings** - Document all modules, classes, and functions
- **f-strings** - Use f-strings for string formatting
- **Async/await** - Use async for I/O-bound operations
- **Error handling** - Use try/except with specific exceptions

### Example

```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def fetch_campaign_data(account_id: str, date_range: Optional[str] = "last_7d") -> Dict:
    """
    Fetch campaign data from Meta API.

    Args:
        account_id: Meta Ad Account ID (e.g., 'act_123456789')
        date_range: Date range for insights (default: 'last_7d')

    Returns:
        Dictionary containing campaign data and metrics

    Raises:
        MetaAPIError: If API request fails
        ValueError: If account_id is invalid
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Failed to fetch campaign data: {e}")
        raise
```

### Comments

- **Explain WHY, not WHAT** - Code should be self-documenting
- **Use clear variable names** - Avoid cryptic abbreviations
- **Add comments for complex logic** only

### Formatting

- **4-space indentation**
- **Line length**: Prefer < 100 characters
- **Blank lines**: Separate logical sections
- **Imports**: Group stdlib, third-party, local (separated by blank lines)

```python
# Standard library
import os
from typing import Dict

# Third-party
import pandas as pd
from facebook_business.api import FacebookAdsApi

# Local
from scripts._config import Config
```

## Pull Request Process

1. **Update documentation**:
   - CHANGELOG.md (under `[Unreleased]`)
   - README.md (if adding major feature)
   - Docstrings and inline comments
   - Architecture docs if needed

2. **Test manually**:
   - Run all existing tests
   - Test new features with real Meta API (in sandbox)
   - Verify Google Sheets integration works
   - Check email alerts if modified

3. **Complete PR checklist**:
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Type hints added
   - [ ] Docstrings added
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented with migration path)
   - [ ] Tested with Meta API sandbox
   - [ ] No credentials committed

4. **PR will be reviewed for**:
   - Code quality and readability
   - Type safety (mypy clean)
   - Error handling completeness
   - Test coverage
   - Documentation completeness
   - Security considerations

5. **After approval**:
   - PR will be merged to main branch
   - Changes will be included in next release
   - You'll be credited in release notes!

## Testing Guidelines

### Manual Testing Checklist

Before submitting a PR, verify:

**Meta API Integration**
- [ ] API authentication works
- [ ] Account data fetched correctly
- [ ] Campaign data retrieved
- [ ] Insights data accurate
- [ ] Error handling works (try with invalid account ID)
- [ ] Rate limiting handled gracefully

**Google Sheets Integration**
- [ ] Sheet creation works
- [ ] Data writes correctly
- [ ] Formatting applied properly
- [ ] Charts generated (if applicable)
- [ ] No data loss on updates

**Email Alerts**
- [ ] Emails sent successfully
- [ ] HTML formatting correct
- [ ] Attachments work (if applicable)
- [ ] Recipients correct
- [ ] Subject line appropriate

**Error Handling**
- [ ] API errors handled gracefully
- [ ] Network errors caught
- [ ] Invalid data handled
- [ ] Logs written correctly
- [ ] User-friendly error messages

### Unit Testing

```python
# Example unit test
import pytest
from scripts._shared_utilities import format_currency


def test_format_currency():
    assert format_currency(1234.56) == "$1,234.56"
    assert format_currency(0) == "$0.00"
    assert format_currency(-100.5) == "-$100.50"


def test_format_currency_invalid():
    with pytest.raises(TypeError):
        format_currency("invalid")
```

## Adding New Quality Checks

When adding a new quality check:

1. **Create issue first** to discuss the check
2. **Add to appropriate script**:
   - Daily checks → `daily_health_check.py`
   - Weekly checks → `comprehensive_quality_check.py`
3. **Follow pattern**:
   ```python
   def check_new_quality_metric(data: Dict) -> Dict:
       """
       Check [description of what is checked].

       Args:
           data: Campaign/Ad Set/Ad data from Meta API

       Returns:
           Dictionary with:
               - status: "pass", "warning", or "fail"
               - message: Description of finding
               - recommendation: Action to take (if status != "pass")
       """
       # Implementation
       pass
   ```
4. **Add tests** for the new check
5. **Update documentation**
6. **Add to CHANGELOG.md**

## Questions?

- **Check existing issues** for similar questions
- **Read documentation** (README, docs/, ARCHITECTURE.md)
- **Create a discussion** for general questions
- **Create an issue** for specific bugs or feature requests

## Thank You!

Every contribution, whether it's fixing a typo or adding a major feature, helps make this project better for everyone using Meta Ads quality control.

Your contributions are greatly appreciated! 🎉
