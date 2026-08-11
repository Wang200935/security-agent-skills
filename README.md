<p align="center">
  <img src="security-agent-skills.png" alt="security-agent-skills" width="100%">
</p>

<h1 align="center">security-agent-skills</h1>

<h3 align="center">Cybersecurity Skills Router · 資安技能路由包 · セキュリティスキルパック</h3>

<p align="center"><em>79 skills · 9 domains · 8 agents — built from real engagements, not theory.</em></p>

<p align="center">
  <a href="https://github.com/Wang200935/security-agent-skills/releases"><img src="https://img.shields.io/badge/release-v2.0.0-blue" alt="release v2.0.0"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/stargazers"><img src="https://img.shields.io/github/stars/Wang200935/security-agent-skills?style=flat&logo=github" alt="stars"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/forks"><img src="https://img.shields.io/github/forks/Wang200935/security-agent-skills?style=flat&logo=github" alt="forks"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/issues"><img src="https://img.shields.io/github/issues/Wang200935/security-agent-skills?style=flat&logo=github" alt="issues"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license MIT"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributions-welcome-orange" alt="contributions welcome"></a>
</p>

<p align="center">
  <a href="#about">About</a> ·
  <a href="#getting-started">Getting Started</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#skill-categories">Categories</a> ·
  <a href="#install">Install</a> ·
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  🌐
  <a href="#english">English</a> ·
  <a href="#繁體中文">繁體中文</a> ·
  <a href="#简体中文">简体中文</a> ·
  <a href="#日本語">日本語</a> ·
  <a href="#한국어">한국어</a> ·
  <a href="#español">Español</a> ·
  <a href="#deutsch">Deutsch</a> ·
  <a href="#français">Français</a> ·
  <a href="#português">Português</a> ·
  <a href="#русский">Русский</a> ·
  <a href="#العربية">العربية</a>
</p>

---

## English

**Security Agent Skills** is a pack of 79 cybersecurity skills for AI coding agents. Covering reconnaissance, web pentest, network pentest, exploit development, reverse engineering, CTF, post-exploitation, cloud/AI security, and hardware/IoT hacking.

When an AI agent (Claude Code, Codex, Cursor, Gemini CLI, Windsurf, GitHub Copilot, OpenClaw, or Hermes Agent) encounters a security task, this pack routes it to the right methodology, payloads, and commands — instead of guessing.

```
User task → security-orchestrator (master router)
         → intent analysis
         → specialized skill(s) activated
         → methodology + payloads + commands
         → execution + reporting
```

**Why this exists:** Most AI agents hallucinate when doing security work — they invent commands that don't exist, suggest patched CVEs as exploitable, and miss entire attack surfaces. This pack solves that by giving the agent real, battle-tested skills built from actual engagements.

| Metric | Value |
|:-------|------:|
| Total skills | 79 |
| Domains | 9 |
| Supported agents | 8 |
| Reference files | 214+ |
| Integrated repos | 479+ |

---

## 繁體中文

**資安代理技能包** — 79 個資安技能，涵蓋偵察/OSINT、網站滲透測試、網路滲透測試、漏洞開發、逆向工程、CTF、後滲透、雲端/AI 安全、硬體/IoT 攻擊。

當 AI 代理（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、GitHub Copilot、OpenClaw、Hermes Agent）遇到資安任務時，這個套件會自動路由到正確的方法論、攻擊載荷和指令——不再用猜的。

**為什麼需要這個：** 大多數 AI 代理做資安工作時會產生幻覺——編造不存在的指令、建議已修補的 CVE 當作可利用、漏掉整個攻擊面。這個套件用從真正 engagements 中建立的實戰技能來解決這個問題。

```
使用者任務 → security-orchestrator（主路由）
           → 意圖分析
           → 啟動對應專業技能
           → 方法論 + 載荷 + 指令
           → 執行 + 報告
```

---

## 简体中文

**安全代理技能包** — 79 个安全技能，覆盖侦察/OSINT、Web 渗透测试、网络渗透测试、漏洞开发、逆向工程、CTF、后渗透、云/AI 安全、硬件/IoT 攻击。

当 AI 代理（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、GitHub Copilot、OpenClaw、Hermes Agent）遇到安全任务时，本套件会自动路由到正确的方法论、攻击载荷和命令——不再猜测。

**为什么需要：** 大多数 AI 代理做安全工作时会产生幻觉——编造不存在的命令、建议已修补的 CVE 视为可利用、遗漏整个攻击面。本套件用从真实 engagements 中构建的实战技能来解决这个问题。

---

## 日本語

**セキュリティエージェントスキルパック** — 79 個のセキュリティスキル。偵察/OSINT、Web ペネトレーション、ネットワークペネトレーション、エクスプロイト開発、リバースエンジニアリング、CTF、ポストエクスプロイト、クラウド/AI セキュリティ、ハードウェア/IoT 攻撃をカバー。

AI エージェント（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、GitHub Copilot、OpenClaw、Hermes Agent）がセキュリティタスクに遭遇した際、正しい手法、ペイロード、コマンドへ自動ルーティングします。

**なぜ必要か：** ほとんどの AI エージェントはセキュリティ作業でハルシネーションを起こします。存在しないコマンドを捏造し、パッチ済み CVE を悪用可能と誤認し、攻撃面全体を見落とします。本パックは実際の engagements から構築された実戦スキルでこの問題を解決します。

---

## 한국어

**보안 에이전트 스킬 팩** — 79개의 보안 스킬. 정찰/OSINT, 웹 침투 테스트, 네트워크 침투 테스트, 익스플로잇 개발, 리버스 엔지니어링, CTF, 포스트 익스플로잇, 클라우드/AI 보안, 하드웨어/IoT 공격을 다룹니다.

AI 에이전트(Claude Code, Codex, Cursor, Gemini CLI, Windsurf, GitHub Copilot, OpenClaw, Hermes Agent)가 보안 작업을 만나면 올바른 방법론, 페이로드, 명령으로 자동 라우팅합니다.

---

## Español

**Paquete de habilidades de seguridad para agentes** — 79 habilidades de ciberseguridad que cubren reconocimiento/OSINT, pruebas de penetración web y de red, desarrollo de exploits, ingeniería inversa, CTF, post-explotación, seguridad en la nube/IA y ataques a hardware/IoT.

---

## Deutsch

**Sicherheits-Agent-Skill-Paket** — 79 Cybersicherheits-Skills für KI-Coding-Agenten. Deckt Reconnaissance/OSINT, Web-/Netzwerk-Penetrationstests, Exploit-Entwicklung, Reverse Engineering, CTF, Post-Exploitation, Cloud-/KI-Sicherheit und Hardware-/IoT-Angriffe ab.

---

## Français

**Pack de compétences de sécurité pour agents** — 79 compétences en cybersécurité couvrant la reconnaissance/OSINT, les tests de pénétration web et réseau, le développement d'exploits, l'ingénierie inverse, les CTF, la post-exploitation, la sécurité cloud/IA et le hacking matériel/IoT.

---

## Português

**Pacote de habilidades de segurança para agentes** — 79 habilidades de segurança cibernética cobrindo reconhecimento/OSINT, testes de penetração web e de rede, desenvolvimento de exploits, engenharia reversa, CTF, pós-exploração, segurança em nuvem/IA e ataques a hardware/IoT.

---

## Русский

**Пакет навыков безопасности для ИИ-агентов** — 79 навыков кибербезопасности: разведка/OSINT, веб- и сетевой пентестинг, разработка эксплойтов, реверс-инжиниринг, CTF, пост-эксплуатация, облачная/ИИ-безопасность и атаки на оборудование/IoT.

---

## العربية

**حزمة مهارات الأمن السيبراني لوكلاء الذكاء الاصطناعي** — 79 مهارة أمنية تغطي الاستطلاع/OSINT، اختبار اختراق الويب والشبكات، تطوير الثغرات، الهندسة العكسية، CTF، ما بعد الاختراق، أمان السحابة/الذكاء الاصطناعي، وهاكندوار الأجهزة/إنترنت الأشياء.

---

## About

When an AI agent encounters a security task — an APK to reverse, a web app to pentest, a CTF challenge to solve, or a binary to analyze — this pack routes it to the right methodology, checks available tools, and executes a repeatable workflow.

```
User task
→ security-orchestrator (master router · intent analysis)
→ specialized skill activated (methodology + payloads + commands)
→ execution + evidence collection
→ reporting
```

### Current status

| Metric | Value |
|:-------|------:|
| Skills | 79 |
| Domains | 9 |
| Master router | 1 (security-orchestrator) |
| Supported agents | 8 |
| Reference files | 214+ |
| Integrated repos | 479+ |
| Skill format | SKILL.md (Agent Skills open standard) |

Primary router: [`skills/security-orchestrator/SKILL.md`](skills/security-orchestrator/SKILL.md)

---

## Getting Started

```bash
git clone https://github.com/Wang200935/security-agent-skills.git
cd security-agent-skills

# Install for your agent
./install.sh --agent claude-code   # Claude Code
./install.sh --agent codex         # Codex / OpenAI
./install.sh --agent cursor        # Cursor IDE
./install.sh --agent gemini-cli    # Gemini CLI
./install.sh --agent windsurf      # Windsurf
./install.sh --agent copilot       # GitHub Copilot
./install.sh --agent openclaw      # OpenClaw
./install.sh --agent hermes        # Hermes Agent

# Or install for all detected agents
./install.sh --all

# List available skills
./install.sh --list
```

---

## Skill Categories

### 🔍 Recon & OSINT (12 skills)
`osint` · `aliens-eye` · `email-osint` · `spiderfoot-osint` · `parallel-intel` · `vulnclaw-osint-recon` · `vulnclaw-recon` · `darkweb-research-env` · `vulnclaw-vuln-discovery` · `chatgpt-web-relay` · `local-network-recon` · `network-device-recon`

### 🌐 Web Pentest (14 skills)
`web-app-pentest` · `api-security-testing` · `client-side-auth-bypass` · `vulnclaw-web-pentest` · `vulnclaw-web-security-advanced` · `vulnclaw-waf-bypass` · `vulnclaw-ctf-web` · `ctf-pwn-web-methodology` · `full-stack-vulnerability-research` · `sql-server-exploitation` · `vulnclaw-client-reverse` · `vulnclaw-android-pentest` · `playwright-browser`

### 🖥️ Network Pentest (6 skills)
`network-pentest` · `pentest` · `pentest-tool-installation` · `vulnclaw-pentest-flow` · `vulnclaw-pentest-tools` · `vulnclaw-rapid-checklist`

### 💥 Exploit Development (10 skills)
`exploit-development` · `zero-day-hunting` · `kernel-exploitation` · `vulnclaw-exploitation` · `vulnclaw-crypto-toolkit` · `vulnclaw-ctf-crypto` · `cryptography` · `ctf-cryptography` · `ctf-encoding-realignment` · `ctf-pwn-binary-exploitation`

### 🔧 Reverse Engineering (3 skills)
`reverse-engineering` · `ctf-reverse-engineering` · `ctf-forensics`

### 🚩 CTF (12 skills)
`ctf-playbook` · `ctf-general` · `ctf-misc` · `ctf-technique-atlas` · `ctf-training-loop` · `ctf-web-exploitation` · `ctf-writeup-artifact-discipline` · `natural-ctf-writeup-screenshots` · `ctf-kernel-exploitation` · `vulnclaw-ctf-misc`

### 🎯 Post-Exploitation (6 skills)
`vulnclaw-post-exploitation` · `vulnclaw-intranet-pentest-advanced` · `overclock-combat-pentest` · `professional-pentest-mastery` · `strix-pentest` · `vulnclaw-reporting`

### ☁️ Cloud & AI Security (7 skills)
`vulnclaw-ai-mcp-security` · `ai-mcp-security` · `modern-attack-surfaces` · `security-and-hardening` · `claude-code-security-review` · `security-audit` · `hackingtool`

### 🔌 Hardware & IoT (12 skills)
`hardware-iot-hacking` · `bt-classic-segmented-sweep` · `esp32-wifi-killer-v12` · `nrf24-bitbang-driver` · `rfclown-multi-protocol-jammer` · `esp32-dualband-wifi-jammer` · `esp32-serial-diagnostics` · `flipper-zero-back` · `flipper-zero-firmware-modification` · `rf-clown-master` · `smart-card-reader-driver-debugging` · `smart-card-usb-direct`

---

## Usage

### The Orchestrator

`security-orchestrator` is the master router. When a user asks about any security task, it:
1. Analyzes intent
2. Routes to the right specialized skill(s)
3. Can trigger parallel skill loading for speed

### Routing Logic

```
"scan this target"         → recon + web-app-pentest
"exploit this bug"         → exploit-development
"reverse this binary"      → reverse-engineering
"CTF challenge"           → ctf (ctf-general routes further)
"enumerate network"        → network-pentest
"OSINT on person/domain"   → recon (osint)
"bypass WAF"               → web-pentest (vulnclaw-waf-bypass)
"privilege escalation"     → post-exploitation
"audit this code"          → cloud-security (security-audit)
"hack IoT device"          → hardware-iot
"AI security / MCP"        → cloud-security (ai-mcp-security)
"fuzz this target"         → exploit-dev (zero-day-hunting)
"crack this hash"          → exploit-dev (cryptography)
"pentest report"           → post-exploitation (vulnclaw-reporting)
```

### Selective Install

```bash
# Install only specific domains
./install.sh --agent claude-code --domains web-pentest,exploit-dev

# Install only CTF skills
./install.sh --agent claude-code --domains ctf

# Install only the orchestrator
./install.sh --agent claude-code --skills security-orchestrator
```

### Skill Structure

Every skill follows the Agent Skills open standard:

```
skills/
├── security-orchestrator/          # Master router
│   └── SKILL.md
├── recon/
│   ├── osint/
│   │   ├── SKILL.md                # Instructions + YAML frontmatter
│   │   ├── references/             # Deep knowledge files
│   │   └── scripts/                # Helper automation
│   └── ...
└── ...
```

### Rules Library

Shared knowledge loaded across skills:

| File | Contents |
|:-----|:---------|
| `rules/security-rules.md` | Payloads (XSS/SSRF/SQLi/SSTI), WAF bypass ladder, hunting rules, top 10 mistakes |

### Provider Configs

Pre-configured instruction files in `providers/`:

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

## Compatibility

This follows the [Agent Skills open standard](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) — portable directories with `SKILL.md` files and YAML frontmatter. Works with any agent that supports the `SKILL.md` format.

| Agent | Install location |
|:------|:-----------------|
| Claude Code | `.claude/skills/` or `~/.claude/skills/` |
| Codex | `.codex/skills/` or `AGENTS.md` |
| Cursor | `.cursor/skills/` or `.cursorrules` |
| Gemini CLI | `.gemini/skills/` |
| Windsurf | `.windsurf/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenClaw | `.agents/skills/` |
| Hermes Agent | `~/.hermes/skills/` |

---

## Contributing

PRs welcome. New skills must include:
1. `SKILL.md` with required YAML frontmatter (`name`, `description`)
2. At least one `references/` file with real knowledge (not AI-generated)
3. Trigger conditions in `description` field
4. Tested in at least one agent before submitting

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

[MIT](LICENSE) — Use for authorized security testing only. Follow responsible disclosure.
