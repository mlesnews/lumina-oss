#!/usr/bin/env python3
"""
SYPHON YouTube RSS Sweep - Automated transcript extraction.
Reads channel config, pulls RSS feeds, extracts transcripts, saves results.
Designed to run as NAS cron job at low-traffic hours.

Self-healing: retries flaky RSS, re-resolves channel IDs via @handle,
auto-updates channels JSON when a fix is found.

Tags: #SYPHON #YOUTUBE #SPARKS @JARVIS
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("ERROR: youtube-transcript-api not installed", file=sys.stderr)
    sys.exit(1)


NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'media': 'http://search.yahoo.com/mrss/',
    'yt': 'http://www.youtube.com/xml/schemas/2015',
}

RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
HANDLE_URL = "https://www.youtube.com/@{}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def load_channels(config_path: str, min_priority: str = "low") -> tuple[list, dict]:
    """Load channels from config file, flatten all categories.
    Filters by minimum priority level: high, medium, or low.
    Returns (channels_list, raw_config) for potential write-back."""
    with open(config_path) as f:
        config = json.load(f)

    priority_rank = {"high": 0, "medium": 1, "low": 2}
    min_rank = priority_rank.get(min_priority, 2)

    channels = []
    for category, channel_list in config.get("channels", {}).items():
        if not isinstance(channel_list, list):
            continue
        for ch in channel_list:
            ch_priority = ch.get("priority", "low")
            if priority_rank.get(ch_priority, 2) <= min_rank:
                ch["category"] = category
                channels.append(ch)
    return channels, config


def fetch_rss_videos(channel_id: str, cutoff: datetime,
                     retries: int = 3, retry_delay: float = 2.0) -> list | None:
    """Fetch recent videos from a channel's RSS feed.
    Returns list of videos on success, None on persistent failure."""
    url = RSS_URL.format(channel_id)
    req = urllib.request.Request(url, headers={'User-Agent': UA})

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    tree = ET.parse(resp)
                    break
        except urllib.error.HTTPError as e:
            if e.code in (404, 500) and attempt < retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            return None
    else:
        return None

    videos = []
    for entry in tree.findall('.//atom:entry', NS):
        title = entry.find('atom:title', NS)
        published = entry.find('atom:published', NS)
        vid_el = entry.find('yt:videoId', NS)
        link_el = entry.find('atom:link', NS)

        if title is None or published is None or vid_el is None:
            continue

        try:
            pub_date = datetime.fromisoformat(published.text.replace('Z', '+00:00'))
            if pub_date >= cutoff:
                desc = ""
                media_group = entry.find('media:group', NS)
                if media_group is not None:
                    desc_el = media_group.find('media:description', NS)
                    if desc_el is not None and desc_el.text:
                        desc = desc_el.text[:500]

                videos.append({
                    "title": title.text,
                    "published": published.text[:10],
                    "video_id": vid_el.text,
                    "url": link_el.get('href', '') if link_el is not None else '',
                    "description": desc,
                })
        except (ValueError, TypeError):
            continue

    return videos


def resolve_channel_id(handle: str) -> str | None:
    """Scrape a YouTube @handle page to extract the current externalId."""
    url = HANDLE_URL.format(handle)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        match = re.search(r'"externalId":"(UC[A-Za-z0-9_-]+)"', html)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def heal_channel(ch: dict, config: dict, config_path: str) -> str | None:
    """Attempt to heal a broken channel ID via @handle resolution.
    Updates the config file if a new working ID is found.
    Returns the new ID or None."""
    handle = ch.get("handle")
    if not handle:
        return None

    new_id = resolve_channel_id(handle)
    if not new_id or new_id == ch["id"]:
        return None

    # Verify the new ID actually works
    url = RSS_URL.format(new_id)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                return None
    except Exception:
        return None

    # Update in-memory
    old_id = ch["id"]
    ch["id"] = new_id

    # Update the config file
    try:
        for cat_channels in config.get("channels", {}).values():
            for entry in cat_channels:
                if entry.get("id") == old_id and entry.get("name") == ch["name"]:
                    entry["id"] = new_id
                    break

        config["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write('\n')
    except Exception:
        pass  # Non-fatal: sweep continues with the new ID in memory

    return new_id


def fetch_transcript(video_id: str) -> str | None:
    """Fetch transcript for a video, return None on failure.
    Handles IP blocks gracefully — logs once and skips further attempts."""
    global _ip_blocked
    if _ip_blocked:
        return None
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id)
        return ' '.join(s.text for s in transcript.snippets)
    except Exception as e:
        if "IpBlocked" in type(e).__name__ or "IpBlocked" in str(e):
            _ip_blocked = True
            print("  WARNING: IP blocked by YouTube — transcripts disabled for this sweep",
                  file=sys.stderr)
        return None

_ip_blocked = False


def main():
    parser = argparse.ArgumentParser(description="SYPHON YouTube RSS Sweep")
    parser.add_argument("--channels", required=True, help="Path to youtube_channels.json")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--lookback-days", type=int, default=7)
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    parser.add_argument("--heal", action="store_true", default=True,
                        help="Auto-heal broken channel IDs (default: on)")
    parser.add_argument("--no-heal", dest="heal", action="store_false",
                        help="Disable auto-healing")
    parser.add_argument("--priority", choices=["high", "medium", "low"],
                        default="medium",
                        help="Minimum priority to sweep (default: medium)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.lookback_days)
    channels, config = load_channels(args.channels, args.priority)

    # Read retry config from the config file
    sweep_cfg = config.get("sweep_config", {})
    retries = sweep_cfg.get("rss_retries", 3)
    retry_delay = sweep_cfg.get("rss_retry_delay_seconds", 2.0)

    print(f"SYPHON YouTube Sweep: {len(channels)} channels, "
          f"{args.lookback_days}d lookback, heal={'on' if args.heal else 'off'}")

    all_videos = []
    success = 0
    failed = 0
    total_words = 0
    healed = []
    still_broken = []

    for ch in channels:
        # Resolve ID from handle if not present
        if not ch.get("id") and ch.get("handle"):
            resolved = resolve_channel_id(ch["handle"])
            if resolved:
                ch["id"] = resolved
                # Write back to config
                try:
                    for cat_channels in config.get("channels", {}).values():
                        if not isinstance(cat_channels, list):
                            continue
                        for entry in cat_channels:
                            if entry.get("handle") == ch.get("handle") and not entry.get("id"):
                                entry["id"] = resolved
                except Exception:
                    pass
            else:
                still_broken.append(ch["name"])
                continue
            time.sleep(args.delay)

        videos = fetch_rss_videos(ch["id"], cutoff, retries, retry_delay)

        # Self-healing: if RSS failed and channel has a handle, try to re-resolve
        if videos is None and args.heal:
            new_id = heal_channel(ch, config, args.channels)
            if new_id:
                print(f"  HEALED {ch['name']}: {ch['id'][:12]}... (via @{ch.get('handle','')})")
                healed.append(ch["name"])
                videos = fetch_rss_videos(new_id, cutoff, retries, retry_delay)
            else:
                still_broken.append(ch["name"])
                continue
        elif videos is None:
            still_broken.append(ch["name"])
            continue

        if not videos:
            continue  # RSS worked but no recent videos

        print(f"  {ch['name']}: {len(videos)} videos")

        for vid in videos:
            transcript = fetch_transcript(vid["video_id"])
            wc = len(transcript.split()) if transcript else 0

            all_videos.append({
                "channel": ch["name"],
                "category": ch["category"],
                **vid,
                "transcript": transcript,
                "word_count": wc,
                "has_transcript": transcript is not None,
            })

            if transcript:
                success += 1
                total_words += wc
            else:
                failed += 1

            time.sleep(args.delay)

    # Report healing results
    if healed:
        print(f"\n  Auto-healed {len(healed)} channels: {', '.join(healed)}")
    if still_broken:
        print(f"  Still broken ({len(still_broken)}): {', '.join(still_broken)}")
        print(f"  Tip: add 'handle' field to channels JSON for auto-healing")

    # Save results
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    output_file = output_dir / f"youtube_sweep_{timestamp}.json"

    result = {
        "sweep_date": datetime.now(timezone.utc).isoformat(),
        "lookback_days": args.lookback_days,
        "channels_scanned": len(channels),
        "channels_broken": len(still_broken),
        "channels_healed": len(healed),
        "total_videos": len(all_videos),
        "transcripts_obtained": success,
        "transcripts_failed": failed,
        "total_words": total_words,
        "healed_channels": healed,
        "broken_channels": still_broken,
        "videos": all_videos,
    }

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save any resolved IDs back to config
    try:
        config["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with open(args.channels, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write('\n')
    except Exception:
        pass

    print(f"\nDone: {success} transcripts, {total_words:,} words -> {output_file.name}")

    # Also update the "latest" file
    latest = output_dir / "youtube_sweep_latest.json"
    with open(latest, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
