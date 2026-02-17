#!/usr/bin/env python3
"""
PEAK Employee & Data Integration
Sends employee data and analytics to @PEAK for processing
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import sqlite3
import logging
logger = logging.getLogger("peak_employee_data_integration")


# Import PEAK and AI Overmind components
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from ai_overmind_analytics import AIOvermindAnalytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

try:
    from peak_ai_orchestrator import PEAK_AI_Orchestrator, ProcessingTask
    PEAK_AVAILABLE = True
except ImportError:
    PEAK_AVAILABLE = False

try:
    from auto_workflow_processor import AutoWorkflowProcessor
    WORKFLOW_PROCESSOR_AVAILABLE = True
except ImportError:
    WORKFLOW_PROCESSOR_AVAILABLE = False


class PeakEmployeeDataIntegration:
    """Integrate employee data and analytics with PEAK"""

    def __init__(self):
        self.analytics = AIOvermindAnalytics() if ANALYTICS_AVAILABLE else None
        self.peak = PEAK_AI_Orchestrator() if PEAK_AVAILABLE else None
        self.workflow_processor = AutoWorkflowProcessor() if WORKFLOW_PROCESSOR_AVAILABLE else None

        self.data_dir = project_root / "data" / "peak_integration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def send_employee_data_to_peak(self, employee_id: Optional[str] = None) -> Dict:
        """
        Send employee data to PEAK for processing

        Args:
            employee_id: Specific employee ID, or None for all employees

        Returns:
            Integration result
        """
        if not self.analytics:
            return {"error": "AI Overmind Analytics not available"}

        # Get employee data
        if employee_id:
            employee = self.analytics.get_employee(employee_id)
            employees = [employee] if employee else []
        else:
            analytics_data = self.analytics.get_hierarchical_analytics()
            employees = analytics_data.get("employees", [])

        # Prepare data for PEAK
        peak_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "ai_overmind_analytics",
            "employees": employees,
            "org_structure": self.analytics.get_hierarchical_analytics().get("org_structure", {}),
            "department_scores": self.analytics.get_hierarchical_analytics().get("department_scores", {}),
            "overall_score": self.analytics.get_hierarchical_analytics().get("overall_score", 0.0)
        }

        # Store to file
        output_file = self.data_dir / f"peak_employee_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(peak_data, f, indent=2)

        # Send to PEAK if available
        peak_result = None
        if self.peak:
            # Create processing task for PEAK
            task_content = json.dumps(peak_data, indent=2)
            try:
                # Use submit_task method (async, but we'll handle it)
                if hasattr(self.peak, 'submit_task'):
                    import asyncio
                    task_id = asyncio.run(self.peak.submit_task(
                        content=task_content,
                        task_type="employee_analytics",
                        priority=7,
                        complexity="medium"
                    ))
                    peak_result = {"task_id": task_id, "status": "submitted", "data_file": str(output_file)}
                elif hasattr(self.peak, 'submit_batch_job'):
                    # Use batch job
                    import asyncio
                    job_id = asyncio.run(self.peak.submit_batch_job([{
                        "content": task_content,
                        "task_type": "employee_analytics",
                        "priority": 7,
                        "complexity": "medium"
                    }]))
                    peak_result = {"job_id": job_id, "status": "submitted", "data_file": str(output_file)}
                else:
                    # Store data for PEAK to pick up
                    peak_result = {"status": "queued", "data_file": str(output_file)}
            except Exception as e:
                peak_result = {"error": str(e), "data_file": str(output_file)}

        # Auto-process workflow (silent)
        if self.workflow_processor:
            workflow_data = {
                "workflow_type": "peak_integration",
                "action": "send_employee_data",
                "employee_count": len(employees),
                "impact": "high",
                "employee_level": 1,
                "data_sources": ["ai_overmind_analytics", "peak_orchestrator"],
                "category": "data_integration",
                "title": f"Employee Data to PEAK ({len(employees)} employees)"
            }
            self.workflow_processor.process_workflow(workflow_data)

        return {
            "sent": True,
            "employee_count": len(employees),
            "output_file": str(output_file),
            "peak_result": peak_result,
            "timestamp": datetime.now().isoformat()
        }

    def send_data_to_peak(self, data: Dict, data_type: str = "general") -> Dict:
        """
        Send general data to PEAK for processing

        Args:
            data: Data dictionary to send
            data_type: Type of data (analytics, workflow, etc.)

        Returns:
            Integration result
        """
        peak_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "data_integration",
            "data_type": data_type,
            "data": data
        }

        # Store to file
        output_file = self.data_dir / f"peak_data_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(peak_data, f, indent=2)

        # Send to PEAK if available
        peak_result = None
        if self.peak:
            task_content = json.dumps(peak_data, indent=2)
            try:
                # Use submit_task method (async, but we'll handle it)
                if hasattr(self.peak, 'submit_task'):
                    import asyncio
                    task_id = asyncio.run(self.peak.submit_task(
                        content=task_content,
                        task_type=data_type,
                        priority=5,
                        complexity="medium"
                    ))
                    peak_result = {"task_id": task_id, "status": "submitted", "data_file": str(output_file)}
                elif hasattr(self.peak, 'submit_batch_job'):
                    # Use batch job
                    import asyncio
                    job_id = asyncio.run(self.peak.submit_batch_job([{
                        "content": task_content,
                        "task_type": data_type,
                        "priority": 5,
                        "complexity": "medium"
                    }]))
                    peak_result = {"job_id": job_id, "status": "submitted", "data_file": str(output_file)}
                else:
                    # Store data for PEAK to pick up
                    peak_result = {"status": "queued", "data_file": str(output_file)}
            except Exception as e:
                peak_result = {"error": str(e), "data_file": str(output_file)}

        # Auto-process workflow (silent)
        if self.workflow_processor:
            workflow_data = {
                "workflow_type": "peak_integration",
                "action": "send_data",
                "data_type": data_type,
                "impact": "medium",
                "employee_level": 1,
                "data_sources": ["peak_integration"],
                "category": "data_integration",
                "title": f"Data to PEAK ({data_type})"
            }
            self.workflow_processor.process_workflow(workflow_data)

        return {
            "sent": True,
            "data_type": data_type,
            "output_file": str(output_file),
            "peak_result": peak_result,
            "timestamp": datetime.now().isoformat()
        }

    def send_all_to_peak(self) -> Dict:
        """
        Send all employee data and analytics to PEAK

        Returns:
            Complete integration result
        """
        # Send employee data
        employee_result = self.send_employee_data_to_peak()

        # Get additional analytics data
        if self.analytics:
            analytics_data = self.analytics.get_hierarchical_analytics()

            # Send analytics data
            analytics_result = self.send_data_to_peak(
                analytics_data,
                "hierarchical_analytics"
            )

            return {
                "employees": employee_result,
                "analytics": analytics_result,
                "timestamp": datetime.now().isoformat()
            }

        return employee_result


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Send employee/data to PEAK")
        parser.add_argument("--employee", help="Specific employee ID")
        parser.add_argument("--data", help="JSON data file to send")
        parser.add_argument("--data-type", default="general", help="Type of data")
        parser.add_argument("--all", action="store_true", help="Send all employee data")

        args = parser.parse_args()

        integration = PeakEmployeeDataIntegration()

        if args.all:
            result = integration.send_all_to_peak()
        elif args.employee:
            result = integration.send_employee_data_to_peak(args.employee)
        elif args.data:
            with open(args.data, 'r') as f:
                data = json.load(f)
            result = integration.send_data_to_peak(data, args.data_type)
        else:
            # Default: send all
            result = integration.send_all_to_peak()

        # Minimal output
        print(json.dumps(result, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()