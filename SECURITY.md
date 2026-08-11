# Security Policy

## Reporting a Vulnerability

If you discover a vulnerability in this repository, please report it
privately — do not open a public issue.

**Email:** Create a GitHub Security Advisory:
1. Go to the repository's Security tab
2. Click "Advisories" → "New draft security advisory"
3. Describe the vulnerability, affected files, and reproduction steps

You will receive a response within 72 hours.

## Credential Exposure

If you find that credentials, API keys, tokens, or real target data have
been committed to this repository:

1. **Do not open a public issue.**
2. Create a private security advisory (above).
3. If you control the exposed credential, rotate/revoke it immediately.
4. Include the file path and line number in your report.

## Unsafe Skill Report

If a skill contains dangerous functionality without adequate safeguards:

1. Open an issue with the label `unsafe-skill`.
2. Describe the dangerous functionality and which skill it affects.
3. Suggest a fix (e.g., authorization gate, confirmation prompt).

## Malicious Upstream Dependency

If an upstream dependency or vendored reference contains malicious code:

1. Create a private security advisory.
2. Identify the upstream source, version/commit, and affected files.
3. We will remove the dependency and audit related files.

## Supported Versions

| Version | Supported |
|---------|-----------|
| main    | ✓         |

This repository does not maintain separate release branches.
