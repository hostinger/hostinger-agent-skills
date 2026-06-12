#!/usr/bin/env python3
"""
Check Hostinger API changelog for updates that may require skill documentation changes.

Monitors the Hostinger API changelog on GitHub and detects significant updates
that could affect the agent skills documentation.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

CHANGELOG_URL = "https://api.github.com/repos/hostinger/api/commits"
CHANGELOG_FILE_PATH = "CHANGELOG.md"
TRACKING_DIR = Path("tracking")
LAST_CHECK_FILE = TRACKING_DIR / "last-check.json"
PENDING_UPDATES_FILE = TRACKING_DIR / "pending-updates.json"

# Keywords that indicate significant API changes
SIGNIFICANT_KEYWORDS = [
    "new endpoint",
    "deprecated",
    "breaking change",
    "removed",
    "new feature",
    "new parameter",
    "changed",
    "updated",
    "added",
    "security",
    "rate limit",
    "authentication",
    "billing",
    "dns",
    "domain",
    "hosting",
    "vps",
    "reach",
    "email",
    "firewall",
    "docker",
    "snapshot",
    "backup",
    "template",
    "database",
    "subdomain",
    "wordpress",
    "nodejs",
    "ecommerce",
    "store",
    "horizons",
    "verification",
]

# Map API areas to skills
SKILL_MAPPING = {
    "billing": "billing",
    "catalog": "billing",
    "payment": "billing",
    "subscription": "billing",
    "order": "billing",
    "dns": "dns",
    "zone": "dns",
    "snapshot": "dns",
    "domain": "domains",
    "whois": "domains",
    "nameserver": "domains",
    "forwarding": "domains",
    "portfolio": "domains",
    "hosting": "hosting",
    "website": "hosting",
    "datacenter": "hosting",
    "database": "hosting",
    "subdomain": "hosting",
    "parked": "hosting",
    "nodejs": "hosting",
    "wordpress": "hosting",
    "vps": "vps",
    "virtual machine": "vps",
    "docker": "vps",
    "firewall": "vps",
    "ssh": "vps",
    "public key": "vps",
    "template": "vps",
    "backup": "vps",
    "recovery": "vps",
    "monarx": "vps",
    "malware": "vps",
    "ptr": "vps",
    "reach": "reach",
    "contact": "reach",
    "segment": "reach",
    "email marketing": "reach",
    "ecommerce": "ecommerce",
    "e-commerce": "ecommerce",
    "store": "ecommerce",
    "sales channel": "ecommerce",
    "horizons": "horizons",
    "website builder": "horizons",
    "verification": "domains",
    "verifier": "domains",
}


def get_last_check_time():
    """Get the timestamp of the last check."""
    if LAST_CHECK_FILE.exists():
        data = json.loads(LAST_CHECK_FILE.read_text())
        return data.get("last_check")
    return None


def save_check_time():
    """Save the current check timestamp."""
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "skills_checked": [
            "billing",
            "dns",
            "domains",
            "ecommerce",
            "hosting",
            "horizons",
            "reach",
            "vps",
        ],
    }
    LAST_CHECK_FILE.write_text(json.dumps(data, indent=2))


def check_changelog_updates(since=None):
    """Check GitHub commits to the Hostinger API changelog."""
    headers = {"Accept": "application/vnd.github.v3+json"}

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    params = {"path": CHANGELOG_FILE_PATH, "per_page": 20}
    if since:
        params["since"] = since

    try:
        response = requests.get(CHANGELOG_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching changelog: {e}", file=sys.stderr)
        return []


def classify_update(message):
    """Classify a commit message and determine affected skills."""
    message_lower = message.lower()

    is_significant = any(kw in message_lower for kw in SIGNIFICANT_KEYWORDS)

    affected_skills = set()
    for keyword, skill in SKILL_MAPPING.items():
        if keyword in message_lower:
            affected_skills.add(skill)

    return is_significant, list(affected_skills)


def main():
    last_check = get_last_check_time()
    print(f"Last check: {last_check or 'never'}")

    commits = check_changelog_updates(since=last_check)
    print(f"Found {len(commits)} changelog commits since last check")

    updates = []
    for commit in commits:
        message = commit.get("commit", {}).get("message", "")
        date = commit.get("commit", {}).get("author", {}).get("date", "")
        sha = commit.get("sha", "")[:8]

        is_significant, affected_skills = classify_update(message)

        if is_significant:
            updates.append(
                {
                    "sha": sha,
                    "date": date,
                    "message": message.split("\n")[0][:200],
                    "affected_skills": affected_skills,
                }
            )

    # Save results
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    PENDING_UPDATES_FILE.write_text(json.dumps(updates, indent=2))
    save_check_time()

    # Set GitHub Actions outputs
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"updates_found={'true' if updates else 'false'}\n")
            f.write(f"update_count={len(updates)}\n")

    if updates:
        print(f"\nFound {len(updates)} significant updates:")
        for update in updates:
            skills = ", ".join(update["affected_skills"]) or "general"
            print(f"  [{update['sha']}] {update['message']} (affects: {skills})")
    else:
        print("\nNo significant updates found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
