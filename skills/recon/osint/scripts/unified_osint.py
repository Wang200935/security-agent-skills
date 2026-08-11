#!/usr/bin/env python3
"""
Unified OSINT Investigation Wrapper
Combines OpenOSINT AI-chained tools with OSINT-Framework resource catalog.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from osint_framework_search import load_catalog, search_tools, find_category


class OpenOSINTWrapper:
    """Wrapper for OpenOSINT CLI and MCP tools."""

    def __init__(self):
        self.openosint_bin = Path("/Users/wang/.hermes/hermes-agent/venv/bin/openosint")
        self.mcp_server = Path("/tmp/OpenOSINT/openosint/mcp_server.py")
        self.python_bin = Path("/Users/wang/.hermes/hermes-agent/venv/bin/python")

    def run_cli(self, args: List[str], timeout: int = 120) -> Dict:
        """Run openosint CLI command."""
        cmd = [str(self.openosint_bin)] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timeout after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def email_scan(self, email: str, json_output: bool = False) -> Dict:
        """Run direct email scan via holehe."""
        args = ["email", email]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def username_scan(self, username: str, json_output: bool = False) -> Dict:
        """Run direct username scan via sherlock."""
        args = ["username", username]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def domain_scan(self, domain: str, json_output: bool = False) -> Dict:
        """Run direct subdomain scan via sublist3r."""
        args = ["domain", domain]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def shodan_scan(self, query: str, json_output: bool = False) -> Dict:
        """Run Shodan scan."""
        args = ["shodan", query]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def virustotal_scan(self, target: str, json_output: bool = False) -> Dict:
        """Run VirusTotal scan."""
        args = ["virustotal", target]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def censys_scan(self, target: str, json_output: bool = False) -> Dict:
        """Run Censys scan."""
        args = ["censys", target]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def github_scan(self, query: str, json_output: bool = False) -> Dict:
        """Run GitHub scan."""
        args = ["github", query]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def dns_scan(self, domain: str, json_output: bool = False) -> Dict:
        """Run DNS scan."""
        args = ["dns", domain]
        if json_output:
            args.append("--json")
        return self.run_cli(args)

    def generate_dorks(self, target: str) -> Dict:
        """Generate Google dorks for target."""
        return self.run_cli(["--provider", "anthropic", "investigate", target, "--tools", "generate_dorks"])

    def investigate(self, target: str, tools: Optional[List[str]] = None) -> Dict:
        """Run full AI investigation on target."""
        args = ["investigate", target]
        if tools:
            args.extend(["--tools", ",".join(tools)])
        return self.run_cli(args, timeout=300)

    def multi_target(self, targets: List[str]) -> Dict:
        """Run multi-target parallel investigation."""
        args = ["multi"] + targets
        return self.run_cli(args, timeout=600)

    def history(self, open_id: Optional[int] = None, clear: bool = False) -> Dict:
        """Manage session history."""
        args = ["history"]
        if open_id:
            args.extend(["open", str(open_id)])
        if clear:
            args.append("clear")
        return self.run_cli(args)


class OSINTFrameworkWrapper:
    """Wrapper for OSINT Framework catalog."""

    def __init__(self):
        self.catalog = load_catalog()

    def search(self, query: str) -> List[Dict]:
        """Search tools by keyword."""
        results = []
        search_tools(self.catalog, query, results)
        return results

    def get_categories(self) -> List[Dict]:
        """Get all top-level categories with tool counts."""
        def count_tools(node: Dict) -> int:
            if node.get("type") == "url":
                return 1
            return sum(count_tools(c) for c in node.get("children", []))

        categories = []
        for child in self.catalog.get("children", []):
            if child.get("type") == "folder":
                categories.append({
                    "name": child.get("name"),
                    "tool_count": count_tools(child),
                    "subcategories": [c.get("name") for c in child.get("children", []) if c.get("type") == "folder"]
                })
        return categories

    def get_tools_in_category(self, category_name: str, subcategory_name: Optional[str] = None) -> List[Dict]:
        """Get all tools in a category/subcategory."""
        category = find_category(self.catalog, category_name)
        if not category:
            return []

        if subcategory_name:
            for child in category.get("children", []):
                if child.get("type") == "folder" and subcategory_name.lower() in child.get("name", "").lower():
                    category = child
                    break

        tools = []
        def collect(node: Dict, path: str = ""):
            name = node.get("name", "")
            current_path = f"{path} > {name}" if path else name
            if node.get("type") == "url":
                tools.append({
                    "name": name,
                    "url": node.get("url", ""),
                    "description": node.get("description", ""),
                    "category_path": current_path,
                    "metadata": {k: v for k, v in node.items()
                               if k not in ["name", "type", "url", "description", "children"]}
                })
            elif node.get("type") == "folder":
                for child in node.get("children", []):
                    collect(child, current_path)

        collect(category)
        return tools

    def get_recommended_tools(self, target_type: str) -> List[Dict]:
        """Get recommended tools for a target type (email, username, domain, ip, phone)."""
        type_mapping = {
            "email": [("Email Address", "Email Search"), ("Email Address", "Breach Data")],
            "username": [("Username", "Username Search Engines")],
            "domain": [("Domain Name", "Subdomains"), ("Domain Name", "Certificate Search"), ("Domain Name", "Discovery")],
            "ip": [("IP & MAC Address", "Reputation"), ("IP & MAC Address", "Geolocation")],
            "phone": [("Telephone Numbers", "Phone Search")],
        }

        recommendations = []
        for cat, subcat in type_mapping.get(target_type.lower(), []):
            recommendations.extend(self.get_tools_in_category(cat, subcat))
        return recommendations


class UnifiedOSINT:
    """Unified interface combining both OSINT systems."""

    def __init__(self):
        self.openosint = OpenOSINTWrapper()
        self.framework = OSINTFrameworkWrapper()

    def investigate_email(self, email: str) -> Dict:
        """Comprehensive email investigation using both systems."""
        print(f"🔍 Investigating email: {email}")
        results = {"email": email, "openosint": {}, "framework_tools": []}

        # OpenOSINT direct tools
        print("  → Running OpenOSINT email scan...")
        results["openosint"]["email_scan"] = self.openosint.email_scan(email, json_output=True)

        print("  → Running OpenOSINT breach check...")
        results["openosint"]["breach"] = self.openosint.run_cli(["email", email])  # breach is part of investigate

        print("  → Running OpenOSINT paste search...")
        results["openosint"]["paste"] = self.openosint.run_cli(["email", email])

        print("  → Generating dorks...")
        results["openosint"]["dorks"] = self.openosint.generate_dorks(email)

        # Framework recommended tools
        print("  → Getting Framework recommended tools...")
        results["framework_tools"] = self.framework.get_recommended_tools("email")

        return results

    def investigate_domain(self, domain: str) -> Dict:
        """Comprehensive domain investigation."""
        print(f"🔍 Investigating domain: {domain}")
        results = {"domain": domain, "openosint": {}, "framework_tools": []}

        # OpenOSINT
        print("  → WHOIS...")
        results["openosint"]["whois"] = self.openosint.run_cli(["dns", domain])  # DNS includes WHOIS-like info

        print("  → Subdomain enumeration...")
        results["openosint"]["subdomains"] = self.openosint.domain_scan(domain, json_output=True)

        print("  → DNS records...")
        results["openosint"]["dns"] = self.openosint.dns_scan(domain, json_output=True)

        print("  → Generating dorks...")
        results["openosint"]["dorks"] = self.openosint.generate_dorks(domain)

        # Framework
        print("  → Getting Framework recommended tools...")
        results["framework_tools"] = self.framework.get_recommended_tools("domain")

        return results

    def investigate_username(self, username: str) -> Dict:
        """Comprehensive username investigation."""
        print(f"🔍 Investigating username: {username}")
        results = {"username": username, "openosint": {}, "framework_tools": []}

        print("  → Username scan...")
        results["openosint"]["username_scan"] = self.openosint.username_scan(username, json_output=True)

        print("  → GitHub scan...")
        results["openosint"]["github"] = self.openosint.github_scan(username, json_output=True)

        print("  → Paste search...")
        results["openosint"]["paste"] = self.openosint.run_cli(["email", username])  # paste search

        print("  → Generating dorks...")
        results["openosint"]["dorks"] = self.openosint.generate_dorks(username)

        # Framework
        print("  → Getting Framework recommended tools...")
        results["framework_tools"] = self.framework.get_recommended_tools("username")

        return results

    def investigate_ip(self, ip: str) -> Dict:
        """Comprehensive IP investigation."""
        print(f"🔍 Investigating IP: {ip}")
        results = {"ip": ip, "openosint": {}, "framework_tools": []}

        # OpenOSINT
        print("  → IP geolocation...")
        results["openosint"]["ip"] = self.openosint.run_cli(["shodan", ip], json_output=True)

        print("  → Shodan...")
        results["openosint"]["shodan"] = self.openosint.shodan_scan(ip, json_output=True)

        print("  → VirusTotal...")
        results["openosint"]["virustotal"] = self.openosint.virustotal_scan(ip, json_output=True)

        print("  → Censys...")
        results["openosint"]["censys"] = self.openosint.censys_scan(ip, json_output=True)

        # Framework
        print("  → Getting Framework recommended tools...")
        results["framework_tools"] = self.framework.get_recommended_tools("ip")

        return results

    def quick_search(self, query: str) -> Dict:
        """Quick search across both systems."""
        print(f"🔍 Quick search: {query}")
        results = {"query": query, "framework_results": [], "recommended_tools": {}}

        # Framework search
        results["framework_results"] = self.framework.search(query)

        # Determine target type and get recommendations
        if "@" in query:
            results["recommended_tools"]["email"] = self.framework.get_recommended_tools("email")
        elif "." in query and not query.startswith("http"):
            results["recommended_tools"]["domain"] = self.framework.get_recommended_tools("domain")
        else:
            results["recommended_tools"]["username"] = self.framework.get_recommended_tools("username")

        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unified OSINT Investigation Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Email investigation
    email_parser = subparsers.add_parser("email", help="Investigate email address")
    email_parser.add_argument("address", help="Email address")

    # Domain investigation
    domain_parser = subparsers.add_parser("domain", help="Investigate domain")
    domain_parser.add_argument("domain", help="Domain name")

    # Username investigation
    user_parser = subparsers.add_parser("username", help="Investigate username")
    user_parser.add_argument("handle", help="Username")

    # IP investigation
    ip_parser = subparsers.add_parser("ip", help="Investigate IP address")
    ip_parser.add_argument("address", help="IP address")

    # Quick search
    search_parser = subparsers.add_parser("search", help="Quick search both systems")
    search_parser.add_argument("query", help="Search query")

    # Framework search
    fw_search = subparsers.add_parser("fw-search", help="Search OSINT Framework catalog")
    fw_search.add_argument("query", help="Search query")

    # List categories
    subparsers.add_parser("categories", help="List OSINT Framework categories")

    # OpenOSINT direct
    oo_parser = subparsers.add_parser("openosint", help="Run OpenOSINT CLI command")
    oo_parser.add_argument("args", nargs="*", help="OpenOSINT arguments")

    args = parser.parse_args()

    unified = UnifiedOSINT()

    if args.command == "email":
        result = unified.investigate_email(args.address)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "domain":
        result = unified.investigate_domain(args.domain)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "username":
        result = unified.investigate_username(args.handle)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "ip":
        result = unified.investigate_ip(args.address)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "search":
        result = unified.quick_search(args.query)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "fw-search":
        results = unified.framework.search(args.query)
        for r in results:
            print(f"🔗 {r['name']}")
            print(f"   Category: {r['category_path']}")
            print(f"   URL: {r['url']}")
            print(f"   Description: {r['description'][:200]}")
            print()

    elif args.command == "categories":
        cats = unified.framework.get_categories()
        print(f"{'Category':<50} {'Tools':>6} {'Subcategories'}")
        print("-" * 100)
        for c in cats:
            subs = ", ".join(c["subcategories"][:3])
            if len(c["subcategories"]) > 3:
                subs += f" ... (+{len(c['subcategories'])-3} more)"
            print(f"{c['name']:<50} {c['tool_count']:>6} {subs}")

    elif args.command == "openosint":
        result = unified.openosint.run_cli(args.args)
        if result["success"]:
            print(result["stdout"])
        else:
            print(f"Error: {result.get('error', result['stderr'])}", file=sys.stderr)
            sys.exit(result["returncode"])

    else:
        parser.print_help()


if __name__ == "__main__":
    main()