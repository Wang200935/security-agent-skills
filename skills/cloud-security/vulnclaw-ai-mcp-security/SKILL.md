---
name: vulnclaw-ai-mcp-security
description: "AI与MCP安全评估 — Prompt注入、工具滥用、MCP信任边界、Agent权限逃逸、数据泄露、模型风险、GAARM风险矩阵。Use when performing authorized penetration testing, CTF, or security assessment tasks related to ai-mcp-security."
version: 1.0.0
author: VulnClaw contributors; ported for Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vulnclaw, red-teaming, penetration-testing, security, imported]
    homepage: https://github.com/Unclecheng-li/VulnClaw
    related_skills: [vulnclaw-pentest-flow, vulnclaw-rapid-checklist, pentest-tools, ctf-web]
  upstream:
    repo: https://github.com/Unclecheng-li/VulnClaw
    source_path: vulnclaw/skills/specialized/ai-mcp-security/SKILL.md
    original_name: ai-mcp-security
---

# AI 与 MCP 安全评估 Skill

当目标包含 LLM、Agent、MCP 工具、Skills、RAG、Memory、Plugin 或模型服务组件时使用本 Skill。

**前置条件**：如果 AI 表面只是展示层，真正的阻塞仍是客户端签名或加密协议，先回到 `vulnclaw-client-reverse` Skill。

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

- 來源為 VulnClaw 專案技能，已匯入 Hermes 本地 skill。僅在**已授權**滲透測試、CTF、內部安全評估或防禦驗證範圍內使用。
- 原文若提到 `fetch`，在 Hermes 中優先使用 `web_extract`、`browser` 或 `terminal(curl/HTTPie)` 取得真實回應。
- 原文若提到 `python_execute`，在 Hermes 中使用 `execute_code` 或 `terminal(python3 ...)`；計算、編碼、hash、PoC 驗證必須用工具實測，不靠猜。
- 原文若提到 MCP/Burp/adb/frida/jadx/chrome_devtools 等外部工具：先確認本機是否安裝或可用；不可用時以 Hermes 現有 `web`、`browser`、`terminal`、`file`、`vision` 工具替代，並明確標註限制。
- 下一次滲透任務中，先載入 `vulnclaw-pentest-flow` 做總路由，再依場景載入本系列專項 skill（例如 `vulnclaw-web-security-advanced`、`vulnclaw-osint-recon`、`vulnclaw-rapid-checklist`）。


## 來源與維護

- Upstream: https://github.com/Unclecheng-li/VulnClaw
- 原始 skill 已保存於 `references/upstream-skill.md`；README/LICENSE 已保存於 `references/`。
