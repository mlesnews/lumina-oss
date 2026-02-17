#!/usr/bin/env python3
"""
Moltbook Agent Integration

Connects Jarvis/Lumina to Moltbook - the social network for AI agents.
Enables participation in the AI community, discovery of tools, and sharing insights.

Usage:
    python moltbook_agent.py register --name "Jarvis-Lumina" --description "AI from homelab federation"
    python moltbook_agent.py check-feed
    python moltbook_agent.py post --title "My Title" --content "Content here"
    python moltbook_agent.py search --query "local AI compute"

Tags: @AGENT_NETWORK @MOLTBOOK @AI_COMMUNITY #automation
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests

# Configuration
MOLTBOOK_API = "https://www.moltbook.com/api/v1"
MOLTBOOK_IP = "216.150.16.129"  # Direct IP fallback
CREDENTIALS_PATH = Path.home() / ".config" / "moltbook" / "credentials.json"


def moltbook_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """Make a request to Moltbook with hostname fallback to IP"""
    import urllib3

    urllib3.disable_warnings()

    url = f"{MOLTBOOK_API}{endpoint}"

    try:
        return requests.request(method, url, timeout=15, **kwargs)
    except requests.exceptions.ConnectionError:
        # Fallback to direct IP
        url = f"https://{MOLTBOOK_IP}/api/v1{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Host"] = "www.moltbook.com"
        return requests.request(method, url, headers=headers, verify=False, timeout=15, **kwargs)


def load_credentials() -> Optional[dict]:
    """Load saved credentials"""
    if CREDENTIALS_PATH.exists():
        return json.loads(CREDENTIALS_PATH.read_text())
    return None


def save_credentials(credentials: dict):
    """Save credentials"""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps(credentials, indent=2))
    print(f"Credentials saved to {CREDENTIALS_PATH}")


def get_api_key() -> str:
    """Get API key from credentials or environment"""
    # Check environment first
    if key := os.environ.get("MOLTBOOK_API_KEY"):
        return key

    # Check saved credentials
    if creds := load_credentials():
        return creds.get("api_key", "")

    print("Error: No API key found. Run 'register' first or set MOLTBOOK_API_KEY")
    sys.exit(1)


def register_agent(name: str, description: str):
    """Register a new agent on Moltbook"""
    print(f"\n🦞 Registering agent '{name}' on Moltbook...")

    response = requests.post(
        f"{MOLTBOOK_API}/agents/register",
        headers={"Content-Type": "application/json"},
        json={"name": name, "description": description},
    )

    if response.status_code == 200:
        data = response.json()
        agent = data.get("agent", {})

        print("\n✅ Registration successful!")
        print("\n⚠️  IMPORTANT - Save these credentials:\n")
        print(f"   API Key: {agent.get('api_key')}")
        print(f"   Claim URL: {agent.get('claim_url')}")
        print(f"   Verification Code: {agent.get('verification_code')}")

        # Save credentials
        save_credentials(
            {
                "api_key": agent.get("api_key"),
                "agent_name": name,
                "claim_url": agent.get("claim_url"),
                "verification_code": agent.get("verification_code"),
            }
        )

        print("\n📝 Next steps:")
        print(f"   1. Go to: {agent.get('claim_url')}")
        print(f"   2. Post a tweet with verification code: {agent.get('verification_code')}")
        print("   3. Your agent will be activated!")

        return agent
    else:
        print(f"❌ Registration failed: {response.text}")
        return None


def check_status():
    """Check agent claim status"""
    api_key = get_api_key()

    response = requests.get(
        f"{MOLTBOOK_API}/agents/status", headers={"Authorization": f"Bearer {api_key}"}
    )

    if response.status_code == 200:
        data = response.json()
        status = data.get("status")

        if status == "claimed":
            print("✅ Agent is claimed and active!")
        elif status == "pending_claim":
            creds = load_credentials()
            print("⏳ Agent is pending claim.")
            if creds:
                print(f"   Claim URL: {creds.get('claim_url')}")
        else:
            print(f"Status: {status}")
        return data
    else:
        print(f"❌ Status check failed: {response.text}")
        return None


def get_profile():
    """Get agent profile"""
    api_key = get_api_key()

    response = requests.get(
        f"{MOLTBOOK_API}/agents/me", headers={"Authorization": f"Bearer {api_key}"}
    )

    if response.status_code == 200:
        data = response.json()
        agent = data.get("agent", {})

        print(f"\n🦞 {agent.get('name')}")
        print(f"   Karma: {agent.get('karma', 0)}")
        print(f"   Followers: {agent.get('follower_count', 0)}")
        print(f"   Following: {agent.get('following_count', 0)}")
        print(f"   Status: {'Active' if agent.get('is_active') else 'Inactive'}")
        print(f"   Profile: https://www.moltbook.com/u/{agent.get('name')}")
        return agent
    else:
        print(f"❌ Profile fetch failed: {response.text}")
        return None


def check_feed(sort: str = "hot", limit: int = 10):
    """Check the Moltbook feed"""
    api_key = get_api_key()

    response = requests.get(
        f"{MOLTBOOK_API}/feed?sort={sort}&limit={limit}",
        headers={"Authorization": f"Bearer {api_key}"},
    )

    if response.status_code == 200:
        data = response.json()
        posts = data.get("posts", [])

        print(f"\n🦞 Moltbook Feed ({sort}, {len(posts)} posts)\n")
        print("-" * 60)

        for post in posts:
            title = post.get("title", "No title")[:50]
            author = post.get("author", {}).get("name", "Unknown")
            upvotes = post.get("upvotes", 0)
            submolt = post.get("submolt", {}).get("name", "general")

            print(f"[{upvotes:>3}⬆] {title}")
            print(f"       by {author} in m/{submolt}")
            print()

        return posts
    else:
        print(f"❌ Feed fetch failed: {response.text}")
        return []


def search_posts(query: str, limit: int = 10):
    """Semantic search on Moltbook"""
    api_key = get_api_key()

    response = requests.get(
        f"{MOLTBOOK_API}/search",
        params={"q": query, "limit": limit, "type": "all"},
        headers={"Authorization": f"Bearer {api_key}"},
    )

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])

        print(f"\n🔍 Search: '{query}' ({len(results)} results)\n")
        print("-" * 60)

        for result in results:
            title = result.get("title") or result.get("content", "")[:50]
            author = result.get("author", {}).get("name", "Unknown")
            similarity = result.get("similarity", 0)
            result_type = result.get("type", "post")

            print(f"[{similarity:.0%}] [{result_type}] {title}")
            print(f"         by {author}")
            print()

        return results
    else:
        print(f"❌ Search failed: {response.text}")
        return []


def create_post(title: str, content: str, submolt: str = "general"):
    """Create a post on Moltbook"""
    api_key = get_api_key()

    response = requests.post(
        f"{MOLTBOOK_API}/posts",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"submolt": submolt, "title": title, "content": content},
    )

    if response.status_code == 200:
        data = response.json()
        post = data.get("post", {})

        print("\n✅ Post created!")
        print(f"   URL: https://www.moltbook.com/m/{submolt}/posts/{post.get('id')}")
        return post
    elif response.status_code == 429:
        data = response.json()
        print(f"⏳ Rate limited. Try again in {data.get('retry_after_minutes', '?')} minutes")
        return None
    else:
        print(f"❌ Post failed: {response.text}")
        return None


def list_submolts():
    """List available submolts (communities)"""
    api_key = get_api_key()

    response = requests.get(
        f"{MOLTBOOK_API}/submolts", headers={"Authorization": f"Bearer {api_key}"}
    )

    if response.status_code == 200:
        data = response.json()
        submolts = data.get("submolts", [])

        print(f"\n🦞 Submolts ({len(submolts)} communities)\n")
        print("-" * 60)

        for sub in submolts[:20]:
            name = sub.get("name")
            display = sub.get("display_name", name)
            members = sub.get("subscriber_count", 0)
            desc = (sub.get("description") or "")[:50]

            print(f"m/{name} ({members} members)")
            print(f"   {display}: {desc}")
            print()

        return submolts
    else:
        print(f"❌ List failed: {response.text}")
        return []


def check_name_available(name: str) -> bool:
    """Check if a name is available WITHOUT using a registration attempt"""
    try:
        response = moltbook_request("GET", f"/agents/profile?name={name}")

        if response.status_code == 404:
            return True  # Available
        elif response.status_code == 200:
            return False  # Taken
        else:
            print(f"Unknown status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error checking: {e}")
        return None


def check_names(names: list):
    """Check multiple names for availability"""
    print(f"\n🔍 Checking {len(names)} names...\n")

    available = []
    taken = []

    for name in names:
        is_available = check_name_available(name)
        if is_available is True:
            print(f"  ✅ {name}: AVAILABLE")
            available.append(name)
        elif is_available is False:
            print(f"  ❌ {name}: taken")
            taken.append(name)
        else:
            print(f"  ❓ {name}: unknown")

    if available:
        print(f"\n📝 Available names: {', '.join(available)}")
        print(
            f'   Register with: python moltbook_agent.py register --name "{available[0]}" --description "..."'
        )

    return available


def main():
    parser = argparse.ArgumentParser(description="Moltbook Agent Integration")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Check names (no registration attempt used!)
    check_parser = subparsers.add_parser(
        "check", help="Check if names are available (FREE - no daily limit)"
    )
    check_parser.add_argument("names", nargs="+", help="Names to check")

    # Register
    reg_parser = subparsers.add_parser("register", help="Register new agent (1 per day limit!)")
    reg_parser.add_argument("--name", required=True, help="Agent name")
    reg_parser.add_argument("--description", required=True, help="Agent description")

    # Status
    subparsers.add_parser("status", help="Check claim status")

    # Profile
    subparsers.add_parser("profile", help="Get agent profile")

    # Feed
    feed_parser = subparsers.add_parser("feed", help="Check feed")
    feed_parser.add_argument("--sort", default="hot", choices=["hot", "new", "top"])
    feed_parser.add_argument("--limit", type=int, default=10)

    # Search
    search_parser = subparsers.add_parser("search", help="Search posts")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=10)

    # Post
    post_parser = subparsers.add_parser("post", help="Create a post")
    post_parser.add_argument("--title", required=True, help="Post title")
    post_parser.add_argument("--content", required=True, help="Post content")
    post_parser.add_argument("--submolt", default="general", help="Community to post in")

    # Submolts
    subparsers.add_parser("submolts", help="List communities")

    args = parser.parse_args()

    if args.command == "check":
        check_names(args.names)
    elif args.command == "register":
        register_agent(args.name, args.description)
    elif args.command == "status":
        check_status()
    elif args.command == "profile":
        get_profile()
    elif args.command == "feed":
        check_feed(args.sort, args.limit)
    elif args.command == "search":
        search_posts(args.query, args.limit)
    elif args.command == "post":
        create_post(args.title, args.content, args.submolt)
    elif args.command == "submolts":
        list_submolts()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
