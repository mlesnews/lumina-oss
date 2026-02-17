#!/usr/bin/env python3
"""
Browser-Based YouTube Data Extractor

Extracts YouTube watch history and recommendations directly from browser.
This script can be run in the browser console or as a bookmarklet.

Usage:
1. Open YouTube in your browser
2. Open Developer Console (F12)
3. Copy and paste this script
4. Run: extractYouTubeData()
5. Save the output JSON

Tags: #YOUTUBE #EXTRACTION #BROWSER @JARVIS @LUMINA
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
logger = logging.getLogger("extract_youtube_browser_data")


# Browser console script (JavaScript)
BROWSER_SCRIPT = """
// YouTube Data Extractor - Browser Console Script
// Run this in YouTube's browser console (F12)

async function extractYouTubeData() {
    console.log("🚀 Starting YouTube data extraction...");

    const data = {
        extracted_at: new Date().toISOString(),
        watch_history: [],
        recommendations: [],
        subscriptions: []
    };

    // Extract watch history from page
    try {
        // Navigate to watch history
        if (window.location.href !== 'https://www.youtube.com/feed/history') {
            console.log("⚠️  Please navigate to: https://www.youtube.com/feed/history");
            console.log("   Then run this script again");
            return;
        }

        // Wait for content to load
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Extract video elements
        const videoElements = document.querySelectorAll('ytd-video-renderer, ytd-grid-video-renderer');
        console.log(`📺 Found ${videoElements.length} videos`);

        videoElements.forEach((element, index) => {
            try {
                const titleElement = element.querySelector('#video-title, a#video-title');
                const channelElement = element.querySelector('#channel-name a, ytd-channel-name a');
                const timeElement = element.querySelector('#metadata-line span, ytd-video-meta-block span');
                const thumbnailElement = element.querySelector('img');

                if (titleElement) {
                    const video = {
                        index: index + 1,
                        title: titleElement.textContent.trim(),
                        url: titleElement.href || '',
                        channel: channelElement ? channelElement.textContent.trim() : 'Unknown',
                        watched_at: timeElement ? timeElement.textContent.trim() : 'Unknown',
                        thumbnail: thumbnailElement ? thumbnailElement.src : '',
                        extracted_at: new Date().toISOString()
                    };

                    data.watch_history.push(video);
                }
            } catch (e) {
                console.warn(`⚠️  Error extracting video ${index}:`, e);
            }
        });

        console.log(`✅ Extracted ${data.watch_history.length} videos from history`);
    } catch (e) {
        console.error("❌ Error extracting watch history:", e);
    }

    // Extract recommendations
    try {
        // Scroll to load more recommendations
        console.log("📜 Scrolling to load recommendations...");
        for (let i = 0; i < 5; i++) {
            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        // Extract recommended videos
        const recommendedElements = document.querySelectorAll('ytd-video-renderer, ytd-grid-video-renderer');
        console.log(`📺 Found ${recommendedElements.length} recommended videos`);

        recommendedElements.forEach((element, index) => {
            try {
                const titleElement = element.querySelector('#video-title, a#video-title');
                const channelElement = element.querySelector('#channel-name a, ytd-channel-name a');
                const viewsElement = element.querySelector('#metadata-line span, ytd-video-meta-block span');
                const thumbnailElement = element.querySelector('img');

                if (titleElement && !data.watch_history.some(v => v.url === titleElement.href)) {
                    const video = {
                        index: index + 1,
                        title: titleElement.textContent.trim(),
                        url: titleElement.href || '',
                        channel: channelElement ? channelElement.textContent.trim() : 'Unknown',
                        views: viewsElement ? viewsElement.textContent.trim() : 'Unknown',
                        thumbnail: thumbnailElement ? thumbnailElement.src : '',
                        extracted_at: new Date().toISOString()
                    };

                    data.recommendations.push(video);
                }
            } catch (e) {
                console.warn(`⚠️  Error extracting recommendation ${index}:`, e);
            }
        });

        console.log(`✅ Extracted ${data.recommendations.length} recommendations`);
    } catch (e) {
        console.error("❌ Error extracting recommendations:", e);
    }

    // Output JSON
    const jsonOutput = JSON.stringify(data, null, 2);
    console.log("=".repeat(80));
    console.log("📄 EXTRACTED DATA (Copy this JSON):");
    console.log("=".repeat(80));
    console.log(jsonOutput);
    console.log("=".repeat(80));

    // Create download link
    const blob = new Blob([jsonOutput], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `youtube_data_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);

    console.log("✅ Data downloaded!");
    console.log(`📊 Summary:`);
    console.log(`   Watch History: ${data.watch_history.length} videos`);
    console.log(`   Recommendations: ${data.recommendations.length} videos`);
    console.log(`   Total: ${data.watch_history.length + data.recommendations.length} videos`);

    return data;
}

// Run extraction
extractYouTubeData();
"""

# Python wrapper for processing extracted data
def process_browser_extracted_data(json_file_path: str, output_dir: str):
    try:
        """Process data extracted from browser"""
        import json
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to format expected by processor
        watch_history = []
        for video in data.get('watch_history', []):
            watch_history.append({
                'title': video.get('title', ''),
                'channel': video.get('channel', ''),
                'url': video.get('url', ''),
                'watched_at': video.get('watched_at', ''),
                'video_id': video.get('url', '').split('v=')[-1].split('&')[0] if 'v=' in video.get('url', '') else ''
            })

        recommendations = []
        for video in data.get('recommendations', []):
            recommendations.append({
                'title': video.get('title', ''),
                'channel': video.get('channel', ''),
                'url': video.get('url', ''),
                'views': video.get('views', ''),
                'video_id': video.get('url', '').split('v=')[-1].split('&')[0] if 'v=' in video.get('url', '') else ''
            })

        # Save formatted data
        history_file = output_path / "watch_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(watch_history, f, indent=2, default=str)

        rec_file = output_path / "recommendations.json"
        with open(rec_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, default=str)

        print(f"✅ Processed browser-extracted data")
        print(f"   Watch History: {len(watch_history)} videos")
        print(f"   Recommendations: {len(recommendations)} videos")
        print(f"   Saved to: {output_path}")

        return watch_history, recommendations


    except Exception as e:
        logger.error(f"Error in process_browser_extracted_data: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("=" * 80)
        print("📺 YOUTUBE BROWSER DATA EXTRACTOR")
        print("=" * 80)
        print()
        print("Browser Console Script:")
        print("-" * 80)
        print(BROWSER_SCRIPT)
        print("-" * 80)
        print()
        print("Usage:")
        print("  1. Open YouTube in your browser")
        print("  2. Navigate to: https://www.youtube.com/feed/history")
        print("  3. Open Developer Console (F12)")
        print("  4. Copy and paste the script above")
        print("  5. Run: extractYouTubeData()")
        print("  6. Save the downloaded JSON file")
        print()
        print("Then process the extracted data:")
        print("  python extract_youtube_browser_data.py <extracted_file.json>")
        print()
    else:
        # Process extracted file
        extracted_file = Path(sys.argv[1])
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "data" / "youtube_30day"

        process_browser_extracted_data(extracted_file, output_dir)

        print()
        print("✅ Now run the processor:")
        print(f"   python scripts/python/youtube_30day_instruction_processor.py --process")
