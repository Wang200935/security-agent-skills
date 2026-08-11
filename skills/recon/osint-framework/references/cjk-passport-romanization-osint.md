# Taiwan Passport Romanization OSINT（護照拼音找中文姓名）

> **Use case**: User knows a person's Chinese name (e.g. 王池川) and suspects
> the person has an online presence tied to their **passport English spelling**
> — academic papers, LinkedIn, Twitter, ORCID. You can't use the CJK-name
> Yahoo playbook alone because the person never types their Chinese name on
> those platforms. You need to enumerate the romanization variants of the
> Chinese name and search those.

> **Verified**: 2026-06-30 across the 王池川 session — turned a zero-hit
> Chinese-name search into 3 confirmed candidates (NYCU 王啟川 fuzzy, NTU 王繼娟
> via ORCID, Twitter `@wangchihchuan` = 「小王」幽靈帳號).

## Why the CJK-name playbook alone fails for 「學術人」

| Platform | Why Chinese-name search fails |
|:---|:---|
| ORCID | 學者都用護照拼音註冊，從不寫中文名 |
| Google Scholar | `author:王池川` → 0 命中（即便有這人也幾乎不會用中文登記） |
| ResearchGate / Scopus | 同上，全英文 |
| Twitter / X | 帳號 = 護照拼音（`@wangchihchuan`） |
| LinkedIn | 顯示名是 `Chi-Chuan Wang`，搜中文完全搜不到 |

**Solution**: 把中文姓名 → 護照拼音 5 種變體 → 用 API + Playwright 對每個變體查學術 / 社交平台。

---

## Step 1 — Generate the 5 (actually 7) passport romanization variants

台灣護照允許的拼音系統：

| 字 | 漢語拼音 | 威妥瑪 (Wade-Giles) | 國音第二式 | 耶魯 (Yale) | 通用拼音 | 注音二式 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 王 | Wang | Wang | Wang | Wang | Wang | Wang |
| 池 | chi | ch'ih (實務→chih) | chr | chr | chi | chr |
| 川 | chuan | ch'uan | chuan | chwan | chuan | chuan |

**王池川** 護照拼法的常見組合（依實務頻率排序）：
1. `WANG CHI-CHUAN` — 漢語拼音（最常見，2010 後主流）
2. `WANG CHIH-CHUAN` — 威妥瑪（1990-2008 護照主流）
3. `WANG CHR-CHUAN` — 國音第二式（少數）
4. `WANG CHI-CHWAN` — 耶魯（少數）
5. `WANG CHIH-CHWAN` — 混合（罕見）

**Pivotal lesson (王池川 2026-06-30)**：這 5 種變體中，
- `wangchichuan`（#1）→ TradingView 幽靈帳號
- `wangchihchuan`（#2 威妥瑪）→ Twitter 真實 `@wangchihchuan`（顯示「小王」）
- **若只查 #1 變體會漏掉 #2 真實身份**

→ **必須 5 種都查**，不能用單一假設。

### 自動產生腳本：`scripts/passport_romanize.py`

（見該檔案）給定中文姓名，輸出 7+ 種 username / scholar 查詢變體：

```bash
python3 scripts/passport_romanize.py "王池川"
# → wangchichuan, wang_chichuan, chichuan_wang, ...
# → wangchihchuan, chihchuan_wang, ...   (Wade-Giles)
# → wangchrchuan, chrchuan_wang, ...     (Guoyin R2)
# → wangchichwan, chichwan_wang, ...     (Yale)
```

---

## Step 2 — Query strategy（優先順序）

### A. OpenAlex API ⭐⭐⭐ KILLER for academics

OpenAlex 是免費的學術 metadata 索引，比 Google Scholar 更強：
- **不用 captcha**
- **不用登入**
- 每個 author 有 ORCID + institution + topic tags

```bash
# Search by display name
curl -s "https://api.openalex.org/authors?search=Chi-Chuan+Wang" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('results', [])[:5]:
    inst = r.get('last_known_institution') or {}
    print(f\"{r.get('display_name')} | {inst.get('display_name')} ({inst.get('country_code')})\")
    print(f\"  works: {r.get('works_count')}, cited: {r.get('cited_by_count')}, ORCID: {r.get('orcid')}\")
"
```

**Why OpenAlex > Google Scholar for this task**:
- 一個 query 直接給 ORCID、學校、發表數、被引數
- 可以排序 / 過濾 country / topic
- 兩個同名「Chi-Chuan Wang」會用 ORCID + works_count 區分（NYCU 王啟川 h=74 vs NTU 王繼娟 h=24）

### B. ORCID Public API

拿到 ORCID 之後，直接查：

```bash
curl -s "https://pub.orcid.org/v3.0/<ORCID-ID>" -H "Accept: application/json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
# Chinese name lives in other-names
person = d.get('person', {})
for o in person.get('other-names', {}).get('other-name', []):
    print(f\"Other name: {o.get('content')}\")
# Employment history is most useful
emp = d.get('activities-summary', {}).get('employments', {}).get('affiliation-group', [])
for e in emp:
    for s in e.get('summaries', []):
        es = s.get('employment-summary', {})
        org = es.get('organization', {})
        start = es.get('start-date', {})
        end = es.get('end-date', {})
        print(f\"{es.get('role-title')} @ {org.get('name')} ({start.get('year','?')}-{end.get('year','present')})\")
"
```

ORCID 直接列「other-name：王繼娟」這種關鍵 disambiguation 證據。

### C. Yahoo TW with `\"Chi-Chuan Wang\" Taiwan` ⭐⭐⭐

Yahoo TW 不擋 bot UA，且會把英文姓名查到的 LinkedIn / Scholar / 校網都索引進去。配合護照拼音查：

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
curl -sL --max-time 30 -A "$UA" "https://tw.search.yahoo.com/search?p=%22Chi-Chuan+Wang%22+Taiwan"
curl -sL --max-time 30 -A "$UA" "https://tw.search.yahoo.com/search?p=%22Chih-Chuan+Wang%22+Taiwan"
```

**Real session output (王池川 2026-06-30)**：
- Yahoo TW 抓到 `chi-chuan-emma-wang` LinkedIn (NTU 藥學系) — 中文名差很多但 ORCID 確認
- Yahoo TW 抓到 `ccwang-lab` LinkedIn (NYCU 王啟川講座教授)
- Yahoo TW 抓到 NYCU scholar.nycu.edu.tw 個人頁

### D. fxtwitter / vxtwitter / xcancel API (Twitter 帳號驗證)

所有 Nitter instance（nitter.net / nitter.cz / nitter.privacydev.net / nitter.poast.org / xcancel.com）在 2026-06-30 都被 Cloudflare Turnstile 擋下來，無法用 nitter 撈。

**替代方案（不需登入、不需 captcha）**：

```bash
# fxtwitter — Twitter profile JSON
curl -s "https://api.fxtwitter.com/<username>" | python3 -c "
import sys, json
d = json.load(sys.stdin)
user = d.get('user', {})
print(f\"name: {user.get('name')}\")
print(f\"created: {user.get('joined')}\")
print(f\"followers/following: {user.get('followers')}/{user.get('following')}\")
print(f\"tweets: {user.get('tweets')}, likes: {user.get('likes')}\")
print(f\"description: {user.get('description')}\")
"

# vxtwitter — sometimes returns full tweet thread
curl -s "https://api.vxtwitter.com/<username>"

# Twitter oEmbed API — exists check (returns 404 if account doesn't exist)
curl -s "https://publish.twitter.com/oembed?url=https://twitter.com/<username>"
```

### E. Google Scholar `author:"<Name>"`

```bash
UA="Mozilla/5.0 ..."
# 注意：要帶 cookies 才能看到完整 profile，curl 通常只給 10 筆
curl -sL --max-time 30 -A "$UA" "https://scholar.google.com/scholar?q=author%3A%22Chi-Chuan+Wang%22&hl=en"
```

---

## Step 3 — Cross-validation matrix

當多個護照拼音變體都回傳「同一個機構 + 同一個 ORCID」時，信心升到 high。

| 信號強度 | 條件 |
|:---|:---|
| 🟢 高 | ORCID 直接列出「other-name: <中文名相符字>」 + 任職台灣機構 + 學術發表 |
| 🟢 高 | 多個護照變體在 Yahoo TW 都命中同一 LinkedIn / Scholar profile |
| 🟡 中 | ORCID 顯示此人但「other-name」與目標中文名**字不完全相符**（如 王繼娟 vs 王池川）— 可能是同音字 / 異體字，需手動確認 |
| 🟡 中 | 只有 TradingView / Spotify / BeReal / Twitter 等娛樂 / 社交帳號命中 — 無學術 / 職業驗證 |
| 🟡 中 | Google Scholar 有「Wang Chi-Chuan」相關 paper 但 ORCID 缺 — 可能不是同一人 |
| 🔴 低 | 只有 username scanner 命中（kik / telegram / mixcloud 等假陽性平台）— 不可作為證據 |

---

## Step 4 — Disambiguation：同拼音不同人

最常見的 false positive（王池川 2026-06-30 親身撞到）：

| 同拼音姓名 | 機構 | 識別依據 |
|:---|:---|:---|
| 王啟川 (Wang Chi-Chuan) | 國立陽明交通大學 機械系 | 講座教授，ORCID 0000-0002-4451-3401，h-index 74 |
| 王繼娟 (Wang Chi-Chuan) | 國立臺灣大學 藥學系 | 副教授，ORCID 0000-0002-4597-4859，h-index 24 |
| 王继娟 (簡體) | 同上 | 同一人的簡繁差異 |
| 王义川 (TikTok hashtag) | 民進黨政治人物王義川 | 拼音完全相同，但是「王**義**川」不是「池川」 |

**Disambiguation 步驟**：
1. 看 Yahoo TW 命中的 LinkedIn / Scholar 頁面頭像與自介
2. ORCID 的 `other-names.other-name.content` 是中文姓名的權威來源
3. 主題 tags（`x_concepts`）：如果是藥學/health economics → 是王繼娟；如果是 heat transfer → 是王啟川
4. 地理位置：NYCU 在新竹，NTU 在台北

---

## Output template — 護照拼音 OSINT

```markdown
# 「<中文名>」護照拼音 OSINT 報告

## 護照拼音變體（已查過）
1. WANG CHI-CHUAN (漢語)
2. WANG CHIH-CHUAN (威妥瑪)
3. WANG CHR-CHUAN (國音第二)
4. WANG CHI-CHWAN (耶魯)
5. WANG CHIH-CHWAN (混合)

## 候選身分（依信心排序）

### 候選 1：<找到的人> (信心：高)
- ORCID: ...
- 任職: ...
- other-names: <中文名>
- 證據鏈: ORCID + Scholar + Yahoo TW + LinkedIn

### 候選 2：<另一個人> (信心：中 - fuzzy)
- ORCID: ...
- 中文名: ... (與目標差 N 個字)
- 是否為同一人: <說明>

## 社交帳號命中（幽靈帳號）
- TradingView: ...
- Twitter: ... (顯示名=...)
- BeReal: ...

## 結論
- 「<中文名>」真實存在為「<同拼音姓名>」的機率: 高/中/低
- 此人學術/職業身份: ...
- 與「王啟川」(fuzzy) 是否同人: 否/待確認

## 後續建議
- 提供更多線索：縣市、年齡、學校、職業
- 用「其他拼字」變體（王馳川、王持川、王迟川）再查
```

---

## Hard lessons

### L1. Nitter 在 2026 已死

不要再浪費時間試 `nitter.net`、`nitter.cz`、`nitter.privacydev.net`、
`nitter.poast.org`、`xcancel.com` — 全都被 Cloudflare Turnstile / DDoS-Guard
擋。**改用 fxtwitter / vxtwitter / xcancel API endpoints**，這些仍活著。

### L2. fxtwitter 不顯示 following / likes

`https://api.fxtwitter.com/<user>/following` 和 `/likes` 都回 404。
只能拿 user profile JSON（name、followers、created_at、description），
看不到 following list 和 liked tweets。要看 following 得用：
- Playwright 登入 Twitter（**違反 OSINT 原則**，不建議）
- 直接看 follower / following count 推測活躍度

### L3. OpenAlex 的 display_name 不一定等於護照拼音

OpenAlex 裡 `Wang Chi-Chuan` 可能 normalized 成 `Chi‐Chuan Wang` 或
`C.C. Wang` — 排序時要查所有變體。

### L4. ORCID 的 other-names 是中文姓名的權威來源

拿到 ORCID 後第一件事就是 dump `person.other-names.other-name[*].content`，
這直接告訴你此人的**官方中文姓名**。如果「other-name: 王繼娟」跟用戶說
的「王池川」對不上 → 兩種可能：
- (a) 用戶口誤 / 簡繁混用 / 異體字
- (b) 這人不是用戶要找的人 — 繼續找下一個 ORCID

### L5. Yahoo TW 對護照拼音搜尋沒有 noise trap

跟中文姓名不同，護照拼音（`"Chi-Chuan Wang"`）在 Yahoo TW 上是正常搜尋，
**沒有** phonetic substitution 或 OR-stripped 行為。直接 grep h3 title 就好。

### L6. Scholar 用 curl 看 profile 只能看到 10 筆

`scholar.google.com/citations?user=...` 完整 profile 需要 cookies。
curl 通常只給前 10 筆論文。要看全部 → 用 OpenAlex 替代。