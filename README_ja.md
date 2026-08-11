<p align="center">
  <img src="security-agent-skills.png" alt="security-agent-skills" width="100%">
</p>

<h1 align="center">security-agent-skills</h1>

<h3 align="center">サイバーセキュリティ技能ルーター · 資安技能ルーティングパック</h3>

<p align="center"><em>79 skills · 9 domains · 8 agents — 実戦で鍛えた知見をもとに構築。理論だけではありません。</em></p>

<p align="center">
  <a href="https://github.com/Wang200935/security-agent-skills/releases"><img src="https://img.shields.io/badge/release-v2.0.0-blue" alt="リリース"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/stargazers"><img src="https://img.shields.io/github/stars/Wang200935/security-agent-skills?style=flat&logo=github" alt="スター"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/forks"><img src="https://img.shields.io/github/forks/Wang200935/security-agent-skills?style=flat&logo=github" alt="フォーク"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/issues"><img src="https://img.shields.io/github/issues/Wang200935/security-agent-skills?style=flat&logo=github" alt="イシュー"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="ライセンス"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributions-welcome-orange" alt="コントリビューション歓迎"></a>
</p>

<p align="center">
  <a href="#about">概要</a> ·
  <a href="#getting-started">はじめに</a> ·
  <a href="#skill-categories">カテゴリ</a> ·
  <a href="#usage">使い方</a> ·
  <a href="#compatibility">互換性</a> ·
  <a href="#contributing">貢献</a>
</p>

<p align="center">
  🌐
  <a href="README.md">English</a> ·
  <a href="README_zh.md">繁體中文</a> ·
  <a href="README_zh_CN.md">简体中文</a>
</p>

---

<a id="about"></a>
## 概要

AI エージェント（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、GitHub Copilot、OpenClaw、Hermes Agent など）が、APK の逆解析、Web アプリのペネトレーションテスト、CTF の解答、バイナリ解析といったセキュリティ課題に遭遇したとき、このパックは推測に頼らず、適切な手法・ペイロード・コマンドへ振り分けます。

```
User task → security-orchestrator (master router · intent analysis)
         → specialized skill activated (methodology + payloads + commands)
         → execution + evidence collection
         → reporting
```

**存在理由:**

- AI エージェントは、与えられた課題に対して nmap、sqlmap、Burp Suite、Ghidra のどれを使うべきか判断できないことがある
- Web、ネットワーク、バイナリ、CTF、ハードウェアの各課題には、それぞれ異なるプレイブックが必要
- 経験が再利用されないため、同じミスが繰り返される
- ペイロード、ツール参照、手法がブックマークやメモに散在している

メインルーター: [`skills/security-orchestrator/SKILL.md`](skills/security-orchestrator/SKILL.md)

### 現在の状況

| 指標 | 値 |
|:-----|---:|
| 総 skill 数 | 79 |
| ドメイン数 | 9 |
| メインルーター | 1 (security-orchestrator) |
| 対応エージェント数 | 8 |
| 参照ファイル数 | 214+ |
| 統合済みリポジトリ数 | 479+ |
| skill 形式 | SKILL.md (Agent Skills open standard) |

---

<a id="getting-started"></a>
## はじめに

### 前提条件

- 対応済みの AI コーディングエージェント（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、Copilot、OpenClaw、Hermes のいずれか）
- インストールスクリプト用の `bash`
- 一部の skill は nmap、sqlmap、Ghidra、IDA、Frida などのツールを参照します

### インストール

```bash
git clone https://github.com/Wang200935/security-agent-skills.git
cd security-agent-skills

# 使用するエージェント向けにインストール
./install.sh --agent claude-code

# もしくは検出された全エージェント向けにインストール
./install.sh --all

# 利用可能な skill を一覧表示
./install.sh --list
```

| エージェント | フラグ |
|:------|:-----|
| Claude Code | `--agent claude-code` |
| Codex / OpenAI | `--agent codex` |
| Cursor IDE | `--agent cursor` |
| Gemini CLI | `--agent gemini-cli` |
| Windsurf | `--agent windsurf` |
| GitHub Copilot | `--agent github-copilot` |
| OpenClaw | `--agent openclaw` |
| Hermes Agent | `--agent hermes-agent` |

---

<a id="skill-categories"></a>
## 技能カテゴリ

### 🔍 偵察・OSINT (12 skills)
`osint-framework` · `username-scanner` · `email-osint-investigation` · `spiderfoot-automation` · `parallel-intel-gathering` · `osint-recon-model` · `reconnaissance-ops` · `darkweb-research` · `vulnerability-discovery` · `chatgpt-web-relay` · `local-network-recon` · `network-device-recon`

### 🌐 Web ペネトレーションテスト (14 skills)
`web-app-pentest` · `api-security-testing` · `client-auth-bypass` · `web-app-assessment` · `web-security-advanced` · `waf-bypass-techniques` · `ctf-web-attacks` · `ctf-web-pwn-methodology` · `framework-vulnerability-research` · `sql-server-exploitation` · `client-reverse-engineering` · `android-pentest` · `browser-automation-security`

### 🖥️ ネットワーク・ペネトレーションテスト (6 skills)
`network-pentest` · `advanced-pentest` · `pentest-tool-setup` · `pentest-workflow` · `pentest-tool-reference` · `pentest-quick-checklist`

### 💥 エクスプロイト開発 (10 skills)
`exploit-development` · `zero-day-hunting` · `kernel-exploitation` · `exploit-poc-builder` · `crypto-toolkit` · `crypto-ctf-attacks` · `cryptography-fundamentals` · `crypto-attack-patterns` · `encoding-realignment` · `binary-exploitation`

### 🔧 リバースエンジニアリング (3 skills)
`reverse-engineering` · `ctf-reverse-engineering` · `digital-forensics`

### 🚩 CTF (12 skills)
`ctf-playbook` · `ctf-orchestrator` · `ctf-misc-toolkit` · `ctf-technique-atlas` · `ctf-training-loop` · `ctf-web-exploitation` · `ctf-writeup-discipline` · `ctf-writeup-screenshots` · `ctf-kernel-exploitation` · `ctf-jail-escape`

### 🎯 ポストエクスプロイト (6 skills)
`post-exploitation-ops` · `intranet-pentest-advanced` · `advanced-attack-chains` · `professional-pentest-guide` · `autonomous-pentest-scanner` · `pentest-report-generator`

### ☁️ クラウド・AI セキュリティ (7 skills)
`ai-ml-security-assessment` · `ai-mcp-security` · `modern-attack-surfaces` · `security-and-hardening` · `security-code-review` · `security-audit` · `offensive-toolkit`

### 🔌 ハードウェア・IoT (12 skills)
`hardware-iot-hacking` · `bluetooth-jammer-sweep` · `wifi-deauth-jammer` · `nrf24-bitbang-spi` · `rf-multi-protocol-jammer` · `wifi-dualband-jammer` · `esp32-serial-diag` · `flipper-zero-backup` · `flipper-zero-firmware` · `rf-jammer-firmware-port` · `smart-card-driver-debug` · `smart-card-usb-direct`

---

<a id="usage"></a>
## 使い方

### オーケストレーター

`security-orchestrator` はメインルーターです。ユーザーが何らかのセキュリティ課題について尋ねると、次の処理を行います。
1. 意図を解析する
2. 適切な専用 skill に振り分ける
3. 速度向上のために複数 skill の並列読み込みを起動できる

### ルーティングロジック

```
"scan this target"         → recon + web-app-pentest
"exploit this bug"         → exploit-development
"reverse this binary"      → reverse-engineering
"CTF challenge"            → ctf (ctf-orchestrator routes further)
"enumerate network"        → network-pentest
"OSINT on person/domain"   → recon (osint-framework)
"bypass WAF"              → web-advanced-pentest (waf-bypass-techniques)
"privilege escalation"     → post-exploitation
"audit this code"          → cloud-security (security-audit)
"hack IoT device"          → hardware-iot
"AI security / MCP"        → cloud-security (ai-mcp-security)
"fuzz this target"         → exploit-dev (zero-day-hunting)
"crack this hash"          → exploit-dev (cryptography-fundamentals)
"advanced-pentest report"           → post-exploitation (pentest-report-generator)
```

### 並列実行

最大速度を出すには、複数の skill を並列で読み込みます。
- **フルペネトレーションテスト**: recon + web-app-pentest + network-pentest + post-exploitation
- **バグバウンティ**: recon + web-app-pentest + exploit-dev + waf-bypass-techniques
- **CTF 解答**: ctf-orchestrator → 必要に応じて ctf-web / ctf-crypto / ctf-misc-toolkit / ctf-reverse に振り分け
- **社内ペネトレーションテスト**: network-pentest + post-exploitation + intranet-pentest-advanced
- **ハードウェア評価**: hardware-iot-hacking + reverse-engineering

### 選択的インストール

```bash
# 特定のドメインだけをインストール
./install.sh --agent claude-code --domains web-advanced-pentest,exploit-dev

# CTF skill だけをインストール
./install.sh --agent claude-code --domains ctf

# オーケストレーターだけをインストール
./install.sh --agent claude-code --skills security-orchestrator
```

### Skill 構成

すべての skill は [Agent Skills open standard](https://agentskills.io) に従います。

```
skills/
├── security-orchestrator/          # メインルーター
│   └── SKILL.md
├── recon/
│   ├── osint-framework/
│   │   ├── SKILL.md                # 指示 + YAML frontmatter
│   │   ├── references/             # 深い知識をまとめたファイル
│   │   └── scripts/                # 補助自動化
│   └── ...
└── ...
```

### ルールライブラリ

`rules/` 内の共通知識は、各 skill から読み込まれます。

| ファイル | 内容 |
|:-----|:---------|
| `rules/security-rules.md` | ペイロード（XSS/SSRF/SQLi/SSTI）、WAF 回避の段階的手順、ハンティング規則、主要なミス 10 項目 |

### プロバイダ設定

各エージェント向けに、`providers/` にあらかじめ設定済みの指示ファイルがあります。

```
providers/
├── claude-code/CLAUDE.md
├── codex/AGENTS.md
├── cursor/.cursorrules
├── gemini/GEMINI.md
├── hermes/AGENTS.md
└── openclaw/AGENTS.md
```

---

<a id="compatibility"></a>
## 互換性

| エージェント | インストール先 |
|:------|:-----------------|
| Claude Code | `.claude/skills/` または `~/.claude/skills/` |
| Codex | `.codex/skills/` または `AGENTS.md` |
| Cursor | `.cursor/skills/` または `.cursorrules` |
| Gemini CLI | `.gemini/skills/` |
| Windsurf | `.windsurf/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenClaw | `.agents/skills/` |
| Hermes Agent | `~/.hermes/skills/` |

---

<a id="contributing"></a>
## 貢献

PR は歓迎します。新しい skill には、次の要件が必要です。
1. 必須 YAML frontmatter（`name`、`description`）を含む `SKILL.md`
2. 実際の知識を含む `references/` ファイルを最低 1 つ追加すること（AI 生成のみは不可）
3. `description` フィールドにトリガー条件を記載すること
4. 送信前に少なくとも 1 つのエージェントでテストすること

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

---

## ライセンス

[MIT](LICENSE) — 許可されたセキュリティテストにのみ使用してください。責任ある開示に従ってください。

---

> 🌐 [English](README.md) · [繁體中文](README_zh.md) · [简体中文](README_zh_CN.md)
