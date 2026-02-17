#!/usr/bin/env python3
"""
EWTN AI Interface

Creates an AI interface that can interact with syphoned EWTN content.
This allows our AI to "talk" with EWTN content by querying the extracted data.

Usage:
    python ewtn_ai_interface.py --query "What does EWTN say about artificial intelligence?"
    python ewtn_ai_interface.py --interactive
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
logger = get_logger("ewtn_ai_interface")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class EWTNAIInterface:
    """AI interface for querying syphoned EWTN content"""

    def __init__(self, data_dir: Path = None, project_root: Path = None):
        """
        Initialize EWTN AI Interface.

        Args:
            data_dir: Directory containing syphoned EWTN data
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        self.data_dir = data_dir or (self.project_root / "data" / "syphon" / "ewtn")
        self.logger = get_logger("EWTNAIInterface")

        # Load all syphoned data
        self.content_index: List[Dict] = []
        self.load_content()

    def load_content(self) -> None:
        """Load all syphoned EWTN content"""
        self.logger.info(f"Loading EWTN content from {self.data_dir}")

        if not self.data_dir.exists():
            self.logger.warning(f"Data directory not found: {self.data_dir}")
            return

        # Load all JSON files
        json_files = list(self.data_dir.glob("ewtn_*.json"))

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Index the content
                    self.content_index.append({
                        "file": str(json_file),
                        "data_id": data.get("data_id", ""),
                        "url": data.get("source_id", ""),
                        "title": data.get("metadata", {}).get("title", ""),
                        "content": data.get("content", ""),
                        "metadata": data.get("metadata", {}),
                        "actionable_items": data.get("actionable_items", []),
                        "intelligence": data.get("intelligence", []),
                        "extracted_at": data.get("extracted_at", "")
                    })
            except Exception as e:
                self.logger.warning(f"Failed to load {json_file}: {e}")

        self.logger.info(f"Loaded {len(self.content_index)} EWTN content items")

    def search_content(self, query: str, limit: int = 10) -> List[Dict]:
        try:
            """
            Search EWTN content for relevant information.

            Args:
                query: Search query
                limit: Maximum number of results to return

            Returns:
                List of relevant content items
            """
            query_lower = query.lower()
            results = []

            for item in self.content_index:
                score = 0

                # Score based on title match
                if query_lower in item["title"].lower():
                    score += 10

                # Score based on content match
                content_lower = item["content"].lower()
                score += content_lower.count(query_lower) * 2

                # Score based on metadata
                metadata_str = json.dumps(item["metadata"]).lower()
                if query_lower in metadata_str:
                    score += 5

                # Score based on intelligence items
                for intel in item.get("intelligence", []):
                    intel_text = json.dumps(intel).lower()
                    if query_lower in intel_text:
                        score += 3

                if score > 0:
                    results.append({
                        "score": score,
                        "item": item
                    })

            # Sort by score and return top results
            results.sort(key=lambda x: x["score"], reverse=True)
            return [r["item"] for r in results[:limit]]

        except Exception as e:
            self.logger.error(f"Error in search_content: {e}", exc_info=True)
            raise
    def query(self, question: str) -> Dict:
        """
        Answer a question using EWTN content.

        Args:
            question: Question to answer

        Returns:
            Dictionary with answer and sources
        """
        self.logger.info(f"Querying: {question}")

        # Search for relevant content
        relevant_items = self.search_content(question, limit=5)

        if not relevant_items:
            return {
                "question": question,
                "answer": "I couldn't find relevant information in the EWTN content I have access to.",
                "sources": [],
                "confidence": 0.0
            }

        # Build answer from relevant content
        answer_parts = []
        sources = []

        for item in relevant_items:
            # Extract relevant snippets
            content = item["content"]
            title = item["title"]
            url = item["url"]

            # Find relevant sentences
            sentences = content.split('.')
            relevant_sentences = [
                s.strip() for s in sentences 
                if any(word in s.lower() for word in question.lower().split())
            ][:3]  # Limit to 3 sentences per item

            if relevant_sentences:
                answer_parts.append(f"From '{title}': {' '.join(relevant_sentences)}")
                sources.append({
                    "title": title,
                    "url": url,
                    "snippets": relevant_sentences
                })

        answer = "\n\n".join(answer_parts) if answer_parts else "I found some content but couldn't extract a clear answer."

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "confidence": min(len(sources) / 5.0, 1.0),  # Confidence based on number of sources
            "total_content_items": len(self.content_index),
            "relevant_items_found": len(relevant_items)
        }

    def get_summary(self) -> Dict:
        """Get summary of available EWTN content"""
        return {
            "total_items": len(self.content_index),
            "data_directory": str(self.data_dir),
            "sample_titles": [item["title"] for item in self.content_index[:10] if item["title"]],
            "last_updated": max(
                (item.get("extracted_at", "") for item in self.content_index),
                default=""
            )
        }

    def interactive_mode(self) -> None:
        """Run in interactive mode for conversation"""
        print("=" * 60)
        print("EWTN AI Interface - Interactive Mode")
        print("=" * 60)
        print(f"Loaded {len(self.content_index)} EWTN content items")
        print("Type 'exit' or 'quit' to end the conversation")
        print("Type 'summary' to see content summary")
        print("=" * 60)
        print()

        while True:
            try:
                question = input("You: ").strip()

                if not question:
                    continue

                if question.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break

                if question.lower() == 'summary':
                    summary = self.get_summary()
                    print(f"\nEWTN Content Summary:")
                    print(f"  Total items: {summary['total_items']}")
                    print(f"  Sample titles: {', '.join(summary['sample_titles'][:5])}")
                    print()
                    continue

                # Query and display answer
                result = self.query(question)

                print(f"\nEWTN AI: {result['answer']}\n")

                if result['sources']:
                    print("Sources:")
                    for i, source in enumerate(result['sources'][:3], 1):
                        print(f"  {i}. {source['title']}")
                        if source['url']:
                            print(f"     {source['url']}")
                    print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(description="EWTN AI Interface - Query syphoned EWTN content")
        parser.add_argument(
            "--query",
            type=str,
            help="Question to ask about EWTN content"
        )
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Run in interactive mode"
        )
        parser.add_argument(
            "--data-dir",
            type=Path,
            help="Directory containing syphoned EWTN data"
        )
        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )

        args = parser.parse_args()

        # Create interface
        interface = EWTNAIInterface(
            data_dir=args.data_dir,
            project_root=args.project_root
        )

        if args.interactive:
            interface.interactive_mode()
        elif args.query:
            result = interface.query(args.query)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Show summary
            summary = interface.get_summary()
            print(json.dumps(summary, indent=2, ensure_ascii=False))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()