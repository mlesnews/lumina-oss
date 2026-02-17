#!/usr/bin/env python3
"""
Setup Automated Feedback Cycles

Creates automated feedback cycle scheduling for Windows Task Scheduler or
runs as a background service.

@LUMINA @AUTOMATION @FEEDBACK_LOOP
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from lumina_data_mining_feedback_loop import LuminaFeedbackLoop

logger = get_logger("AutomatedFeedbackCycles")


def create_windows_task_scheduler_xml(interval_hours: int = 1) -> str:
    """Create Windows Task Scheduler XML for automated feedback cycles"""
    try:
        script_path = Path(__file__).parent / "lumina_data_mining_feedback_loop.py"
        python_exe = sys.executable

        xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}</Date>
    <Author>Lumina Automated Feedback Loop</Author>
    <Description>Runs Lumina Data Mining Feedback Loop every {interval_hours} hour(s)</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{datetime.now().strftime("%Y-%m-%dT%H:00:00")}</StartBoundary>
      <Enabled>true</Enabled>
      <Interval>PT{interval_hours}H</Interval>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{script_path}" --cycle</Arguments>
      <WorkingDirectory>"{project_root}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

        return xml
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in create_windows_task_scheduler_xml: {e}", exc_info=True)
        raise


def create_windows_task_scheduler_script(interval_hours: int = 1) -> str:
    try:
        """Create PowerShell script to register Windows Task Scheduler task"""

        script_path = Path(__file__).parent / "lumina_data_mining_feedback_loop.py"
        python_exe = sys.executable
        task_name = "Lumina_Feedback_Loop"

        ps_script = f'''# PowerShell script to create Lumina Feedback Loop scheduled task

$TaskName = "{task_name}"
$PythonExe = "{python_exe}"
$ScriptPath = "{script_path}"
$WorkingDir = "{project_root}"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {{
    Write-Host "Task already exists. Removing existing task..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}}

# Create action
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`" --cycle" -WorkingDirectory $WorkingDir

# Create trigger (every {interval_hours} hour(s))
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddHours(1) -RepetitionInterval (New-TimeSpan -Hours {interval_hours}) -RepetitionDuration (New-TimeSpan -Days 365)

# Create settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable:$false

# Create principal
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Register task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Lumina Data Mining Feedback Loop - Runs every {interval_hours} hour(s)"

Write-Host "✅ Scheduled task '$TaskName' created successfully!"
Write-Host "   Interval: Every {interval_hours} hour(s)"
Write-Host "   Next run: Check Task Scheduler"
'''

        return ps_script
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in create_windows_task_scheduler_script: {e}", exc_info=True)
        raise


def create_systemd_service(interval_hours: int = 1) -> str:
    """Create systemd service file for Linux"""
    try:
        script_path = Path(__file__).parent / "run_feedback_cycle.py"
        python_exe = sys.executable
        user = "USER_REPLACE"  # Should be replaced with actual user

        service_file = f"""[Unit]
Description=Lumina Data Mining Feedback Loop
After=network.target

[Service]
Type=oneshot
User={user}
WorkingDirectory={project_root}
ExecStart={python_exe} {script_path}
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

        timer_file = f"""[Unit]
Description=Run Lumina Feedback Loop every {interval_hours} hours
Requires=lumina-feedback-loop.service

[Timer]
OnBootSec=1h
OnUnitActiveSec={interval_hours}h
Unit=lumina-feedback-loop.service

[Install]
WantedBy=timers.target
"""

        return service_file, timer_file
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in create_systemd_service: {e}", exc_info=True)
        raise


def create_run_script() -> str:
    """Create standalone run script for feedback cycle"""

    script_content = f'''#!/usr/bin/env python3
"""
Run Single Feedback Cycle

Can be called from cron, Task Scheduler, or manually.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_data_mining_feedback_loop import LuminaFeedbackLoop

if __name__ == "__main__":
    feedback_loop = LuminaFeedbackLoop(project_root)
    report = feedback_loop.run_feedback_cycle()
    print(f"✅ Feedback cycle complete: {{report['cycle_number']}}")
'''

    return script_content


def setup_automated_cycles(interval_hours: int = 1, platform: Optional[str] = None) -> Dict[str, Any]:
    """Setup automated feedback cycles"""
    try:
        if platform is None:
            import platform as plat
            platform = plat.system().lower()

        logger.info(f"Setting up automated feedback cycles for {platform} (interval: {interval_hours} hours)")

        output_dir = project_root / "scripts" / "automation" / "feedback_cycles"
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            'platform': platform,
            'interval_hours': interval_hours,
            'files_created': [],
            'instructions': []
        }

        if platform == 'windows':
            # Create Task Scheduler XML
            xml_file = output_dir / "lumina_feedback_loop_task.xml"
            xml_content = create_windows_task_scheduler_xml(interval_hours)
            xml_file.write_text(xml_content, encoding='utf-16')
            results['files_created'].append(str(xml_file))
            results['instructions'].append(f"Import task: schtasks /Create /XML \"{xml_file}\" /TN Lumina_Feedback_Loop")

            # Create PowerShell script
            ps_file = output_dir / "create_scheduled_task.ps1"
            ps_content = create_windows_task_scheduler_script(interval_hours)
            ps_file.write_text(ps_content)
            results['files_created'].append(str(ps_file))
            results['instructions'].append(f"Run PowerShell script: .\\{ps_file.name} (as Administrator)")

        elif platform == 'linux':
            # Create systemd service files
            service_file = output_dir / "lumina-feedback-loop.service"
            timer_file = output_dir / "lumina-feedback-loop.timer"
            service_content, timer_content = create_systemd_service(interval_hours)
            service_file.write_text(service_content)
            timer_file.write_text(timer_content)
            results['files_created'].extend([str(service_file), str(timer_file)])
            results['instructions'].extend([
                f"Copy service file: sudo cp {service_file} /etc/systemd/system/",
                f"Copy timer file: sudo cp {timer_file} /etc/systemd/system/",
                "Enable and start: sudo systemctl enable lumina-feedback-loop.timer && sudo systemctl start lumina-feedback-loop.timer"
            ])

        # Create run script (cross-platform)
        run_script = output_dir / "run_feedback_cycle.py"
        run_content = create_run_script()
        run_script.write_text(run_content)
        results['files_created'].append(str(run_script))

        # Create cron entry example
        cron_file = output_dir / "cron_example.txt"
        cron_content = f"""# Add to crontab (crontab -e) to run every {interval_hours} hour(s)
# Format: minute hour day month day-of-week command

# Every {interval_hours} hour(s)
0 */{interval_hours} * * * {sys.executable} {run_script} >> {project_root}/logs/feedback_cycle.log 2>&1

# Or use simpler interval (runs at minute 0 of every hour if interval_hours=1)
# 0 * * * * {sys.executable} {run_script} >> {project_root}/logs/feedback_cycle.log 2>&1
"""
        cron_file.write_text(cron_content)
        results['files_created'].append(str(cron_file))

        # Create setup instructions
        instructions_file = output_dir / "SETUP_INSTRUCTIONS.md"
        instructions = f"""# Automated Feedback Cycles Setup

## Platform: {platform}
## Interval: Every {interval_hours} hour(s)

## Setup Options

### Option 1: Run Script Directly (Manual/Cron)
```bash
python {run_script}
```

### Option 2: Task Scheduler (Windows)
"""

        if platform == 'windows':
            instructions += f"""
1. Run PowerShell script as Administrator:
   ```powershell
   .\\{output_dir / "create_scheduled_task.ps1"}
   ```

2. Or import XML manually:
   ```cmd
   schtasks /Create /XML "{output_dir / "lumina_feedback_loop_task.xml"}" /TN Lumina_Feedback_Loop
   ```

3. Verify task:
   ```cmd
   schtasks /Query /TN Lumina_Feedback_Loop
   ```
"""
        elif platform == 'linux':
            instructions += f"""
1. Copy service files:
   ```bash
   sudo cp {output_dir / "lumina-feedback-loop.service"} /etc/systemd/system/
   sudo cp {output_dir / "lumina-feedback-loop.timer"} /etc/systemd/system/
   ```

2. Enable and start timer:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable lumina-feedback-loop.timer
   sudo systemctl start lumina-feedback-loop.timer
   ```

3. Check status:
   ```bash
   systemctl status lumina-feedback-loop.timer
   ```
"""

        instructions += f"""
### Option 3: Cron (Linux/Mac)
See: {cron_file.name}

Add to crontab:
```bash
crontab -e
# Then add the line from {cron_file.name}
```

## Verification

Run a test cycle:
```bash
python {run_script}
```

Check logs:
```bash
# Feedback history
{project_root}/data/lumina_feedback_loop/feedback_history.json

# Analysis report
python scripts/python/analyze_lumina_ots_scaling.py --full
```

## Monitoring

View recent feedback cycles:
```bash
python scripts/python/analyze_lumina_ots_scaling.py --full --output data/lumina_analysis_report.json
```
"""

        instructions_file.write_text(instructions)
        results['files_created'].append(str(instructions_file))

        logger.info(f"✅ Created {len(results['files_created'])} files in {output_dir}")

        return results
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in setup_automated_cycles: {e}", exc_info=True)
        raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup automated feedback cycles")
    parser.add_argument("--interval", type=int, default=1, help="Interval in hours (default: 1)")
    parser.add_argument("--platform", type=str, help="Platform (windows/linux, auto-detected if not provided)")
    parser.add_argument("--output-dir", type=Path, help="Output directory for scripts")

    args = parser.parse_args()

    results = setup_automated_cycles(
        interval_hours=args.interval,
        platform=args.platform
    )

    print("\n" + "="*60)
    print("✅ Automated Feedback Cycles Setup Complete!")
    print("="*60)
    print(f"\nPlatform: {results['platform']}")
    print(f"Interval: Every {results['interval_hours']} hour(s)")
    print(f"\nFiles created:")
    for file_path in results['files_created']:
        print(f"  - {file_path}")
    print(f"\nSetup instructions:")
    for instruction in results['instructions']:
        print(f"  {instruction}")
    print("\nSee SETUP_INSTRUCTIONS.md for detailed instructions.")


if __name__ == "__main__":


    main()