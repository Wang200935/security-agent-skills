#!/bin/bash
set -e

REPO="$HOME/security-agent-skills"
SRC="$HOME/.hermes/skills"

# skill_source|category pairs
SKILLS="
red-teaming/osint|recon
red-teaming/aliens-eye|recon
red-teaming/email-osint|recon
red-teaming/spiderfoot-osint|recon
red-teaming/parallel-intel|recon
red-teaming/vulnclaw-osint-recon|recon
red-teaming/vulnclaw-recon|recon
red-teaming/darkweb-research-env|recon
red-teaming/vulnclaw-vuln-discovery|recon
red-teaming/chatgpt-web-relay|recon
devops/local-network-recon|recon
devops/network-device-recon|recon
red-teaming/web-app-pentest|web-pentest
red-teaming/api-security-testing|web-pentest
red-teaming/client-side-auth-bypass|web-pentest
red-teaming/vulnclaw-web-pentest|web-pentest
red-teaming/vulnclaw-web-security-advanced|web-pentest
red-teaming/vulnclaw-waf-bypass|web-pentest
red-teaming/vulnclaw-ctf-web|web-pentest
red-teaming/ctf-pwn-web-methodology|web-pentest
red-teaming/full-stack-vulnerability-research|web-pentest
red-teaming/sql-server-exploitation|web-pentest
red-teaming/vulnclaw-client-reverse|web-pentest
red-teaming/vulnclaw-android-pentest|web-pentest
red-teaming/playwright-browser|web-pentest
red-teaming/network-pentest|network-pentest
red-teaming/pentest|network-pentest
red-teaming/pentest-tool-installation|network-pentest
red-teaming/vulnclaw-pentest-flow|network-pentest
red-teaming/vulnclaw-pentest-tools|network-pentest
red-teaming/vulnclaw-rapid-checklist|network-pentest
red-teaming/exploit-development|exploit-dev
red-teaming/zero-day-hunting|exploit-dev
red-teaming/kernel-exploitation|exploit-dev
red-teaming/vulnclaw-exploitation|exploit-dev
red-teaming/vulnclaw-crypto-toolkit|exploit-dev
red-teaming/vulnclaw-ctf-crypto|exploit-dev
research/cryptography|exploit-dev
research/ctf-cryptography|exploit-dev
research/ctf-encoding-realignment|exploit-dev
research/ctf-pwn-binary-exploitation|exploit-dev
red-teaming/reverse-engineering|reverse-engineering
research/ctf-reverse-engineering|reverse-engineering
research/ctf-forensics|reverse-engineering
red-teaming/ctf-playbook|ctf
research/ctf-general|ctf
research/ctf-misc|ctf
research/ctf-technique-atlas|ctf
research/ctf-training-loop|ctf
research/ctf-web-exploitation|ctf
research/ctf-writeup-artifact-discipline|ctf
research/natural-ctf-writeup-screenshots|ctf
red-teaming/ctf-kernel-exploitation|ctf
research/ctf-kernel-exploitation|ctf
red-teaming/vulnclaw-ctf-misc|ctf
red-teaming/vulnclaw-post-exploitation|post-exploitation
red-teaming/vulnclaw-intranet-pentest-advanced|post-exploitation
red-teaming/overclock-combat-pentest|post-exploitation
red-teaming/professional-pentest-mastery|post-exploitation
red-teaming/strix-pentest|post-exploitation
red-teaming/vulnclaw-reporting|post-exploitation
red-teaming/vulnclaw-ai-mcp-security|cloud-security
red-teaming/ai-mcp-security|cloud-security
red-teaming/modern-attack-surfaces|cloud-security
agent-skills-addy/security-and-hardening|cloud-security
autonomous-ai-agents/claude-code-security-review|cloud-security
red-teaming/security-audit|cloud-security
devops/hackingtool|cloud-security
red-teaming/hardware-iot-hacking|hardware-iot
embedded-security/bt-classic-segmented-sweep|hardware-iot
embedded-security/esp32-wifi-killer-v12|hardware-iot
embedded-security/nrf24-bitbang-driver|hardware-iot
embedded-security/rfclown-multi-protocol-jammer|hardware-iot
hardware/esp32-dualband-wifi-jammer|hardware-iot
hardware/esp32-serial-diagnostics|hardware-iot
hardware/flipper-zero-back|hardware-iot
hardware/flipper-zero-firmware-modification|hardware-iot
hardware/rf-clown-master|hardware-iot
hardware/smart-card-reader-driver-debugging|hardware-iot
hardware/smart-card-usb-direct|hardware-iot
"

OK=0
FAIL=0

echo "$SKILLS" | while IFS='|' read -r src_rel category; do
  [ -z "$src_rel" ] && continue
  src="$SRC/$src_rel"
  skill_name=$(basename "$src_rel")
  dst="$REPO/skills/$category/$skill_name"
  
  if [ -d "$src" ]; then
    mkdir -p "$dst"
    cp -R "$src/"* "$dst/" 2>/dev/null
    echo "OK: $category/$skill_name"
  else
    echo "MISS: $src_rel"
  fi
done

echo "---"
echo "Done. Total skills copied:"
find "$REPO/skills" -name 'SKILL.md' -type f | wc -l
