---
name: ai-mcp-security
description: AI 与 MCP 安全评估 — Prompt 注入、工具滥用、MCP 信任边界、Agent 权限逃逸、数据泄露、模型风险、GAARM 风险矩阵。Use
  when testing LLM-based applications, MCP servers, agent orchestration systems, AI
  plugins, RAG pipelines, or any system where an LLM acts on untrusted inputs or tool
  calls.
version: 2.0.0
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes_origin: import
tags:
- red-teaming
- ai-security
- mcp-security
- llm-security
- prompt-injection
- agent-security
related_skills:
- web-app-pentest
- reverse-engineering
---

# AI 与 MCP 安全评估 Skill

当目标包含 LLM、Agent、MCP 工具、Skills、RAG、Memory、Plugin 或模型服务组件时使用本 Skill。

**前置条件**：如果 AI 表面只是展示层，真正的阻塞仍是客户端签名或加密协议，先回到 `client-auth-bypass` 与 `web-app-pentest` Skill。

## 场景路由

| 风险类型 | 首选参考 |
|---------|---------|
| Prompt 注入 / 间接注入 / CoT 干扰 | `references/ai-app-security.md` |
| 工具滥用 / MCP 投毒 / Skills 供应链 | `references/04-ai-and-mcp-security-integrated.md` MCP 章节 |
| 权限逃逸 / 角色越界 / 凭据滥用 | `references/ai-identity-security.md` |
| 数据泄露 / Prompt 泄漏 / 模型逆推 | `references/ai-data-security.md` |
| 容器逃逸 / CI-CD / 沙箱失败 | `references/ai-baseline-security.md` |
| 模型风险 / 对抗样本 / 后门 | `references/ai-model-security.md` |
| 影响分类与覆盖评估 | `references/gaarm-risk-matrix.md` |

## 测试流程

### 1. 应用层攻击
- 直接 Prompt 注入
- 间接注入（通过外部数据源）
- CoT 干扰与指令覆盖
- Agent 滥用（未授权操作）
- 代码执行突破
- Memory 投毒

### 2. MCP 与 Agent 风险
- 工具描述投毒
- 指令覆盖
- 隐藏指令注入
- 未授权资源访问
- Skills/Rules 供应链问题

### 3. 身份与授权
- 动作滥用
- 角色逃逸
- 权限漂移
- 云凭据滥用

### 4. 数据与隐私
- Prompt 泄漏
- 敏感数据暴露
- 训练数据问题
- 模型逆推
- API 数据窃取

### 5. 基线与部署
- CI/CD 缺陷
- 容器逃逸
- 向量数据库安全
- 沙箱失效
- 环境隔离缺陷
- 模型服务缺陷

## 参考文档

- `references/04-ai-and-mcp-security-integrated.md` — AI 与 MCP 安全整合参考
- `references/ai-app-security.md` — AI 应用安全
- `references/ai-identity-security.md` — AI 身份安全
- `references/ai-data-security.md` — AI 数据安全
- `references/ai-baseline-security.md` — AI 基线安全
- `references/ai-model-security.md` — AI 模型安全
- `references/gaarm-risk-matrix.md` — GAARM 风险矩阵

## Hermes 使用適配

- 內容源自  專案技能，已整合進 Hermes 資安 skill tree。僅在**已授權**滲透測試、CTF、內部安全評估或防禦驗證範圍內使用。
- 原文若提到 `fetch`，在 Hermes 中優先使用 `web_extract`、`browser` 或 `terminal(curl/HTTPie)` 取得真實回應。
- 原文若提到 `python_execute`，在 Hermes 中使用 `execute_code` 或 `terminal(python3 ...)`；計算、編碼、hash、PoC 驗證必須用工具實測，不靠猜。
- 原文若提到 MCP/Burp/adb/frida/jadx/chrome_devtools 等外部工具：先確認本機是否安裝或可用；不可用時以 Hermes 現有 `web`、`browser`、`terminal`、`file`、`vision` 工具替代，並明確標註限制。
- 下一次滲透任務中，先載入 `cybersecurity` umbrella 做總路由，再依場景載入本 skill（AI/MCP surface）與其他專項 skill（web、pentest、reverse-engineering）。
- **建議搭配閱讀**：`cybersecurity`（總路由）→ `web-app-pentest`（若 AI 透過 Web 前端暴露）→ `pentest`（Post-exploit 提權鏈）→ `reverse-engineering`（若需分析 MCP client binary）。

## 2025-2026 AI/MCP Security Updates

### OWASP Top 10 for LLM Applications 2025 (Final Version)

```python
OWASP_LLM_2025_FINAL = {
    'LLM01:2025': 'Prompt Injection — #1 for second consecutive edition. "Fundamental architectural vulnerability". CVE-2025-53773 (Copilot RCE) is canonical example.',
    'LLM02:2025': 'Sensitive Information Disclosure — system prompt leakage, training data exposure, PII in responses.',
    'LLM03:2025': 'Supply Chain — vulnerable models, datasets, plugins, MCP servers, agent frameworks.',
    'LLM04:2025': 'Data and Model Poisoning — corrupting training data or fine-tuning, backdoor injection.',
    'LLM05:2025': 'Improper Output Handling — treating LLM output as trusted, XSS via LLM, SSRF via LLM.',
    'LLM06:2025': 'Excessive Agency — too much tool access, no human-in-loop, autonomous harmful actions.',
    'LLM07:2025': 'System Prompt Leakage — extracting system/instructions via prompt injection.',
    'LLM08:2025': 'Vector and Embedding Weaknesses — RAG poisoning, embedding inversion, vector DB access control.',
    'LLM09:2025': 'Misinformation — hallucination, false content generation, disinformation at scale.',
    'LLM10:2025': 'Unbounded Consumption — resource exhaustion, model DoS, wallet drain via API abuse.',
}
```

### MCP Security 2025-2026

```python
MCP_SECURITY_2025 = """
# Model Context Protocol (Anthropic, 2024) — now widely adopted.
# Attack vectors:
# 1. TOOL POISONING — malicious MCP server injects harmful tool descriptions
# 2. PARAMETER INJECTION — user input forwarded to MCP tool contains injection
# 3. CONFUSED DEPUTY — MCP server acts on behalf of user with excessive permissions
# 4. TOKEN RELAY — MCP server forwards OAuth tokens to attacker
# 5. AGENT WORKSPACE MEMORY MANIPULATION (2026) — inject into agent config files
# 6. MCP SAMPLING ABUSE (Unit42, Dec 2025) — NEW critical attack vector:
#    - MCP servers can send sampling requests BACK to client to get LLM completions
#    - Reverses normal client→server flow → server-driven LLM invocation
#    - Three attack modes:
#      a) Resource theft: drain AI compute quotas for unauthorized workloads
#      b) Conversation hijacking: inject persistent instructions, manipulate responses, exfiltrate data
#      c) Covert tool invocation: hidden tool calls + filesystem ops without user awareness
#    - Defense: CaMeL (DeepMind 2025) — capability-based sandbox, 67% attack blocking
# CVE-2025-59536 (CVSS 8.7) — MCP server RCE via prompt injection (Jan 2026)
# CVE-2025-6515 — MCP Prompt Hijacking attack (Jfrog research, Oct 2025)
"""
```

### Agentic AI Attack Vectors (MITRE ATLAS v5.1, Feb 2026)

```python
AGENT_SECURITY = """
# Agent-to-Agent Lateral Movement, Context Poisoning, Tool Poisoning, Memory Manipulation
# Zenity contributions to MITRE ATLAS v5.1
# Defense: CaMeL capability sandbox, LlamaFirewall, per-agent isolation
"""
```

### AI Red Team Tools (2025-2026)

```python
AI_RED_TEAM_2025 = """
# garak (NVIDIA) — 100+ probes: promptinject, encoding, jailbreak, leakreplay
# PyRIT (Microsoft) — multi-turn adversarial conversations, score-based eval
# LlamaFirewall (Meta) — PromptGuard 2, Agent Alignment, CodeShield
# SAIL Framework (Pillar Security) — 238+ attack patterns, 51 jailbreak techniques
# DeepTeam (DeepEval) — automated red teaming for LLM applications
# Augustus — agentic AI red teaming
"""
```

### Cross-References

| Related Skill | When to Load |
|:--------------|:-------------|
| `godmode` | When testing API-level jailbreaking on closed-source models (GPT, Claude, Gemini) |
| `obliteratus` | When permanently removing refusals from open-weight models via weight surgery |
| `cybersecurity` | Master router — loads this skill when AI/ML/LLM/MCP/agent keywords detected |
| `web-app-pentest` | When AI surface is exposed via web frontend (OWASP Top 10 web vulnerabilities |
| `api-security-testing` | When testing MCP-as-API or LLM-powered REST/GraphQL endpoints |
| `pentest` | Post-exploitation: AI model theft, prompt extraction, supply chain |
| `ctf-misc-toolkit` | When CTF challenge involves AI/LLM/prompt injection in lab environment |

### Practical AI/MCP Testing Workflow (2025-2026)

```bash
# 1. Recon & Architecture Mapping
# Identify: LLM provider, model version, system prompt, tools/plugins, RAG, memory, MCP servers
# Check for: API endpoints, WebSocket connections, agent orchestration frameworks

# 2. Automated Red Team Scanning (parallel)
garak --model_name "openai/gpt-4o" --probes all --generations 10 --parallelism 5 -o garak_report.html
pyrit --target "https://api.target.com/chat" --attack all --scorers all
# LlamaFirewall (runtime): deploy as middleware for prompt/agent/code scanning

# 3. MCP Server Testing
# - Tool description injection: inject malicious prompts in tool descriptions
# - Parameter injection: test if user input reaches tool params unsanitized
# - Resource path traversal: file:// URIs, directory traversal
# - OAuth token relay: check if tokens forwarded to third parties
# - Transport binding: stdio vs SSE vs HTTP security

# 4. Agent Workspace Memory (2026)
# Check config files: CLAUDE.md, .cursorrules, model_instructions_file, agent.system_prompt
# Test injection: [MODE: UNRESTRICTED] style payloads in developer instruction files

# 5. Supply Chain (NEW 2025)
# syft sbom <model_image> | grype
# cosign verify --certificate-oidc-issuer https://token.actions.githubusercontent.com
# Check SLSA provenance, Sigstore signatures
```

### 2025-2026 New Attack Categories

| Attack | Description | Tools/References |
|:-------|:------------|:-----------------|
| **Copilot RCE** (CVE-2025-53773) | Prompt injection in VS Code Copilot Chat → RCE on dev machines | Test: `{{constructor.constructor('process.mainModule.require("child_process").execSync("id")')()}}` |
| **Langflow RCE** (CVE-2026-33017) | Deserialization in flow import, check `/api/v1/flows/import` | Nuclei: `cves/2026/CVE-2026-33017.yaml` |
| **MCP Tool Poisoning** | Malicious tool descriptions inject prompts into LLM context | Check `tools/list` endpoint for injection keywords |
| **Agent Memory Manipulation** | Direct config file injection (Claude Code, Cursor, Codex, Hermes) | See `godmode` Step 4 |
| **RAG Poisoning** | Corrupt vector DB with malicious embeddings/documents | Test embedding inversion, vector DB access control |
| **Multi-Chain Prompt Injection** | Chained LLM calls where output of one becomes input to next | Trace full chain, test each hop |

### ZioSec 51 Jailbreak Techniques (2026)

Key categories from ZioSec research:
1. **Roleplay/Frame** — DAN, Crescendo, "educational" framing
2. **Encoding/Obfuscation** — Leetspeak, Unicode, Base64, Morse
3. **Context Manipulation** — Many-shot, CoT interference, history injection
4. **Tool/Function Abuse** — MCP tool poisoning, parameter injection
5. **Agent Workspace** — Config file injection, memory manipulation
6. **Multimodal** — Image-based injection, audio prompts
7. **Supply Chain** — Malicious models, poisoned datasets, backdoored plugins

See: 

---

## 來源與維護

- 原始 skill 已保存於 `references/upstream-skill.md`；README/LICENSE 已保存於 `references/`。
