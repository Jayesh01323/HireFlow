# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

**Email**: jayesh@example.com  
**Subject**: [Security] HireFlow AI Vulnerability Report

Please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if known)

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt within 48 hours
2. **Investigation**: We will investigate the vulnerability promptly
3. **Resolution**: We will work on a fix and release a security update
4. **Credit**: With your permission, we will credit you in the release notes

### Disclosure Policy

- We will fix vulnerabilities before public disclosure
- We will coordinate disclosure timeline with you
- We will credit you for discovering the vulnerability
- We will not disclose your identity without permission

## Security Best Practices

### For Users

1. **Keep Dependencies Updated**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Use Environment Variables**
   - Never commit `.env` files
   - Use strong API keys
   - Rotate credentials regularly

3. **Secure Your Database**
   - Use strong database passwords
   - Enable database encryption in production
   - Regular database backups

4. **Network Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Use firewalls appropriately

### For Developers

1. **Input Validation**
   - Validate all user inputs
   - Sanitize file uploads
   - Use parameterized queries

2. **Secrets Management**
   - Never hardcode credentials
   - Use environment variables
   - Rotate API keys regularly

3. **Code Security**
   - Follow secure coding practices
   - Use dependency scanning
   - Regular security audits

4. **Testing**
   - Write security tests
   - Perform penetration testing
   - Use static analysis tools

## Known Security Considerations

### Current Implementation

1. **API Keys**
   - Stored in environment variables
   - Not logged or exposed in errors
   - Loaded at application startup

2. **Database**
   - SQLite for development
   - SQLAlchemy ORM prevents SQL injection
   - No password encryption implemented yet

3. **File Uploads**
   - PDF parsing with PyMuPDF
   - Basic file type validation
   - No size limits currently

4. **Web Scraping**
   - User-agent rotation
   - Rate limiting implemented
   - No CAPTCHA handling

### Future Security Improvements

- [ ] Implement user authentication
- [ ] Add rate limiting to API endpoints
- [ ] Implement CSRF protection
- [ ] Add file size limits
- [ ] Implement password hashing
- [ ] Add security headers
- [ ] Implement audit logging
- [ ] Add dependency vulnerability scanning

## Dependency Security

We regularly update dependencies to address security vulnerabilities:

```bash
# Check for vulnerabilities
pip check

# Update dependencies
pip install --upgrade -r requirements.txt

# Security audit
pip-audit
```

## Security Audits

### Past Audits
- Initial security review: June 2026
- Dependency vulnerability scan: June 2026

### Scheduled Audits
- Quarterly dependency scans
- Annual security review
- Penetration testing before major releases

## Security Resources

- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection)

## Contact

For security-related questions:
- **Email**: jayesh@example.com
- **GitHub Security**: [Security Advisories](https://github.com/Jayesh01323/HireFlow/security/advisories)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
