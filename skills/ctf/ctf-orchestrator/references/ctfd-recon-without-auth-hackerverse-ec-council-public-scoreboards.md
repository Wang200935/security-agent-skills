# CTFd Recon Without Auth (Hackerverse, EC-Council, Public Scoreboards)

When a CTF platform (e.g., Hackerverse) puts `/challenges` behind SSO/CyberArk but still has public CTFd endpoints, you can recover the full challenge list, categories, values, and solve counts **without an account**:

```bash
# 1. Public scoreboard (always public on CTFd)
curl -sk "https://<host>/api/v1/scoreboard?page=1" -o sb.json
# Returns top N scorers with: pos, account_id, account_url (/users/<id>), name, score

# 2. Public user pages reveal challenge names + categories + values + solve times
for uid in $(jq -r '.data[].account_id' sb.json | head); do
  curl -sk "https://<host>/users/$uid" | grep -oE 'category=[^&]+|<h[3-6][^>]*>[^<]+'
done
# vasanthadithya's profile (top scorer) often shows the full challenge list in plain text

# 3. Try non-standard endpoints before giving up
for ep in /api/v1/scoreboard /api/v1/users /api/v1/notifications; do
  curl -sk "https://<host>$ep?page=1" -w 'HTTP %{http_code}\n' -o /tmp/x
done
# /api/v1/scoreboard, /api/v1/users are usually public; /api/v1/challenges is NOT
```

**Top scorers' public `/users/<id>` HTML pages** embed the entire challenge roster (`June 2026: Challenge A`, `June 2026: Challenge B`, etc.) with category and value. This reveals the challenge taxonomy **before** solving a single one. CTFd profile pages also leak challenge ids via anchor hrefs like `challenges/<id>` or hash-fragment links like `challenge:148`. Even without an auth session, you can map challenge names → ids.
