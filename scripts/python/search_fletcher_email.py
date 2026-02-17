"""
Quick script to search for latest Fletcher email
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_gmail_integration import LUMINAGmailIntegration

    gmail = LUMINAGmailIntegration(project_root)

    # Search for Fletcher emails (most recent first)
    print("Searching for Fletcher emails...")
    emails = gmail.search_emails("Fletcher", max_results=5)

    if emails:
        print(f"\n✓ Found {len(emails)} email(s)")
        print("\n" + "="*80)
        print("MOST RECENT FLETCHER EMAIL:")
        print("="*80)

        latest = emails[0]
        print(f"\nFrom: {latest.get('from', 'N/A')}")
        print(f"Subject: {latest.get('subject', 'N/A')}")
        print(f"Date: {latest.get('date', 'N/A')}")
        print(f"\nBody Preview:")
        body = latest.get('body', latest.get('text_body', ''))
        print(body[:500] + "..." if len(body) > 500 else body)

        # Save full email details
        output_file = project_root / "data" / "lumina_gmail" / "latest_fletcher_email.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(latest, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n✓ Full email saved to: {output_file}")
    else:
        print("⚠ No emails found with 'Fletcher'")
        print("\nTrying alternative search queries...")

        # Try more specific queries
        queries = [
            "from:fletcher",
            "brian fletcher",
            "fletcher's heating"
        ]

        for query in queries:
            emails = gmail.search_emails(query, max_results=3)
            if emails:
                print(f"\n✓ Found {len(emails)} with query: {query}")
                latest = emails[0]
                print(f"  From: {latest.get('from', 'N/A')}")
                print(f"  Subject: {latest.get('subject', 'N/A')}")
                print(f"  Date: {latest.get('date', 'N/A')}")
                break

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
