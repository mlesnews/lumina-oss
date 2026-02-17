#!/usr/bin/env python3
"""
RoamWise Server - Web Server for <LOCAL_HOSTNAME>

Serves the hybrid datafeed with WoW Atlas-style pathfinder mapping.

ARCHITECTURE:
- Half 1: SiderAI Wisebase (Knowledge extraction & summarization)
- Half 2: RoamResearch (Lifetime Account - Personal knowledge graph)
- Combined: <LOCAL_HOSTNAME> web frontend

Tags: #ROAMWISE #SIDERAI #WISEBASE #ROAMRESEARCH @JARVIS @LUMINA
"""

import sys
import json
import asyncio
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RoamWiseServer")

# Try to import Flask
try:
    from flask import Flask, jsonify, request, render_template_string
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not available - install: pip install flask flask-cors")

from roamwise_hybrid_datafeed import RoamWiseHybridDatafeed
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# HTML template for WoW Atlas-style visualization
ATLAS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>RoamWise - WoW Atlas Pathfinder</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .atlas-container {
            display: flex;
            height: 100vh;
        }
        .atlas-sidebar {
            width: 300px;
            background: #2d2d2d;
            padding: 20px;
            overflow-y: auto;
        }
        .atlas-map {
            flex: 1;
            background: #1a1a1a;
            position: relative;
            overflow: hidden;
        }
        .zone-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #ffd700;
        }
        .node {
            position: absolute;
            width: 20px;
            height: 20px;
            background: #4a9eff;
            border: 2px solid #fff;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s;
        }
        .node:hover {
            transform: scale(1.5);
            background: #ffd700;
        }
        .node.wisebase {
            background: #4a9eff;
        }
        .node.roamresearch {
            background: #9b59b6;
        }
        .node.hybrid {
            background: #2ecc71;
        }
        .path {
            stroke: #666;
            stroke-width: 2;
            fill: none;
            opacity: 0.5;
        }
        .path.highlight {
            stroke: #ffd700;
            stroke-width: 3;
            opacity: 1;
        }
        .info-panel {
            background: #2d2d2d;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .info-panel h3 {
            margin-top: 0;
            color: #ffd700;
        }
        .search-box {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            background: #1a1a1a;
            border: 1px solid #444;
            color: #fff;
            border-radius: 5px;
        }
        .view-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .view-tab {
            padding: 10px 15px;
            background: #2d2d2d;
            border: 1px solid #444;
            color: #fff;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .view-tab.active {
            background: #4a9eff;
            border-color: #4a9eff;
        }
        .view-tab:hover {
            background: #3d7dd1;
        }
        .view-content {
            display: none;
        }
        .view-content.active {
            display: block;
        }
        #wordcloud-container {
            width: 100%;
            height: 600px;
            background: #1a1a1a;
            border: 1px solid #444;
            border-radius: 5px;
            position: relative;
            overflow: hidden;
        }
        .wordcloud-word {
            cursor: pointer;
            transition: all 0.2s;
        }
        .wordcloud-word:hover {
            opacity: 0.8;
            transform: scale(1.1);
        }
        .wordcloud-controls {
            margin-bottom: 15px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .wordcloud-controls select {
            padding: 8px;
            background: #2d2d2d;
            border: 1px solid #444;
            color: #fff;
            border-radius: 5px;
        }
        .wordcloud-info {
            margin-top: 15px;
            padding: 10px;
            background: #2d2d2d;
            border-radius: 5px;
            font-size: 12px;
        }
        .word-urls {
            margin-top: 10px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .word-url {
            padding: 5px 10px;
            background: #4a9eff;
            color: #fff;
            text-decoration: none;
            border-radius: 3px;
            font-size: 11px;
            transition: all 0.2s;
        }
        .word-url:hover {
            background: #3d7dd1;
        }
        .word-url.database {
            background: #2ecc71;
        }
        .word-url.holocron {
            background: #9b59b6;
        }
        .word-url.video {
            background: #e74c3c;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/wordcloud/1.2.2/wordcloud2.js"></script>
</head>
<body>
    <div class="atlas-container">
        <div class="atlas-sidebar">
            <div class="zone-title">🗺️ RoamWise Atlas</div>
            <div class="view-tabs">
                <div class="view-tab active" data-view="atlas">Atlas</div>
                <div class="view-tab" data-view="wordcloud">Word Cloud</div>
            </div>
            <input type="text" class="search-box" id="search" placeholder="Search nodes...">

            <!-- Atlas View -->
            <div class="view-content active" id="atlas-view">
                <div class="info-panel">
                    <h3>Stats</h3>
                    <p>Nodes: <span id="node-count">0</span></p>
                    <p>Paths: <span id="path-count">0</span></p>
                    <p>Zones: <span id="zone-count">0</span></p>
                </div>
                <div class="info-panel">
                    <h3>Selected Node</h3>
                    <div id="node-info">Click a node to see details</div>
                </div>
            </div>

            <!-- Word Cloud View -->
            <div class="view-content" id="wordcloud-view">
                <div class="wordcloud-controls">
                    <select id="wordcloud-link-type">
                        <option value="database">Database</option>
                        <option value="holocron">Holocron</option>
                        <option value="video_archive">Video Archive</option>
                    </select>
                    <button onclick="loadWordCloud()" style="padding: 8px 15px; background: #4a9eff; border: none; color: #fff; border-radius: 5px; cursor: pointer;">Refresh</button>
                </div>
                <div class="info-panel">
                    <h3>Popularity Word Cloud</h3>
                    <div id="wordcloud-container"></div>
                    <div class="wordcloud-info" id="wordcloud-info">
                        Click on a word to view details
                    </div>
                </div>
            </div>
        </div>
        <div class="atlas-map" id="atlas-map">
            <svg id="paths-svg" style="position: absolute; width: 100%; height: 100%;"></svg>
        </div>
    </div>
    <script>
        const data = {{ data|safe }};
        const nodes = data.nodes || {};
        const paths = data.paths || {};
        const zones = data.zones || {};

        // Render nodes
        function renderNodes() {
            const map = document.getElementById('atlas-map');
            const svg = document.getElementById('paths-svg');

            // Clear existing
            map.querySelectorAll('.node').forEach(n => n.remove());
            svg.innerHTML = '';

            // Render paths
            Object.values(paths).forEach(path => {
                const fromNode = nodes[path.from_node];
                const toNode = nodes[path.to_node];
                if (fromNode && toNode) {
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', fromNode.position[0]);
                    line.setAttribute('y1', fromNode.position[1]);
                    line.setAttribute('x2', toNode.position[0]);
                    line.setAttribute('y2', toNode.position[1]);
                    line.setAttribute('class', 'path');
                    line.setAttribute('data-path-id', path.path_id);
                    svg.appendChild(line);
                }
            });

            // Render nodes
            Object.values(nodes).forEach(node => {
                const nodeEl = document.createElement('div');
                nodeEl.className = `node ${node.zone.toLowerCase()}`;
                nodeEl.style.left = node.position[0] + 'px';
                nodeEl.style.top = node.position[1] + 'px';
                nodeEl.setAttribute('data-node-id', node.node_id);
                nodeEl.setAttribute('title', node.name);
                nodeEl.addEventListener('click', () => selectNode(node));
                map.appendChild(nodeEl);
            });

            // Update stats
            document.getElementById('node-count').textContent = Object.keys(nodes).length;
            document.getElementById('path-count').textContent = Object.values(paths).length;
            document.getElementById('zone-count').textContent = Object.keys(zones).length;
        }

        function selectNode(node) {
            document.getElementById('node-info').innerHTML = `
                <strong>${node.name}</strong><br>
                Type: ${node.node_type}<br>
                Zone: ${node.zone}<br>
                Connections: ${node.connections.length}
            `;

            // Highlight paths
            document.querySelectorAll('.path').forEach(p => p.classList.remove('highlight'));
            node.connections.forEach(connId => {
                document.querySelectorAll(`.path[data-path-id*="${node.node_id}"]`).forEach(p => {
                    p.classList.add('highlight');
                });
            });
        }

        // Search
        document.getElementById('search').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            Object.values(nodes).forEach(node => {
                const nodeEl = document.querySelector(`[data-node-id="${node.node_id}"]`);
                if (nodeEl) {
                    const matches = node.name.toLowerCase().includes(query);
                    nodeEl.style.display = matches ? 'block' : 'none';
                }
            });
        });

        // Initial render
        renderNodes();

        // View switching
        document.querySelectorAll('.view-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const view = tab.getAttribute('data-view');
                document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.view-content').forEach(v => v.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(`${view}-view`).classList.add('active');

                if (view === 'wordcloud') {
                    loadWordCloud();
                }
            });
        });

        // Word Cloud functionality
        let wordcloudData = [];
        let selectedWord = null;

        async function loadWordCloud() {
            try {
                const response = await fetch('/api/wordcloud');
                const data = await response.json();
                wordcloudData = data.words || [];

                // Prepare data for WordCloud2
                const wordList = wordcloudData.map(w => [w.word, w.size]);

                // Clear container
                const container = document.getElementById('wordcloud-container');
                container.innerHTML = '';

                // Generate word cloud
                if (typeof WordCloud !== 'undefined' && wordList.length > 0) {
                    WordCloud(container, {
                        list: wordList,
                        gridSize: Math.round(16 / Math.log(wordList.length + 1)),
                        weightFactor: function(size) {
                            return Math.pow(size, 1.5) * 15;
                        },
                        fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
                        color: function() {
                            // Color based on popularity
                            const word = this.text;
                            const wordData = wordcloudData.find(w => w.word === word);
                            if (wordData) {
                                const popularity = wordData.popularity;
                                if (popularity > 70) return '#ffd700'; // Gold for high popularity
                                if (popularity > 40) return '#4a9eff'; // Blue for medium
                                return '#9b59b6'; // Purple for lower
                            }
                            return '#fff';
                        },
                        rotateRatio: 0.3,
                        rotationSteps: 2,
                        backgroundColor: '#1a1a1a',
                        minSize: 8,
                        drawOutOfBound: false,
                        shrinkToFit: true,
                        click: function(item) {
                            if (item && item[0]) {
                                handleWordClick(item[0]);
                            }
                        }
                    });

                    // Add click handlers to word elements
                    setTimeout(() => {
                        const words = container.querySelectorAll('span, canvas');
                        words.forEach(el => {
                            el.style.cursor = 'pointer';
                            el.addEventListener('click', function() {
                                const word = this.textContent || this.getAttribute('data-word');
                                if (word) {
                                    handleWordClick(word);
                                }
                            });
                        });
                    }, 1000);
                } else {
                    container.innerHTML = '<p style="color: #fff; padding: 20px; text-align: center;">Loading word cloud data...</p>';
                }
            } catch (error) {
                console.error('Error loading word cloud:', error);
                document.getElementById('wordcloud-container').innerHTML = 
                    '<p style="color: #e74c3c; padding: 20px;">Error loading word cloud</p>';
            }
        }

        function handleWordClick(word) {
            selectedWord = wordcloudData.find(w => w.word === word);
            if (!selectedWord) {
                console.warn('Word not found:', word);
                return;
            }

            const linkType = document.getElementById('wordcloud-link-type').value;
            const url = selectedWord.urls[linkType] || selectedWord.urls.database;

            // Update info panel
            const infoPanel = document.getElementById('wordcloud-info');
            const dbUrl = selectedWord.urls.database || '#';
            const holocronUrl = selectedWord.urls.holocron || '#';
            const videoUrl = selectedWord.urls.video_archive || '#';

            infoPanel.innerHTML = `
                <strong style="color: #ffd700; font-size: 18px;">${selectedWord.word}</strong><br>
                <p style="margin: 10px 0;">
                    <strong>Count:</strong> ${selectedWord.count} | 
                    <strong>Popularity:</strong> ${selectedWord.popularity}% | 
                    <strong>Sources:</strong> ${selectedWord.sources}
                </p>
                <div class="word-urls">
                    <a href="${dbUrl}" class="word-url database" target="_blank" onclick="event.stopPropagation(); return true;">📊 Database</a>
                    <a href="${holocronUrl}" class="word-url holocron" target="_blank" onclick="event.stopPropagation(); return true;">💎 Holocron</a>
                    <a href="${videoUrl}" class="word-url video" target="_blank" onclick="event.stopPropagation(); return true;">🎬 Video Archive</a>
                </div>
            `;

            // Navigate to selected URL type if it's valid
            if (url && url !== '#' && !url.includes('undefined')) {
                // Use fetch to check if URL is valid, then navigate
                fetch(url, { method: 'HEAD' })
                    .then(response => {
                        if (response.ok || response.status === 404) {
                            window.open(url, '_blank');
                        }
                    })
                    .catch(() => {
                        // If fetch fails, try opening anyway (might be a relative path)
                        if (url.startsWith('/') || url.startsWith('http')) {
                            window.open(url, '_blank');
                        }
                    });
            }
        }

        // Auto-load word cloud if on wordcloud view
        if (document.querySelector('.view-tab[data-view="wordcloud"]').classList.contains('active')) {
            loadWordCloud();
        }
    </script>
</body>
</html>
"""

if FLASK_AVAILABLE:
    app = Flask(__name__)
    CORS(app)

    # Global datafeed instance
    datafeed = None
    project_root = Path(__file__).parent.parent.parent

    @app.route('/')

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

    @app.route('/')
    def index():
        """Main atlas view"""
        try:
            # Initialize datafeed if needed
            global datafeed
            if not datafeed:
                datafeed = RoamWiseHybridDatafeed(project_root)

            # Get initial data (non-blocking, will load async in frontend)
            return render_template_string(ATLAS_TEMPLATE, data=json.dumps({
                "nodes": {},
                "paths": {},
                "zones": {}
            }))
        except Exception as e:
            logger.error(f"Error in index: {e}", exc_info=True)
            return render_template_string(ATLAS_TEMPLATE, data=json.dumps({
                "nodes": {},
                "paths": {},
                "zones": {},
                "error": str(e)
            }))
    @app.route('/api/status')
    def status():
        """Get system status"""
        return jsonify({
            "status": "operational",
            "domain": "<LOCAL_HOSTNAME>",
            "architecture": {
                "half_1": "SiderAI Wisebase - Knowledge extraction & summarization",
                "half_2": "RoamResearch - Personal knowledge graph (Lifetime Account)",
                "frontend": "<LOCAL_HOSTNAME> web portal"
            },
            "sources": {
                "siderai_wisebase": "ready",
                "roamresearch": "ready"
            },
            "pathfinder": "ready"
        })

    @app.route('/api/data')
    async def get_data():
        """Get all data"""
        global datafeed
        if not datafeed:
            datafeed = RoamWiseHybridDatafeed()

        results = await datafeed.fetch_all_data()

        # Convert to dict format for JSON
        nodes_dict = {nid: node.to_dict() for nid, node in datafeed.pathfinder.nodes.items()}
        paths_dict = {pid: path.to_dict() for pid, path in datafeed.pathfinder.paths.items()}

        return jsonify({
            "nodes": nodes_dict,
            "paths": paths_dict,
            "zones": datafeed.pathfinder.zones,
            "stats": {
                "node_count": len(nodes_dict),
                "path_count": len(paths_dict),
                "zone_count": len(datafeed.pathfinder.zones)
            }
        })

    @app.route('/api/path')
    async def find_path():
        """Find path between nodes"""
        global datafeed
        if not datafeed:
            datafeed = RoamWiseHybridDatafeed()

        from_query = request.args.get('from', '')
        to_query = request.args.get('to', '')

        if not from_query or not to_query:
            return jsonify({"error": "Missing 'from' or 'to' parameter"}), 400

        path_result = await datafeed.get_path(from_query, to_query)
        return jsonify(path_result)

    @app.route('/api/zone/<zone_name>')
    async def get_zone(zone_name: str):
        """Get zone map"""
        global datafeed
        if not datafeed:
            datafeed = RoamWiseHybridDatafeed()

        zone_map = datafeed.pathfinder.get_zone_map(zone_name)
        return jsonify(zone_map)

    @app.route('/api/wordcloud')
    async def get_wordcloud():
        """Get word cloud data with popularity and URLs"""
        global datafeed
        if not datafeed:
            datafeed = RoamWiseHybridDatafeed(project_root)

        # Fetch all data
        results = await datafeed.fetch_all_data()

        # Extract text from all nodes and metadata
        all_text = []
        word_sources = {}  # Track which sources contain each word

        # Process nodes
        for node_id, node in datafeed.pathfinder.nodes.items():
            node_text = f"{node.name} {node.node_type} {node.zone}"
            if node.metadata:
                node_text += f" {json.dumps(node.metadata)}"
            all_text.append(node_text)

            # Track sources for URL mapping
            metadata = node.metadata or {}
            source = metadata.get('source', 'unknown')
            node_data = {
                'type': 'node',
                'id': node_id,
                'name': node.name,
                'source': source,
                'zone': node.zone
            }

            # Extract words and map to sources
            words = _extract_words(node_text)
            for word in words:
                if word not in word_sources:
                    word_sources[word] = []
                word_sources[word].append(node_data)

        # Process raw data items
        if 'data' in results:
            for item in results.get('data', []):
                item_text = f"{item.get('title', '')} {item.get('name', '')} {item.get('content', '')}"
                all_text.append(item_text)

                source = item.get('source', 'unknown')
                item_id = item.get('id', 'unknown')
                item_data = {
                    'type': 'data',
                    'id': item_id,
                    'title': item.get('title', item.get('name', '')),
                    'source': source
                }

                words = _extract_words(item_text)
                for word in words:
                    if word not in word_sources:
                        word_sources[word] = []
                    word_sources[word].append(item_data)

        # Count word frequencies
        all_words = []
        for text in all_text:
            all_words.extend(_extract_words(text))

        word_counts = Counter(all_words)

        # Filter common stop words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'from', 'as', 'it', 'its', 'they', 'them', 'their', 'there', 'then', 'than', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'some', 'any', 'no', 'not', 'only', 'just', 'more', 'most', 'very', 'too', 'so', 'such', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}

        # Filter words
        filtered_counts = {
            word: count for word, count in word_counts.items()
            if len(word) >= 3 and word.lower() not in stop_words and count >= 2
        }

        # Get top words by frequency
        top_words = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)[:100]

        # Build word cloud data with URLs
        wordcloud_data = []
        project_root = Path(__file__).parent.parent.parent

        for word, count in top_words:
            # Calculate popularity score (0-100)
            max_count = top_words[0][1] if top_words else 1
            popularity = int((count / max_count) * 100)

            # Get sources for this word
            sources = word_sources.get(word, [])

            # Build URLs
            urls = {
                'database': f"/api/data?search={word}",
                'holocron': f"/api/holocron?query={word}",
                'video_archive': f"/api/videos?search={word}"
            }

            # Try to find actual file paths
            if sources:
                first_source = sources[0]
                source_type = first_source.get('type', 'unknown')
                source_id = first_source.get('id', '')
                source_name = first_source.get('name') or first_source.get('title', '')

                # Holocron path
                holocron_dir = project_root / "data" / "holocron"
                if holocron_dir.exists():
                    # Try to find matching holocron files
                    holocron_files = list(holocron_dir.rglob(f"*{word}*.md")) + list(holocron_dir.rglob(f"*{word}*.json"))
                    if holocron_files:
                        urls['holocron'] = f"/data/holocron/{holocron_files[0].relative_to(project_root)}"

                # Video archive path
                video_dir = project_root / "data" / "videos"
                if video_dir.exists():
                    video_files = list(video_dir.rglob(f"*{word}*"))
                    if video_files:
                        urls['video_archive'] = f"/data/videos/{video_files[0].relative_to(project_root)}"

                # Database path
                roamwise_dir = project_root / "data" / "roamwise"
                if roamwise_dir.exists():
                    db_files = list(roamwise_dir.rglob(f"*{word}*.json"))
                    if db_files:
                        urls['database'] = f"/data/roamwise/{db_files[0].relative_to(project_root)}"

            wordcloud_data.append({
                'word': word,
                'count': count,
                'popularity': popularity,
                'size': 10 + (popularity / 10),  # Size for word cloud
                'urls': urls,
                'sources': len(sources)
            })

        return jsonify({
            'words': wordcloud_data,
            'total_words': len(wordcloud_data),
            'max_count': top_words[0][1] if top_words else 0
        })

    @app.route('/api/holocron')
    def search_holocron():
        try:
            """Search holocron archive"""
            query = request.args.get('query', '')
            holocron_dir = project_root / "data" / "holocron"

            results = []
            if holocron_dir.exists() and query:
                # Search for matching files
                for file_path in holocron_dir.rglob(f"*{query}*"):
                    if file_path.is_file() and file_path.suffix in ['.md', '.json', '.txt']:
                        relative_path = file_path.relative_to(project_root)
                        results.append({
                            'name': file_path.name,
                            'path': str(relative_path).replace('\\', '/'),
                            'url': f"/data/holocron/{relative_path.name}",
                            'type': 'holocron'
                        })

            return jsonify({
                'query': query,
                'results': results[:50],  # Limit to 50 results
                'count': len(results)
            })

        except Exception as e:
            logger.error(f"Error in search_holocron: {e}", exc_info=True)
            raise
    @app.route('/api/videos')
    def search_videos():
        try:
            """Search video archive"""
            query = request.args.get('search', '')
            video_dir = project_root / "data" / "videos"

            results = []
            if video_dir.exists() and query:
                # Search for matching files
                for file_path in video_dir.rglob(f"*{query}*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(project_root)
                        results.append({
                            'name': file_path.name,
                            'path': str(relative_path).replace('\\', '/'),
                            'url': f"/data/videos/{relative_path.name}",
                            'type': 'video',
                            'extension': file_path.suffix
                        })

            return jsonify({
                'query': query,
                'results': results[:50],  # Limit to 50 results
                'count': len(results)
            })

        except Exception as e:
            logger.error(f"Error in search_videos: {e}", exc_info=True)
            raise
    @app.route('/data/<path:filepath>')
    def serve_data(filepath: str):
        """Serve data files (holocron, videos, etc.)"""
        try:
            data_path = project_root / "data" / filepath
            if data_path.exists() and data_path.is_file():
                # Security: ensure path is within data directory
                if not str(data_path.resolve()).startswith(str(project_root.resolve())):
                    return jsonify({"error": "Invalid path"}), 403

                # Return file content based on type
                if data_path.suffix == '.json':
                    with open(data_path, 'r', encoding='utf-8') as f:
                        return jsonify(json.load(f))
                elif data_path.suffix in ['.md', '.txt']:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        from flask import Response
                        return Response(f.read(), mimetype='text/plain')
                else:
                    from flask import send_file
                    return send_file(str(data_path))
            else:
                return jsonify({"error": "File not found"}), 404
        except Exception as e:
            logger.error(f"Error serving file {filepath}: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500


def _extract_words(text: str) -> List[str]:
    """Extract words from text, removing special characters"""
    if not text:
        return []

    # Convert to lowercase and extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return words


def run_server(host='localhost', port=5000, debug=True):
    """Run the server"""
    # Note: For local domain, you'll need to add to hosts file:
    # 127.0.0.1 <LOCAL_HOSTNAME>
    # Or use localhost directly
    logger.info(f"🌐 Starting RoamWise server")
    logger.info(f"   Architecture: SiderAI Wisebase + RoamResearch")
    logger.info(f"   Access at: http://<LOCAL_HOSTNAME>:{port}")
    logger.info(f"   Or: http://localhost:{port}")
    logger.info(f"   Or: http://127.0.0.1:{port}")
    logger.info(f"   For custom domain, add to hosts file:")
    logger.info(f"     127.0.0.1    <LOCAL_HOSTNAME>")
    logger.info(f"     127.0.0.1    <LOCAL_HOSTNAME>")
    logger.info(f"   Run: powershell -ExecutionPolicy Bypass -File scripts/python/roamwise_setup_hosts.ps1")
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RoamWise Server")
    parser.add_argument('--host', default='localhost', help='Host (default: localhost, or use <LOCAL_HOSTNAME> if configured)')
    parser.add_argument('--port', type=int, default=5000, help='Port')
    parser.add_argument('--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()
    run_server(args.host, args.port, args.debug)

else:
    logger.error("Flask not available - cannot run server")
    logger.error("Install: pip install flask flask-cors")

