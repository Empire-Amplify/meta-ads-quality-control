# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please help us protect our users.

### How to Report

**DO NOT** use public GitHub issues to report security vulnerabilities.

Instead:

1. **Email**: gordon@empireamplify.com.au (or create a security advisory on GitHub)
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if you have one)
   - Your contact information

### Response Timeline

- **48 hours**: Initial response acknowledging your report
- **7 days**: Assessment of the vulnerability and proposed fix timeline
- **30 days**: Security patch released (for confirmed vulnerabilities)

### Disclosure Policy

- We will credit you in the security advisory (unless you prefer to remain anonymous)
- Please allow us reasonable time to fix the issue before public disclosure
- We will notify you when the fix is released

## Security Considerations

### Data Handling

**What This System Does:**
- Connects to Meta Marketing API to fetch account data
- Reads campaign, ad set, and ad information
- Fetches performance insights and metrics
- Writes reports to Google Sheets
- Sends email alerts about account health

**What This System Does NOT Do:**
- Does NOT modify Meta ads or campaigns (read-only by default)
- Does NOT store sensitive data locally (only in Google Sheets)
- Does NOT share data with third parties
- Does NOT track users or collect personal information

### Credentials Management

**Protected Credentials:**
1. **Meta Access Tokens**
   - Stored in `.env` file (never committed to git)
   - Long-lived tokens (60-day expiration)
   - Scoped to minimum required permissions
   - Rotated regularly

2. **Google Service Account Keys**
   - JSON key file stored securely
   - Never committed to version control
   - Limited to specific spreadsheet access
   - Audited permissions

3. **Email Credentials**
   - SMTP credentials in `.env` file
   - App-specific passwords (not main password)
   - Encrypted in transit (TLS)

**Protection Measures:**
- ✅ `.env` file in `.gitignore`
- ✅ `.env.example` provided (no real credentials)
- ✅ Service account key file in `.gitignore`
- ✅ Credentials loaded from environment variables only
- ✅ No hard-coded credentials in code
- ✅ Credentials validated on startup

### API Security

**Meta Marketing API:**
- ✅ OAuth 2.0 authentication
- ✅ HTTPS only (encrypted in transit)
- ✅ Rate limiting respected (200 calls/hour)
- ✅ Minimum required permissions
- ✅ Access token expiration handling
- ✅ Error messages don't expose sensitive data

**Google Sheets API:**
- ✅ Service account authentication
- ✅ Scoped to specific spreadsheets
- ✅ Read/write permissions only (no delete)
- ✅ TLS encrypted connections
- ✅ Batch requests to minimize calls

### Data Storage

**Local Storage:**
- ❌ No sensitive data cached locally
- ✅ Logs stored in `logs/` directory (in `.gitignore`)
- ✅ Logs rotated daily, retained for 30 days
- ✅ Logs don't contain access tokens or passwords

**Google Sheets Storage:**
- ⚠️ Data stored in Google Sheets (user's Google account)
- ✅ Sheets access controlled by user permissions
- ✅ No payment information or passwords stored
- ✅ Only performance metrics and campaign data

**Recommendations:**
- Share sheets only with authorized users
- Enable 2FA on Google account
- Regular access audits
- Use organization-managed Google Workspace

### Code Security

**Safe Practices:**
- ✅ Input validation on all user inputs
- ✅ Parameterized API requests (no injection)
- ✅ Type hints for type safety
- ✅ Comprehensive error handling
- ✅ No `eval()` or `exec()` usage
- ✅ Dependencies pinned to specific versions

**Potential Risks:**
- ⚠️ Email alerts sent via SMTP (configure securely)
- ⚠️ API tokens in environment (protect .env file)
- ⚠️ Google Sheets data visible to sheet collaborators

### Network Security

**Outbound Connections:**
1. **Meta API**: `graph.facebook.com` (HTTPS)
2. **Google Sheets API**: `sheets.googleapis.com` (HTTPS)
3. **SMTP Server**: Configured server (TLS recommended)

**Firewall Recommendations:**
- Allow outbound HTTPS (443)
- Allow outbound SMTP (587 or 465)
- Block inbound connections (not required)

### Deployment Security

**Local Deployment:**
- ✅ Use virtual environment (isolate dependencies)
- ✅ Restrict file permissions on `.env` (chmod 600)
- ✅ Keep Python and dependencies updated
- ❌ Don't run as root/administrator

**Cloud Deployment:**
- ✅ Use environment variables (not files)
- ✅ Enable VPC/firewall rules
- ✅ Use managed secrets (AWS Secrets Manager, Google Secret Manager)
- ✅ Enable CloudWatch/Cloud Logging
- ✅ Rotate credentials regularly

**Docker Deployment:**
```dockerfile
# Example secure Dockerfile
FROM python:3.9-slim

# Create non-root user
RUN useradd -m -u 1000 metauser
USER metauser

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY scripts/ ./scripts/

# Credentials via environment variables (not in image)
CMD ["python", "scripts/daily_health_check.py"]
```

## Vulnerability Tracking

### Known Limitations

1. **Credential Storage**
   - `.env` file stores credentials in plaintext
   - **Mitigation**: Use environment variables in production, restrict file permissions
   - **Better**: Use secrets manager (AWS/Google)

2. **Email Security**
   - Email alerts sent via SMTP may be intercepted
   - **Mitigation**: Use TLS/SSL for SMTP, app-specific passwords
   - **Better**: Use authenticated email service (SendGrid, AWS SES)

3. **API Rate Limiting**
   - Meta API has rate limits (200 calls/hour standard)
   - **Mitigation**: Implemented exponential backoff
   - **Better**: Use batch requests, cache data

4. **Google Sheets Access**
   - Anyone with sheet access can view data
   - **Mitigation**: Restrict sheet sharing
   - **Better**: Use Google Workspace with organization policies

## Recommendations for Users

### Before Deployment

1. **Test in Sandbox Mode**
   - Use Meta sandbox ad account for testing
   - Test with non-production Google Sheets
   - Verify email alerts work correctly
   - Review debug logs for sensitive data leakage

2. **Secure Credentials**
   - Use long-lived Meta access tokens (60 days)
   - Create dedicated service account for Google Sheets
   - Use app-specific password for email
   - Rotate credentials every 60-90 days

3. **Configure Permissions**
   - Grant minimum Meta API permissions (ads_read only)
   - Restrict Google Sheets to specific sheets (not all)
   - Limit email recipients to authorized personnel

### Ongoing Monitoring

1. **Audit Access**
   - Review Meta Business Manager permissions monthly
   - Audit Google Sheets sharing quarterly
   - Monitor email delivery logs

2. **Update Dependencies**
   - Keep Python updated to latest stable version
   - Run `pip list --outdated` monthly
   - Update dependencies in `requirements.txt`

3. **Monitor Logs**
   - Review logs for failed authentication attempts
   - Check for unusual API usage patterns
   - Monitor email delivery failures

### Data Protection

1. **Meta Business Manager**:
   - Enable 2FA for all users
   - Use system users for scripts (not personal accounts)
   - Grant least privilege permissions
   - Regular access audits

2. **Google Workspace**:
   - Enable 2FA
   - Use organization-managed Google Workspace
   - Set sharing defaults to "organization only"
   - Enable audit logs

3. **Email**:
   - Use app-specific passwords (not main password)
   - Enable TLS for SMTP connection
   - Restrict recipient list
   - Regular review of alert content

## Security Best Practices

### For Users

- ✅ Use strong, unique passwords
- ✅ Enable 2FA on all accounts
- ✅ Restrict access to authorized personnel only
- ✅ Regular security audits
- ✅ Keep software updated
- ✅ Monitor for unusual activity
- ❌ Do NOT share credentials
- ❌ Do NOT commit .env to version control
- ❌ Do NOT use production credentials in development
- ❌ Do NOT expose Google Sheets publicly

### For Contributors

- ✅ Follow secure coding practices
- ✅ Validate all inputs
- ✅ Use type hints for type safety
- ✅ Comprehensive error handling
- ✅ Document security implications
- ✅ Test for common vulnerabilities
- ❌ Do NOT use unsafe functions (eval, exec)
- ❌ Do NOT log sensitive data (tokens, passwords)
- ❌ Do NOT bypass authentication/authorization

## Incident Response

If you believe credentials have been compromised:

1. **Immediately**:
   - Rotate all access tokens
   - Regenerate Google service account keys
   - Change email passwords
   - Review access logs

2. **Within 24 hours**:
   - Audit all recent API calls
   - Review Google Sheets access logs
   - Check email send logs
   - Notify affected parties

3. **Follow-up**:
   - Document incident
   - Update security procedures
   - Implement additional safeguards
   - Consider penetration testing

## Questions?

For security-related questions that are **not vulnerabilities**:
- Create a GitHub issue labeled `security-question`
- Check existing documentation first

For **vulnerabilities**:
- Email security contact (do not use public issues)

## Updates

This security policy may be updated as the project evolves. Check back periodically for updates.

---

**Last Updated**: 2026-01-28
**Version**: 1.0.0
**Maintained By**: Gordon Geraghty
