#!/usr/bin/env python3
"""
LUMINA Plain Language Translator

Translates technical jargon ("technobabble") into everyday language
that non-technical users can understand intuitively.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINAPlainLanguage")


class LUMINAPlainLanguageTranslator:
    """
    Translates technical jargon to plain language

    Makes LUMINA accessible to everyday users without technical background
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Translation dictionary: technical term -> plain language
        self.translations = {
            # Core Concepts
            'LUMINA': 'LUMINA (your personal AI assistant)',
            'JARVIS': 'JARVIS (your AI helper that works 24/7)',
            'MARVIN': 'MARVIN (your AI reality checker)',
            'MANUS': 'MANUS (the control system)',

            # Technical Terms
            'API': 'connection between systems',
            'API key': 'password for connecting services',
            'authentication': 'logging in securely',
            'authorization': 'permission to do something',
            'backend': 'the behind-the-scenes system',
            'database': 'organized storage of information',
            'deployment': 'making something live and available',
            'endpoint': 'connection point',
            'framework': 'the structure everything is built on',
            'integration': 'connecting different parts together',
            'interface': 'the way you interact with something',
            'orchestration': 'coordinating multiple things to work together',
            'pipeline': 'a step-by-step process',
            'protocol': 'rules for how things communicate',
            'repository': 'where code is stored',
            'service': 'a program that does a specific job',
            'workflow': 'a series of steps to get something done',

            # AI/ML Terms
            'AI': 'artificial intelligence (smart computer programs)',
            'machine learning': 'computers that learn from examples',
            'LLM': 'large language model (a very smart AI that understands language)',
            'model': 'the AI brain that makes decisions',
            'training': 'teaching the AI',
            'inference': 'the AI making a decision or answer',
            'prompt': 'what you ask the AI',
            'context': 'the information the AI uses to understand',
            'embedding': 'how the AI stores meaning',
            'token': 'a piece of text the AI processes',

            # Development Terms
            'codebase': 'all the code that makes LUMINA work',
            'script': 'a program that does a specific task',
            'module': 'a piece of code that does one thing',
            'function': 'a small program that does one job',
            'class': 'a blueprint for creating things',
            'object': 'a thing created from a blueprint',
            'variable': 'a container that holds information',
            'algorithm': 'a step-by-step way to solve a problem',
            'debugging': 'finding and fixing problems',
            'refactoring': 'improving code without changing what it does',

            # System Terms
            'infrastructure': 'all the systems and equipment',
            'server': 'a computer that provides services',
            'client': 'the device you use to connect',
            'network': 'how computers talk to each other',
            'protocol': 'rules for communication',
            'port': 'a door for information to go through',
            'firewall': 'security that blocks unwanted access',
            'backup': 'a copy kept safe',
            'sync': 'keeping things the same across devices',

            # Data Terms
            'data': 'information',
            'dataset': 'a collection of information',
            'metadata': 'information about information',
            'format': 'how information is organized',
            'parse': 'reading and understanding information',
            'export': 'saving information in a different way',
            'import': 'bringing information in',
            'query': 'asking for specific information',
            'aggregate': 'combining information together',

            # Storytelling Terms
            'holocron': 'a notebook that tells a story',
            'chapter': 'a section of your story',
            'narrative': 'the story being told',
            'curation': 'selecting and organizing the best parts',
            'compilation': 'putting everything together',
            'multimedia': 'using video, audio, and text together',

            # Life Domain Terms
            'domain': 'an area of your life',
            'coaching': 'getting guidance and support',
            'management': 'organizing and keeping track',
            'tracking': 'watching and recording progress',
            'analytics': 'understanding patterns and trends',

            # Complex Phrases
            'unified control interface': 'one place to control everything',
            'living context matrix': 'the AI\'s memory of everything',
            'intelligent routing': 'smartly sending requests to the right place',
            'resource-aware': 'knowing what the system can handle',
            'dependency injection': 'connecting parts together automatically',
            'error handling': 'what happens when something goes wrong',
            'workflow automation': 'making repetitive tasks automatic',
            'real-time processing': 'doing things instantly as they happen',
            'asynchronous operation': 'doing multiple things at the same time',
            'state management': 'keeping track of what\'s happening',
            'event-driven': 'reacting to things as they happen',
            'microservices': 'small programs that work together',
            'containerization': 'packaging programs to run anywhere',
            'orchestration': 'coordinating multiple programs',
            'scalability': 'ability to handle more work',
            'reliability': 'working consistently without breaking',
            'maintainability': 'easy to fix and improve',
        }

        # Common patterns to simplify
        self.patterns = [
            (r'\bAPI\b', 'connection'),
            (r'\bREST\b', 'web connection'),
            (r'\bJSON\b', 'data format'),
            (r'\bHTTP\b', 'web communication'),
            (r'\bHTTPS\b', 'secure web communication'),
            (r'\bSSH\b', 'secure remote connection'),
            (r'\bCLI\b', 'command line (typing commands)'),
            (r'\bGUI\b', 'graphical interface (clicking buttons)'),
            (r'\bIDE\b', 'code editor (where you write code)'),
            (r'\bTTS\b', 'text-to-speech (turning text into voice)'),
            (r'\bSTT\b', 'speech-to-text (turning voice into text)'),
            (r'\bNLP\b', 'natural language processing (understanding human language)'),
            (r'\bML\b', 'machine learning'),
            (r'\bDL\b', 'deep learning (advanced AI)'),
            (r'\bGPU\b', 'graphics card (helps AI think faster)'),
            (r'\bCPU\b', 'processor (the computer\'s brain)'),
            (r'\bRAM\b', 'memory (temporary storage)'),
            (r'\bSSD\b', 'fast storage'),
            (r'\bHDD\b', 'slower storage'),
        ]

    def translate_text(self, text: str) -> str:
        """Translate technical text to plain language"""
        translated = text

        # Apply pattern replacements
        for pattern, replacement in self.patterns:
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)

        # Apply dictionary translations
        words = translated.split()
        translated_words = []

        for word in words:
            # Clean word (remove punctuation for lookup)
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word.lower() in self.translations:
                # Replace with translation, preserving punctuation
                punctuation = re.sub(r'[\w]', '', word)
                translated_word = self.translations[clean_word.lower()] + punctuation
                translated_words.append(translated_word)
            else:
                translated_words.append(word)

        return ' '.join(translated_words)

    def translate_documentation(self, file_path: Path) -> Dict[str, Any]:
        """Translate a documentation file to plain language"""
        if not file_path.exists():
            return {'error': f'File not found: {file_path}'}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into sections
            sections = content.split('\n\n')
            translated_sections = []

            for section in sections:
                if section.strip():
                    translated = self.translate_text(section)
                    translated_sections.append(translated)

            return {
                'original': content,
                'translated': '\n\n'.join(translated_sections),
                'file': str(file_path)
            }
        except Exception as e:
            return {'error': str(e)}

    def create_plain_language_guide(self) -> Dict[str, Any]:
        """Create a plain language guide for LUMINA"""
        guide = {
            'title': 'LUMINA in Plain English - A Guide for Everyone',
            'sections': {}
        }

        # What is LUMINA?
        guide['sections']['what_is_lumina'] = {
            'title': 'What is LUMINA?',
            'technical': 'LUMINA is an AI-powered system for knowledge management, storytelling, and personal assistance.',
            'plain': 'LUMINA is your personal AI assistant that helps you organize your life, tell your story, and get things done. Think of it as a smart helper that works 24/7 to support you.'
        }

        # What does LUMINA do?
        guide['sections']['what_does_it_do'] = {
            'title': 'What Does LUMINA Do?',
            'plain': [
                'Helps you organize your life across all areas (health, finance, career, relationships, etc.)',
                'Turns your experiences into stories (like a personal book of your life)',
                'Creates videos, audio, and other content from your stories',
                'Provides guidance and coaching when you need it',
                'Manages your digital life (files, projects, tasks)',
                'Learns from you and adapts to your needs'
            ]
        }

        # Key Features
        guide['sections']['key_features'] = {
            'title': 'Key Features in Plain English',
            'features': {
                'JARVIS': 'Your main AI assistant that works all the time to help you',
                'MARVIN': 'Your AI reality checker that helps you see things clearly',
                'MANUS': 'The control system that manages everything',
                'Storytelling': 'Turns your life experiences into stories',
                'Multimedia': 'Creates videos, audio, and other content',
                'Life Coaching': 'Provides guidance across all areas of your life',
                'Automation': 'Does repetitive tasks for you automatically'
            }
        }

        # How It Works
        guide['sections']['how_it_works'] = {
            'title': 'How Does LUMINA Work?',
            'plain': [
                'You interact with LUMINA naturally, like talking to a friend',
                'LUMINA learns about you and your needs',
                'LUMINA helps you make decisions and take action',
                'Everything you do becomes part of your life story',
                'LUMINA creates content (videos, audio) from your story',
                'You can access everything through simple interfaces'
            ]
        }

        # Common Questions
        guide['sections']['common_questions'] = {
            'title': 'Common Questions',
            'questions': {
                'Do I need to be technical?': 'No! LUMINA is designed for everyone. You just talk to it naturally.',
                'Is my information safe?': 'Yes, LUMINA takes security seriously and protects your data.',
                'How much does it cost?': 'LUMINA is open-source and free to use.',
                'Can I customize it?': 'Yes, LUMINA adapts to your needs and preferences.',
                'What if I need help?': 'LUMINA has built-in help and guidance systems.'
            }
        }

        return guide

    def translate_assessment_reports(self) -> Dict[str, Any]:
        """Translate recent assessment reports to plain language"""
        reports_dir = self.project_root / "data" / "lumina_analysis"

        if not reports_dir.exists():
            return {'error': 'Reports directory not found'}

        translations = {}

        # Find recent reports
        report_files = [
            'godmode_storytelling_assessment_20251231_230401.json',
            'multimedia_storytelling_assessment_20251231_230517.json',
            'life_domain_assistant_assessment_20251231_230702.json'
        ]

        for report_file in report_files:
            report_path = reports_dir / report_file
            if report_path.exists():
                try:
                    with open(report_path, 'r') as f:
                        report = json.load(f)

                    # Translate key sections
                    translated = {
                        'title': self.translate_text(report.get('vision', {}).get('title', '')),
                        'description': self.translate_text(report.get('vision', {}).get('description', '')),
                        'readiness': f"{report.get('feasibility', {}).get('readiness_score', 0):.1f}% ready",
                        'feasibility': report.get('feasibility', {}).get('overall_feasibility', 'unknown')
                    }

                    translations[report_file] = translated
                except Exception as e:
                    self.logger.error(f"Error translating {report_file}: {e}")

        return translations

    def generate_plain_language_summary(self) -> Dict[str, Any]:
        """Generate plain language summary of LUMINA"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'title': 'LUMINA - Plain English Summary',
            'sections': {}
        }

        # What is LUMINA?
        summary['sections']['what_is_lumina'] = {
            'title': 'What is LUMINA?',
            'content': 'LUMINA is your personal AI assistant that helps you organize your life, tell your story, and get things done. Think of it as a smart helper that works 24/7 to support you in every area of your life.'
        }

        # What Can LUMINA Do?
        summary['sections']['capabilities'] = {
            'title': 'What Can LUMINA Do?',
            'items': [
                'Help you manage all areas of your life (health, finance, career, relationships, etc.)',
                'Turn your life experiences into stories (like a personal book)',
                'Create videos, audio, and other content from your stories',
                'Provide guidance and coaching when you need it',
                'Automate repetitive tasks',
                'Learn from you and adapt to your needs'
            ]
        }

        # How Does It Work?
        summary['sections']['how_it_works'] = {
            'title': 'How Does LUMINA Work?',
            'steps': [
                'You talk to LUMINA naturally, like talking to a friend',
                'LUMINA learns about you and your needs',
                'LUMINA helps you make decisions and take action',
                'Everything becomes part of your life story',
                'LUMINA creates content (videos, audio) from your story',
                'You access everything through simple, easy-to-use interfaces'
            ]
        }

        # Key Features
        summary['sections']['key_features'] = {
            'title': 'Key Features',
            'features': {
                'JARVIS': 'Your main AI assistant that works all the time',
                'MARVIN': 'Your AI reality checker for clear thinking',
                'Storytelling': 'Turns your life into stories',
                'Multimedia': 'Creates videos, audio, and content',
                'Life Coaching': 'Guidance across all life areas',
                'Automation': 'Does tasks for you automatically'
            }
        }

        # Current Status
        summary['sections']['current_status'] = {
            'title': 'Current Status',
            'status': {
                'Storytelling': '50% ready - Foundation exists, can create stories',
                'Multimedia': '75% ready - Can create videos, working on YouTube integration',
                'Life Assistant': '20% ready - Foundation exists, expanding to all life areas'
            }
        }

        return summary

    def save_plain_language_guide(self, guide: Dict[str, Any]) -> Path:
        """Save plain language guide"""
        docs_dir = self.project_root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        guide_file = docs_dir / "LUMINA_PLAIN_LANGUAGE_GUIDE.md"

        try:
            # Format as Markdown
            markdown = f"# {guide['title']}\n\n"
            markdown += f"*Last Updated: {datetime.now().strftime('%Y-%m-%d')}*\n\n"

            for section_key, section in guide['sections'].items():
                markdown += f"## {section.get('title', section_key)}\n\n"

                if 'plain' in section:
                    if isinstance(section['plain'], list):
                        for item in section['plain']:
                            markdown += f"- {item}\n"
                    else:
                        markdown += f"{section['plain']}\n"
                elif 'features' in section:
                    for key, value in section['features'].items():
                        markdown += f"**{key}**: {value}\n\n"
                elif 'questions' in section:
                    for question, answer in section['questions'].items():
                        markdown += f"**Q: {question}**\n\nA: {answer}\n\n"

                markdown += "\n"

            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            self.logger.info(f"✅ Plain language guide saved: {guide_file}")
            return guide_file
        except Exception as e:
            self.logger.error(f"Failed to save guide: {e}")
            return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Plain Language Translator")
    parser.add_argument("--create-guide", action="store_true", help="Create plain language guide")
    parser.add_argument("--translate", type=str, help="Translate a file")
    parser.add_argument("--summary", action="store_true", help="Generate summary")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    translator = LUMINAPlainLanguageTranslator(project_root)

    try:
        if args.create_guide:
            guide = translator.create_plain_language_guide()
            guide_file = translator.save_plain_language_guide(guide)
            print(f"✅ Plain language guide created: {guide_file}")

        elif args.translate:
            file_path = Path(args.translate)
            result = translator.translate_documentation(file_path)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("\n" + "="*80)
                print("TRANSLATED TEXT")
                print("="*80)
                print(result['translated'])

        elif args.summary:
            summary = translator.generate_plain_language_summary()
            print("\n" + "="*80)
            print("LUMINA - PLAIN ENGLISH SUMMARY")
            print("="*80)
            for section_key, section in summary['sections'].items():
                print(f"\n## {section.get('title', section_key)}")
                if 'content' in section:
                    print(section['content'])
                elif 'items' in section:
                    for item in section['items']:
                        print(f"  • {item}")
                elif 'steps' in section:
                    for i, step in enumerate(section['steps'], 1):
                        print(f"  {i}. {step}")
                elif 'features' in section:
                    for key, value in section['features'].items():
                        print(f"  • {key}: {value}")
                elif 'status' in section:
                    for key, value in section['status'].items():
                        print(f"  • {key}: {value}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()