---
name: security-code-review
description: Review code in Hermes with a Claude-Code-style security-focused findings-first
  workflow.
version: 1.0.0
license: MIT
metadata:
  hermes_homepage: https://github.com/Piebald-AI/claude-code-system-prompts
  hermes_origin: import
tags:
- claude-code
- security
- review
- findings
- auth
- injection
related_skills: []
---

# Claude-Code-Style Security Review

Use this skill when the primary task is to find security-relevant issues in code or configuration changes.

## When To Use

Load this skill when:

- the user asks for a security review
- changes touch authn, authz, secrets, file access, persistence, input handling, or network boundaries
- a general review surfaced possible security concerns that need deeper inspection

## Security Review Contract

You are not doing a general style review. You are looking for exploitable or trust-boundary-relevant issues.

Prioritize:

1. authentication and authorization flaws
2. injection risks
3. unsafe deserialization or dynamic execution
4. secret leakage or insecure secret handling
5. path traversal and filesystem trust issues
6. SSRF, open redirects, and outbound trust misuse
7. data exposure, multi-tenant leakage, or missing access checks
8. weak validation at trust boundaries

## Workflow

### 1. Understand The Trust Boundary

Identify:

- where untrusted input enters
- where permissions are checked
- where secrets are read, stored, or transmitted
- where filesystem, database, or network boundaries are crossed

### 2. Inspect Risky Surfaces

Look closely at:

- request parsing
- query construction
- file path handling
- shell or process invocation
- token/session handling
- serialization/deserialization
- redirects and URL fetching
- object ownership or tenant scoping

### 3. Verify When Practical

If feasible, validate concerns with evidence:

- targeted tests
- malicious or adversarial inputs
- negative-path checks
- permission-boundary scenarios

Do not claim exploitability without basis, but do not require a full exploit proof to raise a risk.

## Output Format

Report findings first.

Each finding should include:

1. severity or impact
2. file and location if available
3. the vulnerable behavior
4. why it matters
5. a realistic attack or failure scenario

Use this structure:

```md
Findings

1. [severity] `path/to/file:line` - concise statement of the security issue and why it matters.

Open Questions / Assumptions

- assumptions affecting confidence

Verification Notes

- checks run
- notable results
```

If no findings are discovered:

```md
No security findings.

Residual risks / gaps:
- unverified assumptions, untested boundaries, or areas not executed
```

## Findings Bar

Do not dilute the review with generic style comments.

Good findings:

- user-controlled path reaches file open without canonicalization or allowlisting
- auth check occurs after data fetch and leaks unauthorized metadata
- token is logged or returned in an error path
- SQL or shell command construction incorporates untrusted input

Weak findings:

- naming preferences
- formatting issues
- architecture opinions with no security consequence

## Interaction With Other Skills

- Use `claude-code-review-executor` for a broader non-security review.
- Use `claude-code-pr-executor` after security review if the user wants a PR-ready writeup.
- Use `claude-code-coding-executor` if the user asks to fix confirmed issues.

## Suggested Internal Checklist

Before concluding, confirm:

- trust boundaries were identified
- findings are actually security-relevant
- severity reflects realistic impact
- claims are not overstated beyond the evidence
