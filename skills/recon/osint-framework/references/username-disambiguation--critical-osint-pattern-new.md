# Username Disambiguation — Critical OSINT Pattern (NEW)

**The `yuanhan@mail.tca.org.tw` investigation revealed a universal OSINT trap:**

Common usernames (`yuanhan`, `john`, `admin`, `alex`, `chen`, `wang`, `lee`, `kim`, `smith`, `test`, `demo`, etc.) are **shared by many different people** across platforms. A single username seed like `yuanhan` resolves to **multiple distinct real-world identities**:

| Platform | Displayed Identity | Likely Distinct Person |
|---|---|---|
| GitHub (`github.com/yuanhan`) | **袁晗 / Han Yuan** — 上海財經大學助理教授, 經濟學博士 | Person A |
| GitLab (`gitlab.com/yuanhan`) | **Henry Lee** | Person B |
| Behance (`behance.net/yuanhan`) | **YUAN HAN in USA** (designer) | Person C |
| SoundCloud (`soundcloud.com/yuanhan`) | Located **Shanghai** | Person D |
| TCA Innoserve Awards | `yuanhan@mail.tca.org.tw` — 專案承辦人, 電話 #879 | Person E (target) |

**Key insight**: `yuanhan` is a common romanization for 袁瀚 / 源瀚 / 苑涵 / 遠涵 / 元瀚… — **at least 4-5 different people** actively use this handle. The 110 "high-confidence" accounts from username-scanner are a **collage of multiple identities**, not one person.

### Disambiguation Protocol (Add to Your Workflow)

1. **Treat username hits as "candidate profiles", not confirmed identities**
   - Every `ACCOUNT_EXTERNAL_OWNED` hit from a common username is a *hypothesis*, not a fact.

2. **Require cross-platform attribute correlation for confirmation**
   - Same avatar hash (Gravatar) across GitHub + GitLab + Behance?
   - Same bio snippet ("PhD Economics, Arizona") on LinkedIn + GitHub + personal site?
   - Same email in public commits (GitHub) matching the seed email?
   - Same location (Shanghai / Taipei / USA) declared consistently?

3. **Use "anchor attributes" to cluster profiles into personas**
   - Anchor = rare, specific attribute (personal site URL, ORCID, unique email, published paper DOI, ORCID)
   - Cluster all profiles sharing ≥1 anchor → persona
   - Profiles with zero anchors → "unattributed candidate"

4. **Document attribution confidence per profile**
   - **Confirmed**: ≥2 independent anchors match seed
   - **Probable**: 1 anchor + consistent bio/location
   - **Candidate**: Username match only, no anchors
   - **Different person**: Conflicting anchors (different PhD university, different name, different country)

5. **In reports, always separate "seed-attributed" vs "username-candidate" findings**
   - Seed-attributed: breach events for `yuanhan@mail.tca.org.tw`, TCA contact page listing
   - Username-candidate: 110 username-scanner accounts (flag as "requires disambiguation")

See `spiderfoot-osint` skill for full Disambiguation Protocol, templates, and investigation patterns.
- **Yahoo TW noise traps on cold CJK names** (R1): When the queried Chinese name is rare/cold, Yahoo TW does TWO things that look like hits but aren't: (a) **phonetic / semantic substitution** — "王池川" silently becomes "王治川"/"王義川" and the result list is *all* those substituted names (Wang Yi-chuan, the DPP politician); (b) **`OR` operator is silently dropped** — `"王池川" 老師 OR 教授` becomes `"王池川" 老師 教授` and then `王` (single character), returning 233,000 "王" dictionary entries. Mitigation: never trust a hit count alone — always extract `<h3 class="title"><a href=...>TITLE</a></h3>` titles AND the rendered snippet text and grep for the **exact 3-character name** in the visible text. If `name in title_text` is 0, the count is noise. See `references/cjk-yahoo-tw-noise-trap.md` for the diagnostic recipe + worked example (王池川 2026-06-30), and `scripts/yahoo_cold_name_detector.py` for an automated detector.
- **NDLTD vs TDR captcha asymmetry**: `ndltd.ncl.edu.tw` (國家圖書館 台灣博碩士論文知識加值系統) returns **graphical captcha** on every request when accessed via curl or Playwright from a non-TANet IP — no captcha bypass without (a) TANet IP, (b) library reader account, or (c) OCR. `tdr.lib.ntu.edu.tw` (台大 TDR, different system) does **not** captcha-block but suffers from Tor-SOCKS5 DNS instability. For thesis searches, prefer TDR first; NDLTD only if you can satisfy one of the three conditions.
- **Tor-SOCKS5 DNS for .edu.tw / .gov.tw**: `tdr.lib.ntu.edu.tw`, `moe.edu.tw` and similar Taiwan academic domains **sometimes time out** via `curl --socks5-hostname 127.0.0.1:9050` (curl exit 28, ~12s) — this is the Tor exit's DNS resolution failing, NOT a block. Fallback: Playwright (uses system DNS) or direct curl without Tor. Don't waste cycles re-trying Tor.
- **Legal**: Always verify OSINT is legal in target jurisdiction
- **Privacy laws**: GDPR (EU), CCPA (California), LGPD (Brazil) restrict personal data collection
- **API costs**: Many services have paid tiers beyond free limits
- **Rate limiting**: Aggressive scraping triggers IP bans — use VPN/proxy rotation
- **Data freshness**: OSINT data can be stale — cross-reference with timestamps
- **Attribution**: OSINT alone may not be sufficient for legal attribution
- **OPSEC**: Your searches are logged by providers — use anonymous infrastructure for sensitive ops
