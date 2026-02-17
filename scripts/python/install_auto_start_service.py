#!/usr/bin/env python3
"""
Install Auto-Start Service

Installs the local AI auto-start service to run on system boot.

Tags: #INSTALL #SERVICE #AUTO_START @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path

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

logger = get_logger("InstallAutoStartService")


def create_windows_task():
    """Create Windows Task Scheduler task"""
    import subprocess

    script_path = project_root / "scripts" / "python" / "auto_start_local_ai_services.py"
    python_exe = sys.executable

    # Create task XML
    task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
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
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{script_path}" --daemon</Arguments>
      <WorkingDirectory>"{project_root}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

    # Save XML
    xml_file = project_root / "data" / "local_ai_auto_start_task.xml"
    xml_file.parent.mkdir(parents=True, exist_ok=True)
    with open(xml_file, 'w', encoding='utf-16') as f:
        f.write(task_xml)

    # Create task
    try:
        result = subprocess.run(
            ["schtasks", "/Create", "/TN", "LuminaLocalAIAutoStart", "/XML", str(xml_file), "/F"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ Windows Task Scheduler task created")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to create task: {e.stderr}")
        return False


def create_linux_service():
    """Create Linux systemd service"""
    script_path = project_root / "scripts" / "python" / "auto_start_local_ai_services.py"
    python_exe = sys.executable

    service_content = f"""[Unit]
Description=Lumina Local AI Auto-Start Service
After=network.target docker.service

[Service]
Type=simple
User={Path.home().name}
WorkingDirectory={project_root}
ExecStart={python_exe} {script_path} --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_file = project_root / "data" / "lumina-local-ai.service"
    service_file.parent.mkdir(parents=True, exist_ok=True)
    with open(service_file, 'w') as f:
        f.write(service_content)

    logger.info(f"✅ Systemd service file created: {service_file}")
    logger.info("   To install: sudo cp {service_file} /etc/systemd/system/")
    logger.info("   Then: sudo systemctl enable lumina-local-ai.service")
    logger.info("   Then: sudo systemctl start lumina-local-ai.service")

    return True


def main():
    """Main execution"""
    import platform

    print("=" * 80)
    print("🔧 INSTALL AUTO-START SERVICE")
    print("=" * 80)
    print()

    system = platform.system()

    if system == "Windows":
        print("Installing Windows Task Scheduler task...")
        if create_windows_task():
            print("✅ Auto-start service installed successfully")
            print("   Task Name: LuminaLocalAIAutoStart")
            print("   The service will start on system boot")
        else:
            print("❌ Failed to install auto-start service")
    elif system == "Linux":
        print("Creating Linux systemd service...")
        if create_linux_service():
            print("✅ Systemd service file created")
            print("   Follow the instructions above to install")
        else:
            print("❌ Failed to create service file")
    else:
        print(f"⚠️  Unsupported system: {system}")
        print("   Please manually configure auto-start")


if __name__ == "__main__":


    main()