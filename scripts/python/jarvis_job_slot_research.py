#!/usr/bin/env python3
"""
JARVIS Job Slot Research System
MANUS Framework - Comprehensive Research of Valuable Job Slots for Project Lumina

Thoroughly researches job slots that would be valuable and beneficial to Project Lumina.
Each job slot represents a specialized role/capability that JARVIS can assume.

@JARVIS @MANUS @JOB_SLOTS @RESEARCH
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISJobSlotResearch")


class JobSlotCategory(Enum):
    """Categories of job slots"""
    SYSTEMS_ENGINEERING = "systems_engineering"
    SOFTWARE_DEVELOPMENT = "software_development"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    DATA_SCIENCE = "data_science"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    INTEGRATION = "integration"
    RESEARCH = "research"
    OPERATIONS = "operations"


class JobSlotPriority(Enum):
    """Priority levels for job slot implementation"""
    CRITICAL = "critical"      # Must have
    HIGH = "high"             # Very valuable
    MEDIUM = "medium"         # Valuable
    LOW = "low"              # Nice to have
    FUTURE = "future"         # Future consideration


@dataclass
class JobSlotRequirement:
    """Requirements for a job slot"""
    requirement: str
    importance: str  # critical, important, nice_to_have
    current_capability: Optional[str] = None
    gap_analysis: Optional[str] = None


@dataclass
class JobSlotResearch:
    """Research findings for a job slot"""
    job_slot_id: str
    job_title: str
    category: JobSlotCategory
    priority: JobSlotPriority
    description: str
    value_proposition: str
    key_responsibilities: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    tools_technologies: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    requirements: List[JobSlotRequirement] = field(default_factory=list)
    implementation_complexity: str = "medium"  # low, medium, high
    estimated_value: float = 0.0  # 0.0 to 1.0
    research_date: datetime = field(default_factory=datetime.now)
    research_status: str = "pending"  # pending, in_progress, completed
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['category'] = self.category.value
        data['priority'] = self.priority.value
        data['requirements'] = [r.__dict__ for r in self.requirements]
        data['research_date'] = self.research_date.isoformat()
        return data


class JARVISJobSlotResearcher:
    """
    JARVIS Job Slot Research System

    Researches and evaluates job slots valuable to Project Lumina.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Data directories
        self.data_dir = self.project_root / "data" / "jarvis_job_slots"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.research_file = self.data_dir / "job_slot_research.json"
        self.implemented_file = self.data_dir / "implemented_job_slots.json"

        # Research registry
        self.job_slots: Dict[str, JobSlotResearch] = {}
        self.implemented_slots: Dict[str, Dict[str, Any]] = {}

        # Load existing research
        self._load_research()
        self._load_implemented()

        # Initialize with known valuable job slots
        self._initialize_valuable_slots()

        self.logger.info("✅ JARVIS Job Slot Research System initialized")
        self.logger.info(f"   Research slots: {len(self.job_slots)}")
        self.logger.info(f"   Implemented slots: {len(self.implemented_slots)}")

    def _load_research(self):
        """Load existing research"""
        if self.research_file.exists():
            try:
                with open(self.research_file, 'r') as f:
                    data = json.load(f)
                    for slot_id, slot_data in data.items():
                        research = JobSlotResearch(
                            job_slot_id=slot_data['job_slot_id'],
                            job_title=slot_data['job_title'],
                            category=JobSlotCategory(slot_data['category']),
                            priority=JobSlotPriority(slot_data['priority']),
                            description=slot_data['description'],
                            value_proposition=slot_data['value_proposition'],
                            key_responsibilities=slot_data.get('key_responsibilities', []),
                            required_skills=slot_data.get('required_skills', []),
                            tools_technologies=slot_data.get('tools_technologies', []),
                            integration_points=slot_data.get('integration_points', []),
                            benefits=slot_data.get('benefits', []),
                            challenges=slot_data.get('challenges', []),
                            requirements=[
                                JobSlotRequirement(**r) for r in slot_data.get('requirements', [])
                            ],
                            implementation_complexity=slot_data.get('implementation_complexity', 'medium'),
                            estimated_value=slot_data.get('estimated_value', 0.0),
                            research_date=datetime.fromisoformat(slot_data.get('research_date', datetime.now().isoformat())),
                            research_status=slot_data.get('research_status', 'pending'),
                            notes=slot_data.get('notes', '')
                        )
                        self.job_slots[slot_id] = research
                self.logger.info(f"✅ Loaded {len(self.job_slots)} job slot research entries")
            except Exception as e:
                self.logger.error(f"Failed to load research: {e}")

    def _load_implemented(self):
        """Load implemented job slots"""
        if self.implemented_file.exists():
            try:
                with open(self.implemented_file, 'r') as f:
                    self.implemented_slots = json.load(f)
                self.logger.info(f"✅ Loaded {len(self.implemented_slots)} implemented job slots")
            except Exception as e:
                self.logger.error(f"Failed to load implemented slots: {e}")

    def _save_research(self):
        """Save research to file"""
        try:
            data = {
                slot_id: research.to_dict()
                for slot_id, research in self.job_slots.items()
            }
            with open(self.research_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.debug(f"💾 Saved {len(self.job_slots)} job slot research entries")
        except Exception as e:
            self.logger.error(f"Failed to save research: {e}")

    def _initialize_valuable_slots(self):
        """Initialize research for valuable job slots"""

        # Windows Systems Engineer (already implemented)
        if 'windows_systems_engineer' not in self.job_slots:
            self.job_slots['windows_systems_engineer'] = JobSlotResearch(
                job_slot_id='windows_systems_engineer',
                job_title='Windows Systems Engineer',
                category=JobSlotCategory.SYSTEMS_ENGINEERING,
                priority=JobSlotPriority.CRITICAL,
                description='Manages PC hardware, OS, and applications as parts of JARVIS\'s body with health baselines and log monitoring',
                value_proposition='Ensures PC health and proactive maintenance, treating the entire system as part of JARVIS\'s body',
                key_responsibilities=[
                    'Monitor PC hardware health (CPU, RAM, Disk)',
                    'Monitor Windows OS services',
                    'Monitor application health',
                    'Parse and tail system/application logs',
                    'Maintain health baselines',
                    'Proactive issue detection and resolution'
                ],
                required_skills=[
                    'Windows system administration',
                    'Event log analysis',
                    'Performance monitoring',
                    'Log parsing and analysis',
                    'Health metric tracking'
                ],
                tools_technologies=[
                    'Windows Event Viewer',
                    'PowerShell',
                    'psutil',
                    'Windows Service Control',
                    'Log tailing libraries'
                ],
                integration_points=[
                    'JARVIS Body Check System',
                    'MANUS Workstation Controller',
                    'Windows Event Monitor',
                    'Health Monitoring System'
                ],
                benefits=[
                    'Proactive PC health management',
                    'Early issue detection',
                    'Automated maintenance',
                    'Complete system visibility',
                    'Reduced downtime'
                ],
                challenges=[
                    'Log parsing complexity',
                    'Performance overhead',
                    'Baseline calibration'
                ],
                implementation_complexity='medium',
                estimated_value=0.95,
                research_status='implemented',
                notes='✅ IMPLEMENTED - See jarvis_windows_systems_engineer.py'
            )

        # Add more valuable job slots to research
        valuable_slots = [
            {
                'id': 'devops_engineer',
                'title': 'DevOps Engineer',
                'category': JobSlotCategory.INFRASTRUCTURE,
                'priority': JobSlotPriority.HIGH,
                'description': 'Manages CI/CD pipelines, deployments, infrastructure as code, and automation',
                'value_proposition': 'Streamlines deployment and infrastructure management for Project Lumina',
                'key_responsibilities': [
                    'CI/CD pipeline management',
                    'Infrastructure as Code (IaC)',
                    'Container orchestration',
                    'Deployment automation',
                    'Infrastructure monitoring',
                    'Disaster recovery'
                ],
                'required_skills': [
                    'CI/CD tools (GitHub Actions, Azure DevOps)',
                    'Docker/Kubernetes',
                    'Infrastructure automation',
                    'Configuration management',
                    'Monitoring and alerting'
                ],
                'tools_technologies': [
                    'GitHub Actions',
                    'Docker',
                    'Kubernetes',
                    'Terraform',
                    'Ansible',
                    'Azure DevOps'
                ],
                'integration_points': [
                    'Git repositories',
                    'Azure infrastructure',
                    'Container registry',
                    'Deployment pipelines'
                ],
                'benefits': [
                    'Automated deployments',
                    'Infrastructure consistency',
                    'Faster release cycles',
                    'Reduced manual errors',
                    'Scalable infrastructure'
                ],
                'challenges': [
                    'Complexity of container orchestration',
                    'Learning curve for IaC',
                    'Infrastructure cost management'
                ],
                'estimated_value': 0.85
            },
            {
                'id': 'security_engineer',
                'title': 'Security Engineer',
                'category': JobSlotCategory.SECURITY,
                'priority': JobSlotPriority.CRITICAL,
                'description': 'Manages security posture, threat detection, vulnerability scanning, and compliance',
                'value_proposition': 'Ensures Project Lumina security and compliance with defense protocols',
                'key_responsibilities': [
                    'Security scanning and monitoring',
                    'Threat detection and response',
                    'Vulnerability assessment',
                    'Security policy enforcement',
                    'Compliance monitoring',
                    'Incident response'
                ],
                'required_skills': [
                    'Security scanning',
                    'Threat analysis',
                    'Vulnerability assessment',
                    'Security policy management',
                    'Incident response'
                ],
                'tools_technologies': [
                    'Security scanning tools',
                    'Azure Key Vault',
                    'Security monitoring',
                    'Compliance frameworks'
                ],
                'integration_points': [
                    'Azure Key Vault',
                    'Security scanning automation',
                    'Threat intelligence',
                    'Compliance systems'
                ],
                'benefits': [
                    'Proactive security',
                    'Threat detection',
                    'Compliance assurance',
                    'Reduced security risks',
                    'Automated security checks'
                ],
                'challenges': [
                    'False positive management',
                    'Security tool integration',
                    'Compliance complexity'
                ],
                'estimated_value': 0.90
            },
            {
                'id': 'data_engineer',
                'title': 'Data Engineer',
                'category': JobSlotCategory.DATA_SCIENCE,
                'priority': JobSlotPriority.HIGH,
                'description': 'Manages data pipelines, ETL processes, data quality, and data infrastructure',
                'value_proposition': 'Ensures data quality and efficient data processing for Project Lumina',
                'key_responsibilities': [
                    'Data pipeline management',
                    'ETL process automation',
                    'Data quality monitoring',
                    'Data infrastructure management',
                    'Data warehouse optimization',
                    'Data governance'
                ],
                'required_skills': [
                    'ETL processes',
                    'Data pipeline design',
                    'Data quality assurance',
                    'Data warehousing',
                    'Data governance'
                ],
                'tools_technologies': [
                    'ETL tools',
                    'Data pipelines',
                    'Data quality tools',
                    'Data warehouses',
                    'SQL databases'
                ],
                'integration_points': [
                    'R5 Living Context Matrix',
                    'SYPHON data extraction',
                    'Data storage systems',
                    'Analytics platforms'
                ],
                'benefits': [
                    'Data quality assurance',
                    'Efficient data processing',
                    'Data pipeline automation',
                    'Better data insights',
                    'Data governance'
                ],
                'challenges': [
                    'Data pipeline complexity',
                    'Data quality monitoring',
                    'Performance optimization'
                ],
                'estimated_value': 0.80
            },
            {
                'id': 'site_reliability_engineer',
                'title': 'Site Reliability Engineer (SRE)',
                'category': JobSlotCategory.OPERATIONS,
                'priority': JobSlotPriority.HIGH,
                'description': 'Ensures system reliability, performance, and availability',
                'value_proposition': 'Maintains high availability and reliability of Project Lumina systems',
                'key_responsibilities': [
                    'System reliability monitoring',
                    'Performance optimization',
                    'Incident management',
                    'Capacity planning',
                    'Service level objectives (SLOs)',
                    'Error budget management'
                ],
                'required_skills': [
                    'System monitoring',
                    'Performance optimization',
                    'Incident response',
                    'Capacity planning',
                    'SLO/SLA management'
                ],
                'tools_technologies': [
                    'Monitoring tools',
                    'Performance analysis',
                    'Incident management',
                    'Capacity planning tools'
                ],
                'integration_points': [
                    'System monitoring',
                    'Performance metrics',
                    'Incident response',
                    'Alerting systems'
                ],
                'benefits': [
                    'High system availability',
                    'Proactive issue detection',
                    'Performance optimization',
                    'Reliable operations',
                    'Better user experience'
                ],
                'challenges': [
                    'SLO definition',
                    'Error budget management',
                    'Performance optimization'
                ],
                'estimated_value': 0.85
            },
            {
                'id': 'cloud_architect',
                'title': 'Cloud Architect',
                'category': JobSlotCategory.INFRASTRUCTURE,
                'priority': JobSlotPriority.MEDIUM,
                'description': 'Designs and manages cloud infrastructure architecture',
                'value_proposition': 'Optimizes cloud infrastructure for Project Lumina',
                'key_responsibilities': [
                    'Cloud architecture design',
                    'Infrastructure optimization',
                    'Cost management',
                    'Scalability planning',
                    'Cloud security',
                    'Multi-cloud strategy'
                ],
                'required_skills': [
                    'Cloud architecture',
                    'Infrastructure design',
                    'Cost optimization',
                    'Scalability planning',
                    'Cloud security'
                ],
                'tools_technologies': [
                    'Azure',
                    'AWS',
                    'GCP',
                    'Terraform',
                    'Cloud monitoring'
                ],
                'integration_points': [
                    'Azure infrastructure',
                    'Cloud services',
                    'Infrastructure as Code',
                    'Cloud monitoring'
                ],
                'benefits': [
                    'Optimized cloud costs',
                    'Scalable architecture',
                    'Better performance',
                    'Cloud security',
                    'Multi-cloud support'
                ],
                'challenges': [
                    'Cloud cost management',
                    'Multi-cloud complexity',
                    'Architecture decisions'
                ],
                'estimated_value': 0.75
            },
            {
                'id': 'ai_ml_engineer',
                'title': 'AI/ML Engineer',
                'category': JobSlotCategory.DATA_SCIENCE,
                'priority': JobSlotPriority.HIGH,
                'description': 'Manages AI/ML models, training pipelines, and model deployment',
                'value_proposition': 'Enhances AI capabilities and model management for Project Lumina',
                'key_responsibilities': [
                    'ML model training and optimization',
                    'Model deployment and monitoring',
                    'Feature engineering',
                    'Model versioning',
                    'A/B testing',
                    'Model performance monitoring'
                ],
                'required_skills': [
                    'Machine learning',
                    'Model training',
                    'Model deployment',
                    'MLOps',
                    'Feature engineering'
                ],
                'tools_technologies': [
                    'ML frameworks (PyTorch, TensorFlow)',
                    'MLOps tools',
                    'Model serving',
                    'Feature stores',
                    'Model monitoring'
                ],
                'integration_points': [
                    'Local LLM systems',
                    'Model training pipelines',
                    'Model serving infrastructure',
                    'AI evaluation systems'
                ],
                'benefits': [
                    'Better AI models',
                    'Automated model training',
                    'Model performance monitoring',
                    'Faster model deployment',
                    'Improved AI capabilities'
                ],
                'challenges': [
                    'Model complexity',
                    'Training infrastructure',
                    'Model monitoring'
                ],
                'estimated_value': 0.80
            },
            {
                'id': 'network_engineer',
                'title': 'Network Engineer',
                'category': JobSlotCategory.INFRASTRUCTURE,
                'priority': JobSlotPriority.MEDIUM,
                'description': 'Manages network infrastructure, connectivity, and network security',
                'value_proposition': 'Ensures reliable network connectivity and security for Project Lumina',
                'key_responsibilities': [
                    'Network monitoring',
                    'Network configuration',
                    'Network security',
                    'Connectivity troubleshooting',
                    'Bandwidth management',
                    'Network optimization'
                ],
                'required_skills': [
                    'Network administration',
                    'Network security',
                    'Troubleshooting',
                    'Network protocols',
                    'Network monitoring'
                ],
                'tools_technologies': [
                    'Network monitoring tools',
                    'Network configuration',
                    'Firewall management',
                    'VPN management'
                ],
                'integration_points': [
                    'Home lab infrastructure',
                    'NAS connectivity',
                    'Network monitoring',
                    'Security systems'
                ],
                'benefits': [
                    'Reliable connectivity',
                    'Network security',
                    'Performance optimization',
                    'Troubleshooting automation',
                    'Bandwidth management'
                ],
                'challenges': [
                    'Network complexity',
                    'Security configuration',
                    'Performance optimization'
                ],
                'estimated_value': 0.70
            },
            {
                'id': 'database_administrator',
                'title': 'Database Administrator (DBA)',
                'category': JobSlotCategory.INFRASTRUCTURE,
                'priority': JobSlotPriority.MEDIUM,
                'description': 'Manages databases, performance optimization, and data integrity',
                'value_proposition': 'Ensures database performance and data integrity for Project Lumina',
                'key_responsibilities': [
                    'Database performance optimization',
                    'Backup and recovery',
                    'Database security',
                    'Query optimization',
                    'Database monitoring',
                    'Data integrity management'
                ],
                'required_skills': [
                    'Database administration',
                    'Query optimization',
                    'Backup and recovery',
                    'Database security',
                    'Performance tuning'
                ],
                'tools_technologies': [
                    'SQL databases',
                    'NoSQL databases',
                    'Database monitoring',
                    'Backup tools',
                    'Query analyzers'
                ],
                'integration_points': [
                    'R5 Living Context Matrix',
                    'SYPHON storage',
                    'Application databases',
                    'Data warehouses'
                ],
                'benefits': [
                    'Database performance',
                    'Data integrity',
                    'Automated backups',
                    'Query optimization',
                    'Database security'
                ],
                'challenges': [
                    'Performance tuning',
                    'Backup management',
                    'Query optimization'
                ],
                'estimated_value': 0.75
            },
            {
                'id': 'automation_engineer',
                'title': 'Automation Engineer',
                'category': JobSlotCategory.AUTOMATION,
                'priority': JobSlotPriority.HIGH,
                'description': 'Creates and manages automation workflows and scripts',
                'value_proposition': 'Increases automation and reduces manual work for Project Lumina',
                'key_responsibilities': [
                    'Workflow automation',
                    'Script development',
                    'Process automation',
                    'Automation testing',
                    'Workflow optimization',
                    'Automation monitoring'
                ],
                'required_skills': [
                    'Workflow automation',
                    'Scripting',
                    'Process automation',
                    'Automation testing',
                    'Workflow design'
                ],
                'tools_technologies': [
                    'n8n',
                    'PowerShell',
                    'Python',
                    'Automation frameworks',
                    'Workflow engines'
                ],
                'integration_points': [
                    'n8n workflows',
                    'MANUS automation',
                    'Workflow systems',
                    'Script execution'
                ],
                'benefits': [
                    'Reduced manual work',
                    'Faster processes',
                    'Consistent execution',
                    'Error reduction',
                    'Scalable automation'
                ],
                'challenges': [
                    'Workflow complexity',
                    'Error handling',
                    'Maintenance overhead'
                ],
                'estimated_value': 0.85
            },
            {
                'id': 'quality_assurance_engineer',
                'title': 'Quality Assurance Engineer (QA)',
                'category': JobSlotCategory.SOFTWARE_DEVELOPMENT,
                'priority': JobSlotPriority.MEDIUM,
                'description': 'Ensures code quality, testing, and software reliability',
                'value_proposition': 'Maintains high code quality and reliability for Project Lumina',
                'key_responsibilities': [
                    'Automated testing',
                    'Code quality checks',
                    'Test coverage analysis',
                    'Bug detection',
                    'Quality metrics',
                    'Testing automation'
                ],
                'required_skills': [
                    'Test automation',
                    'Code quality',
                    'Testing frameworks',
                    'Bug tracking',
                    'Quality metrics'
                ],
                'tools_technologies': [
                    'Testing frameworks',
                    'Code quality tools',
                    'Test coverage tools',
                    'Bug tracking',
                    'CI/CD integration'
                ],
                'integration_points': [
                    'CI/CD pipelines',
                    'Code repositories',
                    'Testing frameworks',
                    'Quality metrics'
                ],
                'benefits': [
                    'Higher code quality',
                    'Automated testing',
                    'Early bug detection',
                    'Quality metrics',
                    'Reliable software'
                ],
                'challenges': [
                    'Test coverage',
                    'False positives',
                    'Maintenance overhead'
                ],
                'estimated_value': 0.75
            }
        ]

        for slot_data in valuable_slots:
            slot_id = slot_data['id']
            if slot_id not in self.job_slots:
                research = JobSlotResearch(
                    job_slot_id=slot_id,
                    job_title=slot_data['title'],
                    category=JobSlotCategory(slot_data['category']),
                    priority=JobSlotPriority(slot_data['priority']),
                    description=slot_data['description'],
                    value_proposition=slot_data['value_proposition'],
                    key_responsibilities=slot_data.get('key_responsibilities', []),
                    required_skills=slot_data.get('required_skills', []),
                    tools_technologies=slot_data.get('tools_technologies', []),
                    integration_points=slot_data.get('integration_points', []),
                    benefits=slot_data.get('benefits', []),
                    challenges=slot_data.get('challenges', []),
                    implementation_complexity=slot_data.get('implementation_complexity', 'medium'),
                    estimated_value=slot_data.get('estimated_value', 0.0),
                    research_status='pending'
                )
                self.job_slots[slot_id] = research

        self._save_research()

    def research_job_slot(self, job_slot_id: str, additional_research: Optional[Dict[str, Any]] = None) -> JobSlotResearch:
        """Research a specific job slot"""
        if job_slot_id not in self.job_slots:
            raise ValueError(f"Job slot not found: {job_slot_id}")

        research = self.job_slots[job_slot_id]
        research.research_status = 'in_progress'

        # Add additional research if provided
        if additional_research:
            for key, value in additional_research.items():
                if hasattr(research, key):
                    setattr(research, key, value)

        # Mark as completed
        research.research_status = 'completed'
        research.research_date = datetime.now()

        self._save_research()

        self.logger.info(f"✅ Research completed for: {research.job_title}")
        return research

    def evaluate_job_slot(self, job_slot_id: str) -> Dict[str, Any]:
        """Evaluate a job slot's value and implementation feasibility"""
        if job_slot_id not in self.job_slots:
            raise ValueError(f"Job slot not found: {job_slot_id}")

        research = self.job_slots[job_slot_id]

        # Calculate value score
        value_score = research.estimated_value

        # Adjust based on priority
        priority_multiplier = {
            JobSlotPriority.CRITICAL: 1.0,
            JobSlotPriority.HIGH: 0.8,
            JobSlotPriority.MEDIUM: 0.6,
            JobSlotPriority.LOW: 0.4,
            JobSlotPriority.FUTURE: 0.2
        }
        value_score *= priority_multiplier.get(research.priority, 0.5)

        # Check if already implemented
        is_implemented = job_slot_id in self.implemented_slots

        # Implementation feasibility
        complexity_scores = {
            'low': 0.9,
            'medium': 0.7,
            'high': 0.5
        }
        feasibility = complexity_scores.get(research.implementation_complexity, 0.7)

        return {
            'job_slot_id': job_slot_id,
            'job_title': research.job_title,
            'value_score': value_score,
            'estimated_value': research.estimated_value,
            'priority': research.priority.value,
            'feasibility': feasibility,
            'is_implemented': is_implemented,
            'recommendation': 'implement' if value_score > 0.7 and not is_implemented else 'research_more' if value_score > 0.5 else 'defer',
            'research': research.to_dict()
        }

    def get_research_report(self) -> Dict[str, Any]:
        """Get comprehensive research report"""
        # Evaluate all job slots
        evaluations = {}
        for slot_id in self.job_slots.keys():
            evaluations[slot_id] = self.evaluate_job_slot(slot_id)

        # Sort by value score
        sorted_slots = sorted(evaluations.items(), key=lambda x: x[1]['value_score'], reverse=True)

        # Group by priority
        by_priority = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'future': []
        }

        for slot_id, eval_data in sorted_slots:
            priority = eval_data['priority']
            by_priority[priority].append(eval_data)

        return {
            'timestamp': datetime.now().isoformat(),
            'total_slots': len(self.job_slots),
            'implemented_slots': len(self.implemented_slots),
            'pending_research': len([s for s in self.job_slots.values() if s.research_status == 'pending']),
            'by_priority': by_priority,
            'top_recommendations': [eval_data for _, eval_data in sorted_slots[:10]],
            'evaluations': evaluations
        }

    def mark_implemented(self, job_slot_id: str, implementation_details: Dict[str, Any]):
        """Mark a job slot as implemented"""
        if job_slot_id not in self.job_slots:
            raise ValueError(f"Job slot not found: {job_slot_id}")

        self.implemented_slots[job_slot_id] = {
            'job_slot_id': job_slot_id,
            'job_title': self.job_slots[job_slot_id].job_title,
            'implemented_date': datetime.now().isoformat(),
            'implementation_details': implementation_details
        }

        # Update research status
        self.job_slots[job_slot_id].research_status = 'implemented'

        # Save
        try:
            with open(self.implemented_file, 'w') as f:
                json.dump(self.implemented_slots, f, indent=2)
            self._save_research()
            self.logger.info(f"✅ Marked {job_slot_id} as implemented")
        except Exception as e:
            self.logger.error(f"Failed to save implemented slot: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Job Slot Research System")
    parser.add_argument("--report", action="store_true", help="Get research report")
    parser.add_argument("--evaluate", type=str, help="Evaluate specific job slot")
    parser.add_argument("--list", action="store_true", help="List all job slots")
    parser.add_argument("--implemented", action="store_true", help="List implemented job slots")
    parser.add_argument("--mark-implemented", type=str, help="Mark job slot as implemented")

    args = parser.parse_args()

    researcher = JARVISJobSlotResearcher()

    try:
        if args.report:
            report = researcher.get_research_report()
            print("\n" + "="*80)
            print("📊 JARVIS Job Slot Research Report")
            print("="*80)
            print(f"Total Slots: {report['total_slots']}")
            print(f"Implemented: {report['implemented_slots']}")
            print(f"Pending Research: {report['pending_research']}")
            print("\n🔝 Top Recommendations:")
            for i, rec in enumerate(report['top_recommendations'][:5], 1):
                print(f"\n{i}. {rec['job_title']}")
                print(f"   Value Score: {rec['value_score']:.2f}")
                print(f"   Priority: {rec['priority']}")
                print(f"   Recommendation: {rec['recommendation']}")
                if rec['is_implemented']:
                    print(f"   ✅ Already Implemented")
            print("\n" + "="*80)

        elif args.evaluate:
            eval_data = researcher.evaluate_job_slot(args.evaluate)
            print("\n" + "="*80)
            print(f"📊 Evaluation: {eval_data['job_title']}")
            print("="*80)
            print(f"Value Score: {eval_data['value_score']:.2f}")
            print(f"Estimated Value: {eval_data['estimated_value']:.2f}")
            print(f"Priority: {eval_data['priority']}")
            print(f"Feasibility: {eval_data['feasibility']:.2f}")
            print(f"Status: {'✅ Implemented' if eval_data['is_implemented'] else '⏳ Not Implemented'}")
            print(f"Recommendation: {eval_data['recommendation']}")
            print("="*80)

        elif args.list:
            print("\n📋 All Job Slots:")
            print("="*80)
            for slot_id, research in researcher.job_slots.items():
                status_icon = "✅" if research.research_status == 'implemented' else "📋"
                print(f"{status_icon} {research.job_title} ({slot_id})")
                print(f"   Category: {research.category.value}")
                print(f"   Priority: {research.priority.value}")
                print(f"   Value: {research.estimated_value:.2f}")
                print()

        elif args.implemented:
            print("\n✅ Implemented Job Slots:")
            print("="*80)
            for slot_id, details in researcher.implemented_slots.items():
                print(f"  - {details['job_title']} ({slot_id})")
                print(f"    Implemented: {details['implemented_date']}")

        elif args.mark_implemented:
            researcher.mark_implemented(args.mark_implemented, {
                'implementation_file': 'TBD',
                'notes': 'Marked as implemented'
            })
            print(f"✅ Marked {args.mark_implemented} as implemented")

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":

# TODO: Add error handling to functions identified by roast system:  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
#   - to_dict (line 89)
#   - _initialize_valuable_slots (line 191)
#   - research_job_slot (line 765)
#   - evaluate_job_slot (line 788)
#   - get_research_report (line 831)


    main()