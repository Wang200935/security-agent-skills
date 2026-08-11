<p align="center">
  <img src="security-agent-skills.png" alt="security-agent-skills" width="100%">
</p>

<h1 align="center">security-agent-skills</h1>

<h3 align="center">安全代理技能路由包 · Cybersecurity Skills Router</h3>

<p align="center"><em>79 个技能 · 9 大领域 · 8 个 AI 代理 — 来自真实攻防，而非纸上谈兵。</em></p>

<p align="center">
  <a href="https://github.com/Wang200935/security-agent-skills/releases"><img src="https://img.shields.io/badge/release-v2.0.0-blue" alt="release"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/stargazers"><img src="https://img.shields.io/github/stars/Wang200935/security-agent-skills?style=flat&logo=github" alt="stars"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/forks"><img src="https://img.shields.io/github/forks/Wang200935/security-agent-skills?style=flat&logo=github" alt="forks"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/issues"><img src="https://img.shields.io/github/issues/Wang200935/security-agent-skills?style=flat&logo=github" alt="issues"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributions-welcome-orange" alt="contributing"></a>
</p>

<p align="center">
  <a href="#关于">关于</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#技能分类">技能分类</a> ·
  <a href="#使用说明">使用说明</a> ·
  <a href="#兼容性">兼容性</a> ·
  <a href="#贡献">贡献</a>
</p>

<p align="center">
  🌐
  <a href="README.md">English</a> ·
  <a href="README_zh.md">繁體中文</a> ·
  <a href="README_ja.md">日本語</a>
</p>

---

## 关于

当 AI 代理（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、GitHub Copilot、OpenClaw 或 Hermes Agent）遇到安全任务——逆向 APK、渗透测试 Web 应用、解 CTF 题目或分析二进制文件时——本套件会自动路由到正确的方法论、攻击载荷和命令，而不是盲目猜测。

```
用户任务 → security-orchestrator（主路由 · 意图分析）
         → 启动对应专业技能（方法论 + 载荷 + 命令）
         → 执行 + 证据收集
         → 报告生成
```

**为什么需要这个项目：**

- AI 代理不知道该用 nmap、sqlmap、Burp Suite 还是 Ghidra 来处理给定任务
- Web、网络、二进制、CTF 和硬件任务各自需要不同的方法论
- 同样的错误反复出现，因为经验没有被复用
- 攻击载荷、工具参考和方法论散落在书签和笔记中

主路由：[`skills/security-orchestrator/SKILL.md`](skills/security-orchestrator/SKILL.md)

### 当前状态

| 指标 | 数值 |
|:-----|-----:|
| 技能总数 | 79 |
| 领域数 | 9 |
| 主路由 | 1（security-orchestrator） |
| 支持的代理 | 8 |
| 参考文件 | 214+ |
| 集成仓库 | 479+ |
| 技能格式 | SKILL.md（Agent Skills 开放标准） |

---

## 快速开始

### 前置依赖

- 一个支持的 AI 编码代理（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、Copilot、OpenClaw 或 Hermes）
- `bash`（用于安装脚本）
- 部分技能引用了 nmap、sqlmap、Ghidra、IDA、Frida 等工具

### 安装

```bash
git clone https://github.com/Wang200935/security-agent-skills.git
cd security-agent-skills

# 为你的代理安装
./install.sh --agent claude-code

# 或安装到所有检测到的代理
./install.sh --all

# 列出所有可用技能
./install.sh --list
```

| 代理 | 参数 |
|:-----|:-----|
| Claude Code | `--agent claude-code` |
| Codex / OpenAI | `--agent codex` |
| Cursor IDE | `--agent cursor` |
| Gemini CLI | `--agent gemini-cli` |
| Windsurf | `--agent windsurf` |
| GitHub Copilot | `--agent github-copilot` |
| OpenClaw | `--agent openclaw` |
| Hermes Agent | `--agent hermes-agent` |

---

## 技能分类

### 🔍 侦察 & OSINT（12 个技能）
`osint-framework` · `username-scanner` · `email-osint-investigation` · `spiderfoot-automation` · `parallel-intel-gathering` · `osint-recon-model` · `reconnaissance-ops` · `darkweb-research` · `vulnerability-discovery` · `chatgpt-web-relay` · `local-network-recon` · `network-device-recon`

### 🌐 Web 渗透测试（14 个技能）
`web-app-pentest` · `api-security-testing` · `client-auth-bypass` · `web-app-assessment` · `web-security-advanced` · `waf-bypass-techniques` · `ctf-web-attacks` · `ctf-web-pwn-methodology` · `framework-vulnerability-research` · `sql-server-exploitation` · `client-reverse-engineering` · `android-pentest` · `browser-automation-security`

### 🖥️ 网络渗透测试（6 个技能）
`network-pentest` · `advanced-pentest` · `pentest-tool-setup` · `pentest-workflow` · `pentest-tool-reference` · `pentest-quick-checklist`

### 💥 漏洞开发（10 个技能）
`exploit-development` · `zero-day-hunting` · `kernel-exploitation` · `exploit-poc-builder` · `crypto-toolkit` · `crypto-ctf-attacks` · `cryptography-fundamentals` · `crypto-attack-patterns` · `encoding-realignment` · `binary-exploitation`

### 🔧 逆向工程（3 个技能）
`reverse-engineering` · `ctf-reverse-engineering` · `digital-forensics`

### 🚩 CTF（12 个技能）
`ctf-playbook` · `ctf-orchestrator` · `ctf-misc-toolkit` · `ctf-technique-atlas` · `ctf-training-loop` · `ctf-web-exploitation` · `ctf-writeup-discipline` · `ctf-writeup-screenshots` · `ctf-kernel-exploitation` · `ctf-jail-escape`

### 🎯 后渗透（6 个技能）
`post-exploitation-ops` · `intranet-pentest-advanced` · `advanced-attack-chains` · `professional-pentest-guide` · `autonomous-pentest-scanner` · `pentest-report-generator`

### ☁️ 云 & AI 安全（7 个技能）
`ai-ml-security-assessment` · `ai-mcp-security` · `modern-attack-surfaces` · `security-and-hardening` · `security-code-review` · `security-audit` · `offensive-toolkit`

### 🔌 硬件 & IoT（12 个技能）
`hardware-iot-hacking` · `bluetooth-jammer-sweep` · `wifi-deauth-jammer` · `nrf24-bitbang-spi` · `rf-multi-protocol-jammer` · `wifi-dualband-jammer` · `esp32-serial-diag` · `flipper-zero-backup` · `flipper-zero-firmware` · `rf-jammer-firmware-port` · `smart-card-driver-debug` · `smart-card-usb-direct`

---

## 使用说明

### 路由器

`security-orchestrator` 是主路由。当用户提出任何安全相关问题时，它会：
1. 分析意图
2. 路由到正确的专业技能
3. 可并行加载多个技能以提升速度

### 路由逻辑

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

### 并行执行

为最大化速度，可并行加载多个技能：
- **完整渗透测试**：recon + web-app-pentest + network-pentest + post-exploitation
- **Bug Bounty**：recon + web-app-pentest + exploit-dev + waf-bypass-techniques
- **CTF 解题**：ctf-orchestrator → 按需路由到 ctf-web / ctf-crypto / ctf-misc-toolkit / ctf-reverse
- **内网渗透**：network-pentest + post-exploitation + intranet-pentest-advanced
- **硬件评估**：hardware-iot-hacking + reverse-engineering

### 选择性安装

```bash
# 只安装特定领域
./install.sh --agent claude-code --domains web-advanced-pentest,exploit-dev

# 只安装 CTF 技能
./install.sh --agent claude-code --domains ctf

# 只安装路由器
./install.sh --agent claude-code --skills security-orchestrator
```

### 技能结构

每个技能遵循 [Agent Skills 开放标准](https://agentskills.io)：

```
skills/
├── security-orchestrator/          # 主路由
│   └── SKILL.md
├── recon/
│   ├── osint-framework/
│   │   ├── SKILL.md                # 说明 + YAML frontmatter
│   │   ├── references/             # 深度知识文件
│   │   └── scripts/                # 辅助自动化脚本
│   └── ...
└── ...
```

### 规则库

`rules/` 目录中存放跨技能共享的知识：

| 文件 | 内容 |
|:-----|:-----|
| `rules/security-rules.md` | 攻击载荷（XSS/SSRF/SQLi/SSTI）、WAF 绕过阶梯、漏洞挖掘规则、十大常见错误 |

### 代理配置

`providers/` 目录中为每个代理预配置了指令文件：

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

## 兼容性

| 代理 | 安装位置 |
|:-----|:---------|
| Claude Code | `.claude/skills/` 或 `~/.claude/skills/` |
| Codex | `.codex/skills/` 或 `AGENTS.md` |
| Cursor | `.cursor/skills/` 或 `.cursorrules` |
| Gemini CLI | `.gemini/skills/` |
| Windsurf | `.windsurf/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenClaw | `.agents/skills/` |
| Hermes Agent | `~/.hermes/skills/` |

---

## 贡献

欢迎提交 PR。新技能必须包含：
1. `SKILL.md`，带必需的 YAML frontmatter（`name`、`description`）
2. 至少一个 `references/` 文件，包含真实知识（非 AI 生成）
3. `description` 字段中写明触发条件
4. 提交前至少在一个代理中测试过

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 许可证

[MIT](LICENSE) — 仅用于授权的安全测试。请遵循负责任披露原则。

---

> 🌐 [English](README.md) · [繁體中文](README_zh.md) · [日本語](README_ja.md)
