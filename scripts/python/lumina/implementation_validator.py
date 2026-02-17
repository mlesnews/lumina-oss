#!/usr/bin/env python3
"""
Lumina Implementation Validator

Validates that implementations serve Lumina principles.
Prevents falling in love with implementations.

Tags: #LUMINA #VALIDATION #PRINCIPLES #ANTI_LOCK_IN @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
from lumina.principles import LuminaPrinciples, LuminaPrinciple

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaImplementationValidator")


class ImplementationValidator:
    """
    Validates implementations against Lumina principles.

    Prevents:
    - Falling in love with specific implementations
    - Pigeon-holing into one approach
    - Locking into specific technologies
    """

    def __init__(self):
        self.principles = LuminaPrinciples()
        logger.info("🔍 Implementation Validator initialized")

    def validate(
        self,
        implementation: Dict[str, Any],
        check_lock_in: bool = True
    ) -> Dict[str, Any]:
        """
        Validate implementation against Lumina principles.

        Args:
            implementation: Implementation to validate
            check_lock_in: Check for lock-in risks

        Returns:
            Validation result
        """
        results = {
            'valid': True,
            'principle_compliance': {},
            'lock_in_risks': [],
            'recommendations': []
        }

        # Check principle compliance
        compliance = self.principles.validate_implementation(implementation)
        results['principle_compliance'] = compliance

        # Check for lock-in risks
        if check_lock_in:
            lock_in_risks = self._check_lock_in_risks(implementation)
            results['lock_in_risks'] = lock_in_risks

        # Generate recommendations
        recommendations = self._generate_recommendations(implementation, compliance)
        results['recommendations'] = recommendations

        # Overall validity
        all_compliant = all(
            result['serves_principle']
            for result in compliance.values()
        )
        no_lock_in = len(results['lock_in_risks']) == 0

        results['valid'] = all_compliant and no_lock_in

        return results

    def _check_lock_in_risks(
        self,
        implementation: Dict[str, Any]
    ) -> List[str]:
        """Check for lock-in risks"""
        risks = []

        # Check for hard-coded dependencies
        if implementation.get('hard_coded_dependencies'):
            risks.append("Hard-coded dependencies - consider abstraction")

        # Check for vendor lock-in
        if implementation.get('vendor_specific'):
            risks.append("Vendor-specific implementation - consider abstraction")

        # Check for single implementation
        if not implementation.get('has_alternatives'):
            risks.append("No alternative implementations - consider plugin architecture")

        # Check for tight coupling
        if implementation.get('tightly_coupled'):
            risks.append("Tightly coupled - consider loose coupling")

        return risks

    def _generate_recommendations(
        self,
        implementation: Dict[str, Any],
        compliance: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []

        # Check each principle
        for principle, result in compliance.items():
            if not result['serves_principle']:
                recommendations.append(
                    f"Improve {principle} compliance: {result['notes']}"
                )

        # Check for abstraction opportunities
        if not implementation.get('has_abstraction'):
            recommendations.append(
                "Consider adding abstraction layer for flexibility"
            )

        # Check for plugin architecture
        if not implementation.get('plugin_based'):
            recommendations.append(
                "Consider plugin architecture for extensibility"
            )

        return recommendations

    def check_evolution_readiness(
        self,
        current_impl: Dict[str, Any],
        new_impl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if we can evolve from current to new implementation.

        Args:
            current_impl: Current implementation
            new_impl: New implementation

        Returns:
            Evolution readiness assessment
        """
        assessment = {
            'ready': True,
            'migration_path': 'unknown',
            'risks': [],
            'benefits': []
        }

        # Check if both serve principles
        current_valid = self.validate(current_impl)
        new_valid = self.validate(new_impl)

        if not current_valid['valid']:
            assessment['risks'].append("Current implementation doesn't serve principles")

        if not new_valid['valid']:
            assessment['risks'].append("New implementation doesn't serve principles")
            assessment['ready'] = False

        # Check for abstraction layer
        if current_impl.get('has_abstraction') and new_impl.get('has_abstraction'):
            assessment['migration_path'] = 'abstraction_layer'
            assessment['benefits'].append("Both use abstraction - easy migration")
        else:
            assessment['risks'].append("No abstraction layer - migration may be difficult")

        return assessment


def main():
    """Example usage"""
    validator = ImplementationValidator()

    # Example implementation
    implementation = {
        'name': 'Ollama AI Provider',
        'local_first': True,
        'human_control': True,
        'knowledge_preserved': True,
        'security_builtin': True,
        'extensible': True,
        'has_abstraction': True,
        'plugin_based': True,
        'has_alternatives': True,
        'hard_coded_dependencies': False,
        'vendor_specific': False,
        'tightly_coupled': False
    }

    # Validate
    result = validator.validate(implementation)

    print("VALIDATION RESULT")
    print("=" * 80)
    print(f"Valid: {'✅' if result['valid'] else '❌'}")
    print(f"\nPrinciple Compliance:")
    for principle, compliance in result['principle_compliance'].items():
        status = "✅" if compliance['serves_principle'] else "❌"
        print(f"  {status} {principle}")

    if result['lock_in_risks']:
        print(f"\nLock-In Risks:")
        for risk in result['lock_in_risks']:
            print(f"  ⚠️  {risk}")

    if result['recommendations']:
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  💡 {rec}")


if __name__ == "__main__":


    main()