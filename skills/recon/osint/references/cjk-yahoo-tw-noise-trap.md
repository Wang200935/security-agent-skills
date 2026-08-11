# Yahoo TW 搜尋結果「假命中」陷阱（cold CJK name noise trap）

> **Use case**: 你的 query 是罕見/冷僻的中文姓名（學術網路上沒有真實個體），但 Yahoo TW 卻回「約 10,000 項」甚至「約 233,000 項」結果。本 reference 解釋這是怎麼發生的，以及怎麼驗證「這是 noise 不是真命中」。

> **驗證 session**：王池川 2026-06-30（Taiwan person OSINT 完整任務）。

## 兩個主要陷阱

### 陷阱 1：Phonetic / Semantic 自動替換

當 query 的中文姓名在 Yahoo TW 索引裡「零命中」時，Yahoo 不會直接給你「沒有結果」頁 — 它會**自動做字面相似替換**（類似 Google 的「您是不是要查：...」）並把替代結果呈現給你看。

**真實例子**（王池川，2026-06-30）：
```
Query:     王池川
Yahoo 回:  約 10,000 項 搜尋結果包含：王治川
實際結果:  全部都是「王義川」（台灣政治評論家）
          - zh.wikipedia.org/wiki/王義川
          - news.ltn.com.tw 王義川桃園水情
          - udn.com 王義川的反指標
          - chinatimes.com 王義川回應了
```

**為什麼危險**：10,000 是一個看起來很可觀的數字，會讓人以為「這個人公開足跡超多」。但其實全部是 noise — 真正有沒有「王池川」這個體，答案是 0。

### 陷阱 2：`OR` 運算元被吃掉

Yahoo TW 不支援（或悄悄不處理）Google-style 的 `OR` 運算元。當 query 裡含 `OR` 時，Yahoo 不會把它當布林運算，而是把它當字面字串處理、甚至**直接忽略**，query 就退化為「Chinese-name + 後面的第一個中文 token」。

**真實例子**（王池川，2026-06-30）：
```
Query:     王池川 老師 OR 教授
Yahoo 回:  約 233,000 項
實際結果:  query 退回成「王」單字
          - 教育部《重編國語辭典》「王」字
          - 百度百科「王（漢語文字）」
          - 維基百科「王姓」
          - 漢堡王burgerking.com.tw
          - 教育部異體字字典

Query:     王池川 醫師 OR 工程師 OR 律師
Yahoo 回:  約 233,000 項
實際結果:  與上面完全相同（10 筆全是「王」單字結果）
```

**為什麼危險**：233,000 看起來更可觀。但 query 已經退化成單字「王」，所以這其實是「Yahoo 對『王』這個字的全部索引」。**和目標人完全無關**。

---

## 驗證「這是 noise」的三步驟

當 Yahoo TW 對一個冷僻姓名回報「10,000+ 命中」時，照這個順序檢查：

### Step 1：抓第一頁所有 `<h3 class="title"><a>` 標題

```python
import re, html as h
from urllib.parse import unquote

raw = open("tor_yahoo_tw.html", encoding="utf-8").read()
blocks = re.findall(
    r'<h3[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
    raw, flags=re.DOTALL|re.IGNORECASE
)

for href, title in blocks[:10]:
    title_text = re.sub(r"<[^>]+>", "", title)
    title_text = h.unescape(re.sub(r"\s+", " ", title_text)).strip()
    real = re.search(r"/RU=([^/]+)/", href)
    real_url = unquote(real.group(1)) if real else href
    print(f"  {title_text[:60]}")
    print(f"    -> {real_url[:100]}")
```

### Step 2：在可見文字裡 grep 完整姓名

```python
text = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.DOTALL)
text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text)

target = "王池川"
print(f"'{target}' 在可見文字出現次數: {text.count(target)}")
```

**判定**：
- 若 `count >= 2` 且第 1 個命中出現在 result block（不是 search bar）：可能是真命中，要繼續挖。
- 若 `count == 1` 且只在 search input 附近：Yahoo 自動替換了，這是 noise。
- 若 `count == 0`：完全沒命中。

### Step 3：交叉比對「搜尋結果包含」提示

```python
hint = re.search(r"搜尋結果包含[：:]\s*([^<\"]+?)(?=[\"<])", raw)
if hint:
    print(f"Did-you-mean: {hint.group(1).strip()}")
```

如果 Yahoo 顯示「搜尋結果包含：XXX」，那 XXX 一定**不是**你查的姓名，這就是自動替換的鐵證。

---

## 完整 noise-trap 判定流程圖

```
Yahoo TW 回「10,000+ 命中」
       │
       ▼
[1] grep 完整姓名於可見文字
       │
       ├── count >= 2 在 result block  → 真命中，繼續 Step 2 分析
       │
       ├── count == 1 只在 search bar  → 自動替換（陷阱 1）
       │                                → 結論：Yahoo 認為這是 cold name
       │
       └── count == 0                  → 完全沒命中
                                           → 結論：沒有任何公開足跡

[2] 檢查首頁 h3 title links
       │
       ├── 所有標題都沒有 query 姓名    → 確認是 noise
       │   → 比對 Yahoo did-you-mean 提示
       │   → 列出 Yahoo 認為「相近」的姓名並標記
       │
       └── 至少 1 個標題含 query 姓名   → 真命中，逐條抓 URL 解析
```

---

## 已驗證的 Yahoo TW「搜尋結果包含：」自動替換範例

| Query | Yahoo 提示「包含」 | 實際結果 | 噪音程度 |
|---|---|---|---|
| `王池川` | `王治川` | 7 筆全是 `王義川`（台灣政治人物） | 100% noise |
| `王池川 老師 OR 教授` | （無提示但 query 退回成 `王`） | 10 筆全是「王」單字 | 100% noise |
| `王池川 醫師 OR 工程師 OR 律師` | （同上） | 同上 | 100% noise |

---

## 何時 Yahoo TW noise trap 不會發生

- Query 是**常見姓名**（如 `王小明`、`陳大文`）：Yahoo 直接給真實命中，不會觸發替換。
- Query 有明確限定（`"王池川" site:ntu.edu.tw` 或 `inurl:wang`）：Yahoo 較難做替換，因為 site: / inurl: 限制了候選範圍。
- Query 是**英文姓名**（如 `"John Wang"`）：替換演算法是 CJK 專屬。

---

## 配套的診斷腳本

可在 `scripts/` 目錄放這個 5 行的 noise detector，未來任何 Yahoo TW 結果跑一次：

```python
import re, sys
raw = open(sys.argv[1], encoding="utf-8").read()
target = sys.argv[2]
text = re.sub(r"<[^>]+>", " ", raw)
text = re.sub(r"\s+", " ", text)
titles = re.findall(r'<h3[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]+>(.*?)</a>', raw, flags=re.DOTALL|re.IGNORECASE)
hit_titles = [t for t in titles if target in re.sub(r"<[^>]+>", "", t)]
hint = re.search(r"搜尋結果包含[：:]\s*([^<\"]+)", raw)
print(f"query '{target}': {text.count(target)} in text, {len(hit_titles)}/{len(titles)} titles contain it")
print(f"  hint: {hint.group(1).strip() if hint else 'none'}")
if len(titles) > 0 and len(hit_titles) == 0 and hint:
    print("  >>> NOISE TRAP DETECTED: query was auto-substituted")
```

---

## 給上層的「如何陳述這個情況」範本

> 「Yahoo TW 報告「約 10,000 項」結果，但實際首頁 7 筆結果全部都是「王義川」，且 Yahoo 在頁面明確顯示「搜尋結果包含：王治川」——這是 Yahoo 對冷僻中文姓名的自動字面相似替換行為。在 `<h3 class="title">` 區塊的可見文字裡搜尋完整姓名「王池川」出現次數為 0（除了 search input）。因此這些「命中」全部為 noise，不計入證據鏈。」

這段陳述同時點出三件事：(a) 表面命中數字很大但其實是 noise，(b) 明確指出 noise 的機制（自動替換），(c) 給出可重現的驗證方法。

---

## 何時這個 reference 該被更新

- 當 Yahoo TW 改變其替換演算法（替換可能會從 phonetic → 改為 semantic 或完全不替換）。
- 當用戶回報「Yahoo 回 0 命中」時：可能 noise trap 已消失，需要換工具。
- 當 task 是英文姓名或常見中文姓名時：本 reference 不適用，忽略。