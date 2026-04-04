#!/usr/bin/env python3
"""
Sync Quest Progress from GitHub Issues

This script reads GitHub Issues (quest tiers) and syncs checkbox progress
back to QUEST_TRACKER.md. Source of truth is GitHub Issues.

Works with GitHub Actions via GH_TOKEN environment variable.

Usage:
  GH_TOKEN=your_token python3 sync_quests_from_issues.py
  (Within GitHub Actions, GH_TOKEN is automatically available)
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Tuple


def get_issues_via_gh_cli() -> Dict[str, list]:
    """Fetch all quest issues using GitHub CLI."""
    try:
        # Get all issues with 'bronze', 'silver', or 'gold' labels
        result = subprocess.run(
            [
                "gh",
                "issue",
                "list",
                "--label",
                "bronze,silver,gold",
                "--json",
                "title,body,state,labels",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        issues = json.loads(result.stdout)
        return issues
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch issues: {e.stderr}")
        return []


def extract_quest_tier_from_issue(issue: dict) -> Tuple[str, str, int, int]:
    """
    Extract quest name, tier name, checked count, and total count from an issue.

    Returns: (quest_name, tier_name, checked_count, total_count)
    """
    title = issue["title"]
    body = issue["body"]

    # Parse title: "🛡️ Reliability Engineering — Bronze (The Shield)"
    emoji_match = re.search(r"([🛡️🚀🚨📜])\s+(.+?)\s+—\s+(.+)", title)
    if not emoji_match:
        return None, None, 0, 0

    emoji = emoji_match.group(1)
    quest_name = emoji_match.group(2)
    tier_name = emoji_match.group(3)

    # Count checkboxes in body
    checked = len(re.findall(r"- \[x\]", body, re.IGNORECASE))
    total = len(re.findall(r"- \[[ xX]\]", body))

    return quest_name, tier_name, checked, total


def sync_quest_tracker(issues: list) -> str:
    """
    Sync GitHub Issues to QUEST_TRACKER.md content.
    Returns updated content.
    """
    
    quest_tracker_path = Path("QUEST_TRACKER.md")
    content = quest_tracker_path.read_text(encoding="utf-8")

    # Build a map of quest -> tier -> (checked, total)
    quest_progress = {}
    for issue in issues:
        quest_name, tier_name, checked, total = extract_quest_tier_from_issue(issue)
        if quest_name:
            if quest_name not in quest_progress:
                quest_progress[quest_name] = {}
            quest_progress[quest_name][tier_name] = (checked, total)

    # Update status lines in content
    for quest_name, tiers in quest_progress.items():
        # Calculate completed tiers
        completed = sum(1 for tier, (checked, total) in tiers.items() if total > 0 and checked == total)
        tier_count = len(tiers)

        # Map status
        if completed == 0:
            status_emoji = "🔴"
            status_text = "Not Started"
        elif completed < tier_count:
            total_checked = sum(c for c, t in tiers.values())
            total_items = sum(t for c, t in tiers.values())
            status_emoji = "🟡"
            status_text = f"In Progress ({total_checked}/{total_items})"
        else:
            status_emoji = "🟢"
            status_text = "Complete! ✨"

        # Update status in content
        pattern = rf"({re.escape(quest_name)}\*\*\n.*?\*\*Status:\*\*) [🔴🟡🟢][^|]*"
        replacement = rf"\1 {status_emoji} {status_text}"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return content


def main():
    """Main entry point."""
    print("🔄 Syncing quest progress from GitHub Issues...\n")

    # Fetch issues
    issues = get_issues_via_gh_cli()
    if not issues:
        print("⚠️  No quest issues found. Create them first:")
        print("   python3 create_quest_issues.py")
        return

    print(f"📋 Found {len(issues)} quest issues\n")

    # Sync to QUEST_TRACKER.md
    updated_content = sync_quest_tracker(issues)

    # Write back
    Path("QUEST_TRACKER.md").write_text(updated_content, encoding="utf-8")

    print("✅ QUEST_TRACKER.md synced from GitHub Issues!")
    print("\n🎯 Workflow:")
    print("   1. Open a GitHub Issue")
    print("   2. Check off items in the issue")
    print("   3. This script automatically syncs back to QUEST_TRACKER.md")


if __name__ == "__main__":
    main()
