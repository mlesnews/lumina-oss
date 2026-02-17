#!/usr/bin/env python3
"""
LUMINA Overview for Glenda - AUDIBLE VERSION

Non-technical, high-level overview of LUMINA spoken aloud.
For Glenda to understand how LUMINA can help "unstick their lives."

Tags: #LUMINA #OVERVIEW #AUDIBLE #NON-TECHNICAL #GLENDA @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINAOverviewAudio")

# Import FIXED voice output
try:
    from jarvis_voice_output_fixed import JARVISVoiceOutputFixed, speak_text_fixed
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("Fixed voice output not available")


def speak_text(text: str, pause_after: bool = True):
    """Speak text aloud using JARVIS voice - FIXED with fallbacks"""
    if VOICE_AVAILABLE:
        try:
            voice = JARVISVoiceOutputFixed()
            success = voice.speak(text)
            if pause_after:
                import time
                time.sleep(0.5)  # Brief pause
            if not success:
                print(f"\n[JARVIS SPEAKS - READ ALOUD]: {text}\n")
        except Exception as e:
            logger.warning(f"Could not speak: {e}")
            print(f"\n[JARVIS SPEAKS - READ ALOUD]: {text}\n")
    else:
        print(f"\n[JARVIS SPEAKS - READ ALOUD]: {text}\n")


def lumina_overview_for_glenda():
    """Non-technical LUMINA overview for Glenda"""

    print("\n" + "="*80)
    print("🎙️  LUMINA Overview for Glenda - AUDIBLE")
    print("="*80 + "\n")

    # Introduction
    intro = """
    Hello Glenda. I'm JARVIS, and I'm here to explain LUMINA in simple terms.

    Think of LUMINA as your personal assistant that never forgets where anything is.
    It's like having a super-organized filing system that you can ask questions to,
    and it always knows the answer.
    """
    speak_text(intro.strip())

    # What LUMINA Does
    what_it_does = """
    Here's what LUMINA does for you:

    First, it organizes all your information. All those medical records, financial documents,
    and business files scattered across Dropbox? LUMINA finds them, organizes them, and
    makes them easy to search.

    Second, it remembers where everything is. Instead of trying to remember where you
    put that important document, you just ask LUMINA, and it tells you exactly where
    to find it.

    Third, it connects the dots. It sees how your medical records relate to your
    financial planning, how business decisions affect personal life, and helps you
    see the big picture.

    Fourth, it tracks history. Need to know when something happened? LUMINA has
    a complete timeline of events, so you never lose track of what happened when.
    """
    speak_text(what_it_does.strip())

    # How It Helps "Unstick Your Lives"
    unstuck = """
    Now, how does this help unstick your lives?

    Right now, you probably spend a lot of time searching for documents, trying to
    remember where things are, and manually organizing information. LUMINA does all
    that heavy lifting for you.

    Need a medical record from last year? Just ask. LUMINA finds it instantly.

    Want to see your complete medical timeline? LUMINA shows you everything in order.

    Need to compile documentation for something? LUMINA gathers it all automatically.

    The goal is to free up your time and mental energy for what really matters,
    instead of spending hours searching through folders and files.
    """
    speak_text(unstuck.strip())

    # Medical Records Example
    medical_example = """
    Let me give you a practical example with medical records.

    Right now, your medical records are probably in different Dropbox folders,
    maybe organized by date or doctor. To find something, you have to remember
    which folder, which date, which doctor.

    With LUMINA, you just ask: "When was my last blood test?" And LUMINA tells you:
    "March 15th, 2025, and the results are in your Dropbox medical folder,
    file name blood_test_results_2025_03_15.pdf."

    Or you ask: "Show me all my medical records from this year." And LUMINA
    creates a complete timeline with everything organized and easy to review.

    It's like having a medical assistant who never forgets and always knows
    where everything is.
    """
    speak_text(medical_example.strip())

    # Co-CEO Implementation
    co_ceo = """
    As co-CEOs of <COMPANY_NAME>, here's how we can implement this:

    Phase one is gathering. LUMINA will scan your Dropbox, find all your documents,
    medical records, financial files, and business documents, and organize them
    into a searchable knowledge base.

    Phase two is organization. LUMINA categorizes everything by type - medical,
    financial, business, personal - and creates connections between related items.
    So when you're looking at medical expenses, LUMINA can also show you the
    related financial records.

    Phase three is daily use. You both have access, you can both search and find
    information instantly, and LUMINA keeps everything updated automatically as
    new documents come in.

    The best part? You don't need to learn complicated software. You just ask
    questions in plain English, and LUMINA answers.
    """
    speak_text(co_ceo.strip())

    # Benefits
    benefits = """
    The main benefits for you both:

    Time savings. No more hours searching for documents. Find what you need
    in seconds, not hours.

    Peace of mind. Everything is organized and documented. You never have to
    worry about losing important information.

    Better decisions. With all your information connected and organized,
    you can see the full picture and make better decisions together.

    Less stress. When you need something important, you know LUMINA can find it.
    No more panic searching or wondering if you lost something.
    """
    speak_text(benefits.strip())

    # Next Steps
    next_steps = """
    So what happens next?

    We start by scanning your Dropbox and organizing what's already there.
    Then we set up the system so it automatically organizes new documents as
    they come in.

    You both get access, and you can start using it right away. Ask questions,
    search for documents, and let LUMINA do the heavy lifting.

    The goal is to make your lives easier, less stressful, and more organized,
    so you can focus on what really matters - running your business, taking
    care of your health, and enjoying life together.

    Does this make sense? What questions do you have?
    """
    speak_text(next_steps.strip())

    print("\n" + "="*80)
    print("✅ LUMINA Overview Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    lumina_overview_for_glenda()
