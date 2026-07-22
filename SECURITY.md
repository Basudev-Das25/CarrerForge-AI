# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.5.0-alpha | ✅ |
| < 0.5.0 | ❌ |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email: [security@careerforge.ai](mailto:security@careerforge.ai)
3. Include: description, steps to reproduce, potential impact
4. We will respond within 48 hours

## Security Measures

### Data Privacy
- All data stored locally on user's device
- No cloud storage by default
- No telemetry or tracking
- API keys stored locally only

### AI Provider Security
- API keys sent only to selected provider
- HTTPS-only connections to AI services
- No keys logged or stored in plaintext
- Keys can be cleared from settings

### Application Security
- Tauri CSP (Content Security Policy) enforced
- No remote code execution
- No file system access beyond user data directory
- Subprocess isolation for backend

### Update Security
- HTTPS-only update checks
- Signature verification (planned for production)
- No unsigned installer execution
- Version integrity checks

## Dependency Security

We run `npm audit` and `pip audit` regularly. Known vulnerabilities are tracked and resolved.

## Best Practices for Users

1. Keep the application updated
2. Don't share API keys
3. Use strong passwords for AI provider accounts
4. Review backup contents before restoring
5. Report suspicious behavior immediately
