<p align="center">
  <img src="security-agent-skills.png" alt="security-agent-skills" width="100%">
</p>

<h1 align="center">security-agent-skills</h1>

<h3 align="center">網路安全技能路由器 · Cybersecurity Skills Router</h3>

<p align="center"><em>79 個技能 · 9 個領域 · 8 個代理 — 基於真實案例，而非理論。</em></p>

<p align="center">
  <a href="https://github.com/Wang200935/security-agent-skills/releases"><img src="https://img.shields.io/badge/release-v2.0.0-blue" alt="release"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/stargazers"><img src="https://img.shields.io/github/stars/Wang200935/security-agent-skills?style=flat&logo=github" alt="stars"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/forks"><img src="https://img.shields.io/github/forks/Wang200935/security-agent-skills?style=flat&logo=github" alt="forks"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/issues"><img src="https://img.shields.io/github/issues/Wang200935/security-agent-skills?style=flat&logo=github" alt="issues"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributions-welcome-orange" alt="contributing"></a>
</p>

<p align="center">
  <a href="#about">關於</a> ·
  <a href="#getting-started">快速上手</a> ·
  <a href="#skill-categories">技能分類</a> ·
  <a href="#usage">使用方式</a> ·
  <a href="#compatibility">相容性</a> ·
  <a href="#contributing">貢獻</a>
</p>

<p align="center">
  🌐
  <a href="README.md">English</a> ·
  <a href="README_zh_CN.md">简体中文</a> ·
  <a href="README_ja.md">日本語</a>
</p>

---

## 關於

當 AI 代理（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、GitHub Copilot、OpenClaw 或 Hermes Agent）遇到安全相關任務時——需要反編譯 APK、滲透測試 Web 應用、解決 CTF 挑戰或分析二進制文件——此技能包會將其路由到正確的方法論、payload 和命令，而非盲目猜測。

```
使用者任務 → security-orchestrator (主路由器 · 意圖分析)
         → 激活專門技能 (方法論 + payload + 命令)
         → 執行 + 證據收集
         → 報告生成
```

**為何需要此專案：**

- AI 代理不知道針對特定任務應使用 nmap、sqlmap、Burp Suite 還是 Ghidra
- Web、網路、二進制、CTF 和硬體任務各自需要不同的作戰手冊
- 相同的錯誤會反覆發生，因為經驗未被重複使用
- Payload、工具參考和方法論分散在書籤和筆記中

主路由器：[`skills/security-orchestrator/SKILL.md`](skills/security-orchestrator/SKILL.md)

### 目前狀態

| 指標 | 數值 |
|:-------|------:|
| 總技能數 | 79 |
| 領域數 | 9 |
| 主路由器 | 1 (security-orchestrator) |
| 支援代理 | 8 |
| 參考文件 | 214+ |
| 整合倉庫 | 479+ |
| 技能格式 | SKILL.md (Agent Skills 開放標準) |

---

## 快速上手

### 先決條件

- 支援的 AI 程式碼代理（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、Copilot、OpenClaw 或 Hermes）
- `bash` 環境用於安裝腳本
- 部分技能需要參考 nmap、sqlmap、Ghidra、IDA、Frida 等工具

### 安裝

```bash
git clone https://github.com/Wang200935/security-agent-skills.git
cd security-agent-skills

# 為你的代理安裝
./install.sh --agent claude-code

# 或為所有檢測到的代理安裝
./install.sh --all

# 列出可用技能
./install.sh --list
```

| 代理 | 旗標 |
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

## 技能分類

<!-- BEGIN INVENTORY -->
### 🔍 Recon & OSINT (12 個技能)
`chatgpt-web-relay` · `darkweb-research` · `email-osint-investigation` · `local-network-recon` · `network-device-recon` · `osint-framework` · `osint-recon-model` · `parallel-intel-gathering` · `reconnaissance-ops` · `spiderfoot-automation` · `username-scanner` · `vulnerability-discovery`

### 🌐 Web Pentest (13 個技能)
`android-pentest` · `api-security-testing` · `browser-automation-security` · `client-auth-bypass` · `client-reverse-engineering` · `ctf-web-attacks` · `ctf-web-pwn-methodology` · `framework-vulnerability-research` · `sql-server-exploitation` · `waf-bypass-techniques` · `web-app-assessment` · `web-app-pentest` · `web-security-advanced`

### 🖥️ Network Pentest (6 個技能)
`advanced-pentest` · `network-pentest` · `pentest-quick-checklist` · `pentest-tool-reference` · `pentest-tool-setup` · `pentest-workflow`

### 💥 Exploit Development (10 個技能)
`binary-exploitation` · `crypto-attack-patterns` · `crypto-ctf-attacks` · `crypto-toolkit` · `cryptography-fundamentals` · `encoding-realignment` · `exploit-development` · `exploit-poc-builder` · `kernel-exploitation` · `zero-day-hunting`

### 🔧 Reverse Engineering (3 個技能)
`ctf-reverse-engineering` · `digital-forensics` · `reverse-engineering`

### 🚩 CTF (10 個技能)
`ctf-jail-escape` · `ctf-kernel-exploitation` · `ctf-misc-toolkit` · `ctf-orchestrator` · `ctf-playbook` · `ctf-technique-atlas` · `ctf-training-loop` · `ctf-web-exploitation` · `ctf-writeup-discipline` · `ctf-writeup-screenshots`

### 🎯 Post-Exploitation (6 個技能)
`advanced-attack-chains` · `autonomous-pentest-scanner` · `intranet-pentest-advanced` · `pentest-report-generator` · `post-exploitation-ops` · `professional-pentest-guide`

### ☁️ Cloud & AI Security (6 個技能)
`ai-mcp-security` · `modern-attack-surfaces` · `offensive-toolkit` · `security-and-hardening` · `security-audit` · `security-code-review`

### 🔌 Hardware & IoT (12 個技能)
`bluetooth-jammer-sweep` · `esp32-serial-diag` · `flipper-zero-backup` · `flipper-zero-firmware` · `hardware-iot-hacking` · `nrf24-bitbang-spi` · `rf-jammer-firmware-port` · `rf-multi-protocol-jammer` · `smart-card-driver-debug` · `smart-card-usb-direct` · `wifi-deauth-jammer` · `wifi-dualband-jammer`

### 🧭 Orchestrator (1 個技能)
`security-orchestrator`

**Total: 79 skills** (+ 1 orchestrator)
<!-- END INVENTORY -->


## 使用方式

### 協調器

`security-orchestrator` 是主路由器。當使用者詢問任何安全相關任務時，它會：
1. 分析意圖
2. 路由到正確的專門技能
3. 可觸發並行技能載入以提高速度

### 路由邏輯

```
"掃描此目標"         → recon + web-app-pentest
"利用此漏洞"         → exploit-development
"反編譯此二進制"      → reverse-engineering
"CTF 挑戰"            → ctf (ctf-orchestrator 進一步路由)
"枚舉網路"            → network-pentest
"對人/域名進行 OSINT"   → recon (osint-framework)
"繞過 WAF"            → web-advanced-pentest (waf-bypass-techniques)
"權限提升"            → post-exploitation
"審計此程式碼"         → cloud-security (security-audit)
"入侵 IoT 裝置"       → hardware-iot
"AI 安全 / MCP"       → cloud-security (ai-mcp-security)
"模糊測試此目標"       → exploit-dev (zero-day-hunting)
"破解此雜湊"          → exploit-dev (cryptography-fundamentals)
"滲透測試報告"        → post-exploitation (pentest-report-generator)
```

### 平行執行

為達到最大速度，可並行載入多個技能：
- **完整滲透測試**：recon + web-app-pentest + network-pentest + post-exploitation
- **漏洞賞金**：recon + web-app-pentest + exploit-dev + waf-bypass-techniques
- **CTF 解題**：ctf-orchestrator → 根據需要路由到 ctf-web / ctf-crypto / ctf-misc-toolkit / ctf-reverse
- **內部滲透測試**：network-pentest + post-exploitation + intranet-pentest-advanced
- **硬體評估**：hardware-iot-hacking + reverse-engineering

### 選擇性安裝

```bash
# 只安裝特定領域
./install.sh --agent claude-code --domains web-advanced-pentest,exploit-dev

# 只安裝 CTF 技能
./install.sh --agent claude-code --domains ctf

# 只安裝協調器
./install.sh --agent claude-code --skills security-orchestrator
```

### 技能結構

每個技能都遵循 [Agent Skills 開放標準](https://agentskills.io)：

```
skills/
├── security-orchestrator/          # 主路由器
│   └── SKILL.md
├── recon/
│   ├── osint-framework/
│   │   ├── SKILL.md                # 指令 + YAML 前置資料
│   │   ├── references/             # 深度知識文件
│   │   └── scripts/                # 輔助自動化
│   └── ...
└── ...
```

### 規則庫

`rules/` 目錄中的共享知識會在各技能中載入：

| 檔案 | 內容 |
|:-----|:---------|
| `rules/security-rules.md` | Payload (XSS/SSRF/SQLi/SSTI)、WAF 繞過階梯、狩獵規則、前 10 大錯誤 |

### 供應商配置

`providers/` 目錄中包含每個代理的預配置指令文件：

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

## 相容性

| 代理 | 安裝位置 |
|:------|:-----------------|
| Claude Code | `.claude/skills/` 或 `~/.claude/skills/` |
| Codex | `.codex/skills/` 或 `AGENTS.md` |
| Cursor | `.cursor/skills/` 或 `.cursorrules` |
| Gemini CLI | `.gemini/skills/` |
| Windsurf | `.windsurf/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenClaw | `.agents/skills/` |
| Hermes Agent | `~/.hermes/skills/` |

---

## 貢獻

歡迎提交 PR。新技能必須包含：
1. 帶有必需 YAML 前置資料（`name`、`description`）的 `SKILL.md`
2. 至少一個 `references/` 檔案，包含真實知識（非 AI 生成）
3. 在 `description` 欄位中包含觸發條件
4. 在提交前至少在一個代理中測試

詳細請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 授權

[MIT](LICENSE) — 僅用於授權的安全測試。請遵循負責任披露原則。

---

> 🌐 [English](README.md) · [简体中文](README_zh_CN.md) · [日本語](README_ja.md)
