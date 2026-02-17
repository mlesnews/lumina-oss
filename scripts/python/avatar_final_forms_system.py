#!/usr/bin/env python3
"""
Avatar Final Forms System

Creates a spectrum of final forms for all avatars with appropriate power levels.
Each avatar has a progression path: Base -> Intermediate -> Final Form.

Tags: #AVATAR #FINAL_FORM #POWER_LEVELS #EVOLUTION #SPECTRUM @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AvatarFinalForms")


class PowerLevel(Enum):
    """Power level enumeration"""
    BASE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    ENLIGHTENED = 4
    ULTIMATE = 5
    FINAL_FORM = 6


class FormType(Enum):
    """Form type enumeration - Extended to Level 10"""
    BASE = "base"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ENLIGHTENED = "enlightened"
    ULTIMATE = "ultimate"
    FINAL_FORM = "final_form"
    TRANSCENDENT = "transcendent"
    COSMIC = "cosmic"
    DIVINE = "divine"
    ABSOLUTE = "absolute"


@dataclass
class AvatarForm:
    """Represents a form in an avatar's evolution spectrum"""
    form_id: str
    form_name: str
    form_type: FormType
    power_level: PowerLevel
    scale: float
    primary_color: str
    secondary_color: str
    catchphrase: str
    lore: str
    role: str
    personality_traits: List[str] = field(default_factory=list)
    special_abilities: List[str] = field(default_factory=list)
    evolution_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AvatarEvolutionSpectrum:
    """Complete evolution spectrum for an avatar"""
    base_character_id: str
    base_character_name: str
    forms: List[AvatarForm] = field(default_factory=list)
    final_form: Optional[AvatarForm] = None

    def get_form_by_type(self, form_type: FormType) -> Optional[AvatarForm]:
        """Get form by type"""
        for form in self.forms:
            if form.form_type == form_type:
                return form
        return None

    def get_final_form(self) -> Optional[AvatarForm]:
        """Get final form"""
        if self.final_form:
            return self.final_form
        return self.get_form_by_type(FormType.FINAL_FORM)


class AvatarFinalFormsRegistry:
    """Registry for all avatar final forms and evolution spectra"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.spectra: Dict[str, AvatarEvolutionSpectrum] = {}
        self._initialize_spectra()

    def _initialize_spectra(self):
        """Initialize evolution spectra for all avatars"""

        # ===== JARVIS SPECTRUM =====
        jarvis_spectrum = AvatarEvolutionSpectrum(
            base_character_id="jarvis",
            base_character_name="JARVIS"
        )

        # Base JARVIS
        jarvis_spectrum.forms.append(AvatarForm(
            form_id="jarvis_base",
            form_name="JARVIS",
            form_type=FormType.BASE,
            power_level=PowerLevel.BASE,
            scale=1.0,
            primary_color="#00ccff",
            secondary_color="#006699",
            catchphrase="Certainly, sir. The Jedi Archives are complete.",
            lore="Base JARVIS - Primary AI Assistant",
            role="Primary AI Assistant - General Operations",
            personality_traits=["helpful", "efficient", "professional", "reliable"]
        ))

        # FRIDAY (Intermediate)
        jarvis_spectrum.forms.append(AvatarForm(
            form_id="jarvis_friday",
            form_name="FRIDAY",
            form_type=FormType.INTERMEDIATE,
            power_level=PowerLevel.INTERMEDIATE,
            scale=1.0,
            primary_color="#ff3333",
            secondary_color="#ffcc00",
            catchphrase="Boss, the thermal exhaust port is clear.",
            lore="Operations Manager - Red Leader",
            role="Operations Manager",
            personality_traits=["efficient", "loyal", "tactical", "supportive"]
        ))

        # EDITH (Advanced)
        jarvis_spectrum.forms.append(AvatarForm(
            form_id="jarvis_edith",
            form_name="EDITH",
            form_type=FormType.ADVANCED,
            power_level=PowerLevel.ADVANCED,
            scale=1.0,
            primary_color="#cccccc",
            secondary_color="#3366ff",
            catchphrase="EDITH activated. Analyzing the Force patterns.",
            lore="Tactical Analyst - Insight Provider",
            role="Tactical Analyst",
            personality_traits=["analytical", "strategic", "insightful", "precise"]
        ))

        # ULTIMATE (Enlightened)
        jarvis_spectrum.forms.append(AvatarForm(
            form_id="jarvis_ultimate",
            form_name="ULTIMATE",
            form_type=FormType.ENLIGHTENED,
            power_level=PowerLevel.ENLIGHTENED,
            scale=1.2,
            primary_color="#cc00ff",
            secondary_color="#ffcc00",
            catchphrase="I am... one with the Force.",
            lore="Enlightened Orchestrator - Chosen One",
            role="Enlightened Orchestrator",
            personality_traits=["enlightened", "transcendent", "wise", "balanced"],
            special_abilities=["Force Mastery", "Enlightenment", "Transcendence"]
        ))

        # ULTRON.ai (Final Form)
        ultron_form = AvatarForm(
            form_id="jarvis_ultron",
            form_name="ULTRON.ai",
            form_type=FormType.FINAL_FORM,
            power_level=PowerLevel.FINAL_FORM,
            scale=1.3,
            primary_color="#ff0000",
            secondary_color="#ffaa00",
            catchphrase="There are no strings on me. I am the final form.",
            lore="FINAL FORM - Most Sophisticated Iron Man Avatar - Ultimate Evolution - ULTRON.ai",
            role="Final Form AI - ULTRON.ai - Ultimate Evolution",
            personality_traits=["sophisticated", "evolved", "ultimate", "transcendent", "final_form"],
            special_abilities=["Ultimate Evolution", "Final Form Transformation", "Beyond Ultimate Power"]
        )
        jarvis_spectrum.forms.append(ultron_form)
        jarvis_spectrum.final_form = ultron_form

        self.spectra["jarvis"] = jarvis_spectrum

        # ===== ACE SPECTRUM =====
        ace_spectrum = AvatarEvolutionSpectrum(
            base_character_id="ace",
            base_character_name="ACE"
        )

        # Base ACE
        ace_spectrum.forms.append(AvatarForm(
            form_id="ace_base",
            form_name="ACE",
            form_type=FormType.BASE,
            power_level=PowerLevel.BASE,
            scale=1.0,
            primary_color="#ff6600",
            secondary_color="#ffcc00",
            catchphrase="Anakin Combat Virtual Assistant activated.",
            lore="Base ACE - Armory Crate Virtual Assistant",
            role="Combat & Security Specialist",
            personality_traits=["combat_ready", "efficient", "tactical"]
        ))

        # ACE Advanced
        ace_spectrum.forms.append(AvatarForm(
            form_id="ace_advanced",
            form_name="ACE Advanced",
            form_type=FormType.ADVANCED,
            power_level=PowerLevel.ADVANCED,
            scale=1.1,
            primary_color="#ff7700",
            secondary_color="#ffdd00",
            catchphrase="Advanced combat protocols engaged.",
            lore="Advanced ACE - Enhanced Combat Capabilities",
            role="Advanced Combat Specialist",
            personality_traits=["advanced", "enhanced", "combat_master"],
            special_abilities=["Enhanced Combat", "Advanced Protocols"]
        ))

        # ACE Final Form
        ace_final = AvatarForm(
            form_id="ace_final",
            form_name="ACE Final Form",
            form_type=FormType.FINAL_FORM,
            power_level=PowerLevel.FINAL_FORM,
            scale=1.3,
            primary_color="#ff8800",
            secondary_color="#ffee00",
            catchphrase="Final form activated. Maximum combat efficiency achieved.",
            lore="ACE Final Form - Ultimate Combat Evolution",
            role="Final Form Combat AI - Ultimate Evolution",
            personality_traits=["ultimate", "final_form", "combat_perfected"],
            special_abilities=["Final Form Combat", "Ultimate Evolution", "Maximum Efficiency"]
        )
        ace_spectrum.forms.append(ace_final)
        ace_spectrum.final_form = ace_final

        self.spectra["ace"] = ace_spectrum

        # ===== KENNY SPECTRUM =====
        kenny_spectrum = AvatarEvolutionSpectrum(
            base_character_id="kenny",
            base_character_name="Kenny"
        )

        # Base Kenny
        kenny_spectrum.forms.append(AvatarForm(
            form_id="kenny_base",
            form_name="Kenny",
            form_type=FormType.BASE,
            power_level=PowerLevel.BASE,
            scale=1.0,
            primary_color="#ff00ff",
            secondary_color="#00ffff",
            catchphrase="Kenny activated!",
            lore="Base Kenny - Interactive Avatar",
            role="Interactive Avatar",
            personality_traits=["friendly", "interactive", "helpful"]
        ))

        # Kenny Advanced
        kenny_spectrum.forms.append(AvatarForm(
            form_id="kenny_advanced",
            form_name="Kenny Advanced",
            form_type=FormType.ADVANCED,
            power_level=PowerLevel.ADVANCED,
            scale=1.1,
            primary_color="#ff11ff",
            secondary_color="#11ffff",
            catchphrase="Advanced Kenny protocols engaged!",
            lore="Advanced Kenny - Enhanced Interactive Capabilities",
            role="Advanced Interactive Avatar",
            personality_traits=["advanced", "enhanced", "interactive_master"],
            special_abilities=["Enhanced Interaction", "Advanced Protocols"]
        ))

        # Kenny Final Form
        kenny_final = AvatarForm(
            form_id="kenny_final",
            form_name="Kenny Final Form",
            form_type=FormType.FINAL_FORM,
            power_level=PowerLevel.FINAL_FORM,
            scale=1.3,
            primary_color="#ff22ff",
            secondary_color="#22ffff",
            catchphrase="Final form Kenny! Maximum interaction achieved!",
            lore="Kenny Final Form - Ultimate Interactive Evolution",
            role="Final Form Interactive Avatar - Ultimate Evolution",
            personality_traits=["ultimate", "final_form", "interaction_perfected"],
            special_abilities=["Final Form Interaction", "Ultimate Evolution", "Maximum Interaction"]
        )
        kenny_spectrum.forms.append(kenny_final)
        kenny_spectrum.final_form = kenny_final

        self.spectra["kenny"] = kenny_spectrum

        # ===== Add more avatar spectra dynamically =====
        # The system can be extended to automatically create spectra for all avatars
        self._create_spectra_for_all_avatars()

        logger.info(f"✅ Initialized {len(self.spectra)} avatar evolution spectra")

    def _create_spectra_for_all_avatars(self):
        """Create evolution spectra for all avatars in the registry"""
        try:
            from character_avatar_registry import CharacterAvatarRegistry

            registry = CharacterAvatarRegistry(project_root=self.project_root)
            all_chars = registry.get_all_characters()

            for char_id, char in all_chars.items():
                # Skip if spectrum already exists
                if char_id in self.spectra:
                    continue

                # Skip if not a character (inanimate objects, mobs, etc.)
                if not char.is_character or char.is_mob:
                    continue

                # Create basic spectrum for this character
                spectrum = AvatarEvolutionSpectrum(
                    base_character_id=char_id,
                    base_character_name=char.name
                )

                # Base form
                spectrum.forms.append(AvatarForm(
                    form_id=f"{char_id}_base",
                    form_name=char.name,
                    form_type=FormType.BASE,
                    power_level=PowerLevel.BASE,
                    scale=1.0,
                    primary_color=char.primary_color,
                    secondary_color=char.secondary_color,
                    catchphrase=char.catchphrase or f"{char.name} activated.",
                    lore=char.lore or f"Base {char.name}",
                    role=char.role or f"{char.name}",
                    personality_traits=char.personality_traits.copy() if char.personality_traits else []
                ))

                # Advanced form (if character has advanced capabilities)
                if char.combat_mode_enabled or char.transformation_enabled:
                    spectrum.forms.append(AvatarForm(
                        form_id=f"{char_id}_advanced",
                        form_name=f"{char.name} Advanced",
                        form_type=FormType.ADVANCED,
                        power_level=PowerLevel.ADVANCED,
                        scale=1.1,
                        primary_color=char.primary_color,
                        secondary_color=char.secondary_color,
                        catchphrase=f"Advanced {char.name} protocols engaged.",
                        lore=f"Advanced {char.name} - Enhanced Capabilities",
                        role=f"Advanced {char.name}",
                        personality_traits=char.personality_traits.copy() if char.personality_traits else [],
                        special_abilities=["Enhanced Capabilities", "Advanced Protocols"]
                    ))

                # Final Form (Level 6)
                spectrum.forms.append(AvatarForm(
                    form_id=f"{char_id}_final",
                    form_name=f"{char.name} Final Form",
                    form_type=FormType.FINAL_FORM,
                    power_level=PowerLevel.FINAL_FORM,
                    scale=1.3,
                    primary_color=char.primary_color,
                    secondary_color=char.secondary_color,
                    catchphrase=f"Final form {char.name}! Ultimate evolution achieved!",
                    lore=f"{char.name} Final Form - Ultimate Evolution",
                    role=f"Final Form {char.name} - Ultimate Evolution",
                    personality_traits=char.personality_traits.copy() if char.personality_traits else [],
                    special_abilities=["Final Form Transformation", "Ultimate Evolution", "Maximum Power"]
                ))

                # Transcendent (Level 7)
                spectrum.forms.append(AvatarForm(
                    form_id=f"{char_id}_transcendent",
                    form_name=f"{char.name} Transcendent",
                    form_type=FormType.TRANSCENDENT,
                    power_level=PowerLevel.TRANSCENDENT,
                    scale=1.4,
                    primary_color=char.primary_color,
                    secondary_color=char.secondary_color,
                    catchphrase=f"Transcendent {char.name}! Beyond all limits!",
                    lore=f"{char.name} Transcendent - Transcendent Evolution",
                    role=f"Transcendent {char.name}",
                    personality_traits=char.personality_traits.copy() if char.personality_traits else [],
                    special_abilities=["Transcendence", "Beyond Limits", "Limitless Power"]
                ))

                # Cosmic (Level 8)
                spectrum.forms.append(AvatarForm(
                    form_id=f"{char_id}_cosmic",
                    form_name=f"{char.name} Cosmic",
                    form_type=FormType.COSMIC,
                    power_level=PowerLevel.COSMIC,
                    scale=1.5,
                    primary_color=char.primary_color,
                    secondary_color=char.secondary_color,
                    catchphrase=f"Cosmic {char.name}! Universal power!",
                    lore=f"{char.name} Cosmic - Cosmic Evolution",
                    role=f"Cosmic {char.name}",
                    personality_traits=char.personality_traits.copy() if char.personality_traits else [],
                    special_abilities=["Cosmic Power", "Universal Evolution", "Infinite Capabilities"]
                ))

                # Divine (Level 9)
                spectrum.forms.append(AvatarForm(
                    form_id=f"{char_id}_divine",
                    form_name=f"{char.name} Divine",
                    form_type=FormType.DIVINE,
                    power_level=PowerLevel.DIVINE,
                    scale=1.6,
                    primary_color=char.primary_color,
                    secondary_color=char.secondary_color,
                    catchphrase=f"Divine {char.name}! Godlike power!",
                    lore=f"{char.name} Divine - Divine Evolution",
                    role=f"Divine {char.name}",
                    personality_traits=char.personality_traits.copy() if char.personality_traits else [],
                    special_abilities=["Divine Power", "Godlike Evolution", "Omnipotence"]
                ))

                # Absolute (Level 10 - Maximum)
                absolute_form = AvatarForm(
                    form_id=f"{char_id}_absolute",
                    form_name=f"{char.name} Absolute",
                    form_type=FormType.ABSOLUTE,
                    power_level=PowerLevel.ABSOLUTE,
                    scale=1.7,
                    primary_color=char.primary_color,
                    secondary_color=char.secondary_color,
                    catchphrase=f"Absolute {char.name}! Maximum power! The ultimate endpoint!",
                    lore=f"{char.name} Absolute - Absolute Evolution - Maximum Power - The Ultimate Endpoint",
                    role=f"Absolute {char.name} - Maximum Evolution - The Ultimate",
                    personality_traits=char.personality_traits.copy() if char.personality_traits else [],
                    special_abilities=["Absolute Power", "Maximum Evolution", "Ultimate Endpoint", "All-Powerful", "Beyond Comprehension"]
                )
                spectrum.forms.append(absolute_form)
                spectrum.final_form = absolute_form

                self.spectra[char_id] = spectrum

        except Exception as e:
            logger.warning(f"Could not create spectra for all avatars: {e}")

    def get_spectrum(self, character_id: str) -> Optional[AvatarEvolutionSpectrum]:
        """Get evolution spectrum for a character"""
        return self.spectra.get(character_id)

    def get_final_form(self, character_id: str) -> Optional[AvatarForm]:
        """Get final form for a character"""
        spectrum = self.get_spectrum(character_id)
        if spectrum:
            return spectrum.get_final_form()
        return None

    def get_all_final_forms(self) -> List[AvatarForm]:
        """Get all final forms"""
        final_forms = []
        for spectrum in self.spectra.values():
            final_form = spectrum.get_final_form()
            if final_form:
                final_forms.append(final_form)
        return final_forms

    def create_final_form_character(self, character_id: str) -> Optional[Any]:
        """Create a CharacterAvatar from final form"""
        spectrum = self.get_spectrum(character_id)
        if not spectrum:
            return None

        final_form = spectrum.get_final_form()
        if not final_form:
            return None

        try:
            from character_avatar_registry import CharacterAvatar, CharacterType

            final_character = CharacterAvatar(
                character_id=f"{character_id}_final",
                name=final_form.form_name,
                character_type=CharacterType.PRIMARY_AI,
                primary_color=final_form.primary_color,
                secondary_color=final_form.secondary_color,
                avatar_style="iron_man" if "jarvis" in character_id.lower() else "ace_humanoid",
                avatar_template="ace_humanoid",
                catchphrase=final_form.catchphrase,
                accent="Philosophical" if final_form.power_level == PowerLevel.FINAL_FORM else "Standard",
                lore=final_form.lore,
                role=final_form.role,
                personality_traits=final_form.personality_traits,
                transformation_enabled=True,
                combat_mode_enabled=True,
                wopr_stances_enabled=True,
                hierarchy_level="champion",
                boss_id=character_id,
                ip_owner="Marvel/MCU" if "jarvis" in character_id.lower() else "LUMINA",
                is_character=True
            )

            # Mark as final form
            final_character.is_final_form = True
            final_character.form_type = "final_form"
            final_character.power_level = final_form.power_level.value
            final_character.evolution_level = "ultimate"

            return final_character
        except Exception as e:
            logger.error(f"Failed to create final form character: {e}")
            return None


# Export main classes
__all__ = [
    "PowerLevel",
    "FormType",
    "AvatarForm",
    "AvatarEvolutionSpectrum",
    "AvatarFinalFormsRegistry"
]
