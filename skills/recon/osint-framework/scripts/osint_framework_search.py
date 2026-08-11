#!/usr/bin/env python3
"""
OSINT Framework Catalog Search Script
Searches the local arf.json catalog (1100+ tools, 35 categories)
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

CATALOG_PATH = Path(__file__).parent.parent / "references" / "osint-framework-catalog.json"


def load_catalog() -> Dict:
    """Load the OSINT Framework catalog."""
    with open(CATALOG_PATH, "r") as f:
        return json.load(f)


def find_category(catalog: Dict, category_name: str) -> Optional[Dict]:
    """Find a category by name (case-insensitive, partial match)."""
    category_name_lower = category_name.lower()
    for child in catalog.get("children", []):
        if child.get("type") == "folder" and category_name_lower in child.get("name", "").lower():
            return child
    return None


def find_subcategory(category: Dict, subcategory_name: str) -> Optional[Dict]:
    """Find a subcategory within a category."""
    subcategory_name_lower = subcategory_name.lower()
    for child in category.get("children", []):
        if child.get("type") == "folder" and subcategory_name_lower in child.get("name", "").lower():
            return child
    return None


def search_tools(node: Dict, query: str, results: List[Dict], path: str = ""):
    """Recursively search for tools matching query."""
    query_lower = query.lower()
    name = node.get("name", "")
    current_path = f"{path} > {name}" if path else name

    if node.get("type") == "url":
        description = node.get("description", "")
        url = node.get("url", "")
        # Search in name, description, and URL
        if (query_lower in name.lower() or
            query_lower in description.lower() or
            query_lower in url.lower()):
            results.append({
                "name": name,
                "url": url,
                "description": description,
                "category_path": current_path,
                "metadata": {k: v for k, v in node.items()
                           if k not in ["name", "type", "url", "description", "children"]}
            })
    elif node.get("type") == "folder":
        for child in node.get("children", []):
            search_tools(child, query, results, current_path)


def list_categories(catalog: Dict):
    """Print all top-level categories with tool counts."""
    def count_tools(node: Dict) -> int:
        if node.get("type") == "url":
            return 1
        return sum(count_tools(c) for c in node.get("children", []))

    print(f"{'Category':<50} {'Tools':>6}")
    print("-" * 57)
    for child in catalog.get("children", []):
        if child.get("type") == "folder":
            count = count_tools(child)
            print(f"{child.get('name', 'Unknown'):<50} {count:>6}")


def list_tools(category_node: Dict, indent: int = 0):
    """Print all tools in a category/subcategory."""
    prefix = "  " * indent
    for child in category_node.get("children", []):
        if child.get("type") == "folder":
            print(f"{prefix}📁 {child.get('name', 'Unknown')}")
            list_tools(child, indent + 1)
        elif child.get("type") == "url":
            name = child.get("name", "Unknown")
            url = child.get("url", "")
            desc = child.get("description", "")[:80]
            status = child.get("status", "")
            pricing = child.get("pricing", "")
            meta = f"[{status}]" if status else ""
            if pricing:
                meta += f" [{pricing}]"
            print(f"{prefix}🔗 {name} {meta}")
            if desc:
                print(f"{prefix}    {desc}...")
            print(f"{prefix}    {url}")


def get_tool_details(category_node: Dict, tool_name: str) -> Optional[Dict]:
    """Find a specific tool by name within a category tree."""
    tool_name_lower = tool_name.lower()
    for child in category_node.get("children", []):
        if child.get("type") == "url" and tool_name_lower in child.get("name", "").lower():
            return child
        elif child.get("type") == "folder":
            result = get_tool_details(child, tool_name)
            if result:
                return result
    return None


def export_category(category_node: Dict, format: str = "json") -> str:
    """Export category tools to JSON or CSV."""
    tools = []

    def collect_tools(node: Dict, path: str = ""):
        name = node.get("name", "")
        current_path = f"{path} > {name}" if path else name
        if node.get("type") == "url":
            tools.append({
                "name": name,
                "url": node.get("url", ""),
                "description": node.get("description", ""),
                "category_path": current_path,
                "status": node.get("status", ""),
                "pricing": node.get("pricing", ""),
                "bestFor": node.get("bestFor", ""),
                "input": node.get("input", ""),
                "output": node.get("output", ""),
                "opsec": node.get("opsec", ""),
                "localInstall": node.get("localInstall", False),
                "googleDork": node.get("googleDork", False),
                "registration": node.get("registration", False),
                "api": node.get("api", False),
            })
        elif node.get("type") == "folder":
            for child in node.get("children", []):
                collect_tools(child, current_path)

    collect_tools(category_node)

    if format == "json":
        return json.dumps(tools, indent=2, ensure_ascii=False)
    elif format == "csv":
        import csv
        import io
        output = io.StringIO()
        if tools:
            writer = csv.DictWriter(output, fieldnames=tools[0].keys())
            writer.writeheader()
            writer.writerows(tools)
        return output.getvalue()
    return ""


def main():
    parser = argparse.ArgumentParser(description="Search OSINT Framework catalog")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search tools by keyword")
    search_parser.add_argument("query", help="Search query")

    # Categories command
    subparsers.add_parser("categories", help="List all categories with tool counts")

    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List tools in a category")
    tools_parser.add_argument("category", help="Category name")
    tools_parser.add_argument("subcategory", nargs="?", help="Optional subcategory name")

    # Tool detail command
    tool_parser = subparsers.add_parser("tool", help="Get tool details by name")
    tool_parser.add_argument("name", help="Tool name")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export category to JSON/CSV")
    export_parser.add_argument("category", help="Category name")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json")

    args = parser.parse_args()

    catalog = load_catalog()

    if args.command == "search":
        results = []
        search_tools(catalog, args.query, results)
        if results:
            for r in results:
                print(f"🔗 {r['name']}")
                print(f"   Category: {r['category_path']}")
                print(f"   URL: {r['url']}")
                print(f"   Description: {r['description'][:200]}")
                if r['metadata']:
                    print(f"   Metadata: {r['metadata']}")
                print()
        else:
            print(f"No tools found for: {args.query}")

    elif args.command == "categories":
        list_categories(catalog)

    elif args.command == "tools":
        category = find_category(catalog, args.category)
        if not category:
            print(f"Category not found: {args.category}")
            print("Available categories:")
            for c in catalog.get("children", []):
                if c.get("type") == "folder":
                    print(f"  - {c.get('name')}")
            sys.exit(1)

        if args.subcategory:
            subcategory = find_subcategory(category, args.subcategory)
            if not subcategory:
                print(f"Subcategory not found: {args.subcategory} in {args.category}")
                sys.exit(1)
            list_tools(subcategory)
        else:
            list_tools(category)

    elif args.command == "tool":
        for child in catalog.get("children", []):
            if child.get("type") == "folder":
                tool = get_tool_details(child, args.name)
                if tool:
                    print(json.dumps(tool, indent=2, ensure_ascii=False))
                    return
        print(f"Tool not found: {args.name}")
        sys.exit(1)

    elif args.command == "export":
        category = find_category(catalog, args.category)
        if not category:
            print(f"Category not found: {args.category}")
            sys.exit(1)
        output = export_category(category, args.format)
        print(output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()