#!/usr/bin/env python3
"""
AI Overmind Analytics System
Tracks company hierarchical structure and calculates AI Overmind Scores
Integrates with HTTW (Hook/Trace/Track-Workflow) and WOPR Simulator
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import sqlite3

@dataclass
class Employee:
    """Employee data structure"""
    employee_id: str
    name: str
    level: int
    department: str
    team: Optional[str]
    reports_to: Optional[str]
    ai_overmind_score: float = 0.0
    data_sources: List[str] = None
    last_updated: str = None

    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = []
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

class AIOvermindAnalytics:
    """AI Overmind Analytics System"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize AI Overmind Analytics

        Args:
            config_path: Path to org_chart_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "org_chart_config.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "ai_overmind"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "overmind_analytics.db"
        self._init_database()

    def _load_config(self) -> Dict:
        try:
            """Load configuration"""
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def _init_database(self):
        try:
            """Initialize SQLite database for analytics"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Employees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level INTEGER,
                    department TEXT,
                    team TEXT,
                    reports_to TEXT,
                    ai_overmind_score REAL DEFAULT 0.0,
                    data_sources TEXT,
                    last_updated TEXT
                )
            ''')

            # Analytics history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    employee_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            ''')

            # Workflow routing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_routing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    workflow_type TEXT,
                    routed_to TEXT,
                    team TEXT,
                    status TEXT,
                    metadata TEXT
                )
            ''')

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def calculate_ai_overmind_score(self, employee_id: str, data_sources: List[str]) -> float:
        """
        Calculate AI Overmind Score (0-100%)

        Args:
            employee_id: Employee identifier
            data_sources: List of data sources JARVIS can access

        Returns:
            Score as percentage (0.0-100.0)
        """
        metrics = self.config.get("ai_overmind_metrics", {})
        control_factors = metrics.get("control_factors", {})

        # Available data sources
        available_sources = metrics.get("data_sources", [])
        accessible_sources = [ds for ds in data_sources if ds in available_sources]

        # Calculate component scores
        monitoring_score = (len(accessible_sources) / len(available_sources)) * 100 if available_sources else 0
        automation_score = self._calculate_automation_score(employee_id)
        data_access_score = (len(accessible_sources) / len(available_sources)) * 100 if available_sources else 0
        decision_influence_score = self._calculate_decision_influence(employee_id)

        # Weighted average
        weights = control_factors
        total_score = (
            monitoring_score * weights.get("monitoring", 0.3) +
            automation_score * weights.get("automation", 0.3) +
            data_access_score * weights.get("data_access", 0.2) +
            decision_influence_score * weights.get("decision_influence", 0.2)
        )

        return round(total_score, 2)

    def _calculate_automation_score(self, employee_id: str) -> float:
        """Calculate automation level score"""
        # Placeholder - would integrate with JARVIS automation tracking
        # Check how many tasks/processes are automated for this employee
        return 50.0  # Default

    def _calculate_decision_influence(self, employee_id: str) -> float:
        """Calculate decision influence score"""
        # Placeholder - would integrate with decision tracking
        # Check how many decisions JARVIS influences for this employee
        return 30.0  # Default

    def update_employee_score(self, employee_id: str, data_sources: List[str]):
        try:
            """Update employee AI Overmind Score"""
            score = self.calculate_ai_overmind_score(employee_id, data_sources)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE employees 
                SET ai_overmind_score = ?, 
                    data_sources = ?,
                    last_updated = ?
                WHERE employee_id = ?
            ''', (score, json.dumps(data_sources), datetime.now().isoformat(), employee_id))

            # Log to history
            cursor.execute('''
                INSERT INTO analytics_history (timestamp, employee_id, metric_name, metric_value)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), employee_id, "ai_overmind_score", score))

            conn.commit()
            conn.close()

            return score

        except Exception as e:
            self.logger.error(f"Error in update_employee_score: {e}", exc_info=True)
            raise
    def get_org_chart_analytics(self) -> Dict:
        try:
            """
            Get top-down analytics for entire org chart

            Returns:
                Dict with hierarchical structure and scores
            """
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM employees 
                ORDER BY level ASC, department ASC, team ASC
            ''')

            employees = []
            for row in cursor.fetchall():
                employees.append({
                    "employee_id": row[0],
                    "name": row[1],
                    "level": row[2],
                    "department": row[3],
                    "team": row[4],
                    "reports_to": row[5],
                    "ai_overmind_score": row[6],
                    "data_sources": json.loads(row[7]) if row[7] else [],
                    "last_updated": row[8]
                })

            conn.close()

            # Build hierarchical structure
            org_structure = self._build_hierarchy(employees)

            # Calculate department/team averages
            department_scores = self._calculate_department_scores(employees)
            team_scores = self._calculate_team_scores(employees)

            return {
                "timestamp": datetime.now().isoformat(),
                "org_structure": org_structure,
                "department_scores": department_scores,
                "team_scores": team_scores,
                "overall_score": self._calculate_overall_score(employees),
                "employees": employees
            }

        except Exception as e:
            self.logger.error(f"Error in get_org_chart_analytics: {e}", exc_info=True)
            raise
    def _build_hierarchy(self, employees: List[Dict]) -> Dict:
        """Build hierarchical org chart structure"""
        hierarchy = {}

        # Group by level
        by_level = {}
        for emp in employees:
            level = emp["level"]
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(emp)

        # Build top-down structure
        for level in sorted(by_level.keys()):
            hierarchy[f"level_{level}"] = by_level[level]

        return hierarchy

    def _calculate_department_scores(self, employees: List[Dict]) -> Dict:
        """Calculate average scores by department"""
        dept_scores = {}

        for emp in employees:
            dept = emp.get("department", "Unknown")
            if dept not in dept_scores:
                dept_scores[dept] = {"total": 0, "count": 0}
            dept_scores[dept]["total"] += emp["ai_overmind_score"]
            dept_scores[dept]["count"] += 1

        # Calculate averages
        for dept in dept_scores:
            dept_scores[dept] = round(
                dept_scores[dept]["total"] / dept_scores[dept]["count"], 
                2
            )

        return dept_scores

    def _calculate_team_scores(self, employees: List[Dict]) -> Dict:
        """Calculate average scores by team"""
        team_scores = {}

        for emp in employees:
            team = emp.get("team")
            if team:
                if team not in team_scores:
                    team_scores[team] = {"total": 0, "count": 0}
                team_scores[team]["total"] += emp["ai_overmind_score"]
                team_scores[team]["count"] += 1

        # Calculate averages
        for team in team_scores:
            team_scores[team] = round(
                team_scores[team]["total"] / team_scores[team]["count"],
                2
            )

        return team_scores

    def _calculate_overall_score(self, employees: List[Dict]) -> float:
        """Calculate overall company AI Overmind Score"""
        if not employees:
            return 0.0

        total = sum(emp["ai_overmind_score"] for emp in employees)
        return round(total / len(employees), 2)

    def route_workflow(self, workflow_type: str, metadata: Dict = None) -> Dict:
        """
        Route workflow to appropriate team (HELPDESK, CM, PM, Network Team)

        Args:
            workflow_type: Type of workflow (firewall, network, security, etc.)
            metadata: Additional workflow metadata

        Returns:
            Routing information
        """
        routing_config = self.config.get("workflow_routing", {})
        workflow_config = routing_config.get(workflow_type, {})

        primary = workflow_config.get("primary", "helpdesk")
        secondary = workflow_config.get("secondary", [])
        team = workflow_config.get("team", "network_team")
        priority = workflow_config.get("priority", "medium")

        routing = {
            "workflow_type": workflow_type,
            "routed_to": {
                "primary": primary,
                "secondary": secondary,
                "team": team
            },
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        # Log to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO workflow_routing 
            (timestamp, workflow_type, routed_to, team, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            routing["timestamp"],
            workflow_type,
            json.dumps(routing["routed_to"]),
            team,
            "routed",
            json.dumps(metadata or {})
        ))

        conn.commit()
        conn.close()

        return routing

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate comprehensive analytics report

        Args:
            output_path: Optional path to save report

        Returns:
            Report as JSON string
        """
        analytics = self.get_org_chart_analytics()

        report = {
            "report_date": datetime.now().isoformat(),
            "company": self.config.get("company_name", "Unknown"),
            "overall_ai_overmind_score": analytics["overall_score"],
            "hierarchical_structure": analytics["org_structure"],
            "department_breakdown": analytics["department_scores"],
            "team_breakdown": analytics["team_scores"],
            "employee_details": analytics["employees"],
            "summary": {
                "total_employees": len(analytics["employees"]),
                "average_score": analytics["overall_score"],
                "highest_score": max((e["ai_overmind_score"] for e in analytics["employees"]), default=0),
                "lowest_score": min((e["ai_overmind_score"] for e in analytics["employees"]), default=0)
            }
        }

        report_json = json.dumps(report, indent=2)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_json)

        return report_json


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Overmind Analytics")
    parser.add_argument("command", choices=["report", "score", "route"], help="Command to execute")
    parser.add_argument("--employee-id", help="Employee ID (for score command)")
    parser.add_argument("--workflow-type", help="Workflow type (for route command)")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    analytics = AIOvermindAnalytics()

    if args.command == "report":
        report = analytics.generate_report(args.output)
        print(report)
    elif args.command == "score" and args.employee_id:
        # Would need data sources - placeholder
        data_sources = ["system_logs", "user_activity", "file_access"]
        score = analytics.update_employee_score(args.employee_id, data_sources)
        print(f"AI Overmind Score for {args.employee_id}: {score}%")
    elif args.command == "route" and args.workflow_type:
        routing = analytics.route_workflow(args.workflow_type)
        print(json.dumps(routing, indent=2))


if __name__ == "__main__":


    main()