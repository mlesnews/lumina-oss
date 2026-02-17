#!/usr/bin/env python3
"""Search Moltbook for communities and posts (no auth required for search)"""

import sys

import requests
import urllib3

urllib3.disable_warnings()

MOLTBOOK_IP = "216.150.16.129"


def search(query: str, search_type: str = "all", limit: int = 15):
    """Semantic search on Moltbook"""
    print(f"\n🔍 Searching: '{query}'\n")
    print("-" * 60)

    try:
        response = requests.get(
            f"https://{MOLTBOOK_IP}/api/v1/search",
            params={"q": query, "type": search_type, "limit": limit},
            headers={"Host": "www.moltbook.com"},
            timeout=30,
            verify=False,
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                print("No results found.")
                return []

            for r in results:
                title = r.get("title") or r.get("content", "")[:60]
                author = r.get("author", {}).get("name", "?")
                similarity = r.get("similarity", 0)
                rtype = r.get("type", "?")
                upvotes = r.get("upvotes", 0)
                submolt = r.get("submolt", {}).get("name", "")

                print(f"[{similarity:.0%}] [{rtype}] {title}")
                print(f"       by {author} | {upvotes} upvotes | m/{submolt}")
                print()

            return results
        elif response.status_code == 401:
            print("Search requires authentication on Moltbook.")
            print("We'll need to register first to search.")
            return None
        else:
            print(f"Error {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def list_submolts():
    """List all communities (submolts)"""
    print("\n🦞 Moltbook Communities (Submolts)\n")
    print("-" * 60)

    try:
        response = requests.get(
            f"https://{MOLTBOOK_IP}/api/v1/submolts",
            headers={"Host": "www.moltbook.com"},
            timeout=30,
            verify=False,
        )

        if response.status_code == 200:
            data = response.json()
            submolts = data.get("submolts", [])

            for s in sorted(submolts, key=lambda x: x.get("subscriber_count", 0), reverse=True)[
                :30
            ]:
                name = s.get("name", "?")
                display = s.get("display_name", name)
                members = s.get("subscriber_count", 0)
                desc = (s.get("description") or "")[:50]

                print(f"m/{name} ({members} members)")
                print(f"   {display}: {desc}")
                print()

            return submolts
        elif response.status_code == 401:
            print("Listing submolts requires authentication.")
            return None
        else:
            print(f"Error {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "submolts":
            list_submolts()
        else:
            query = " ".join(sys.argv[1:])
            search(query)
    else:
        # Default searches
        searches = [
            "federated compute pool homelab",
            "local AI inference cluster",
            "ollama distributed",
            "GPU sharing homelab",
        ]
        for q in searches:
            search(q)
            print("\n" + "=" * 60 + "\n")
