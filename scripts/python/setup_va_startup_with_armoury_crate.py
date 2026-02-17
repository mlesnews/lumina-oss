#!/usr/bin/env python3
"""
Setup VA Startup with Armoury Crate

Creates a Windows scheduled task to start all Virtual Assistants
when Armoury Crate starts up (on boot/logon).

Tags: #STARTUP #VA #ARMOURY_CRATE #TASK_SCHEDULER @JARVIS @ACE @LUMINA
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupVAStartup")


def create_va_startup_task() -> Dict[str, Any]:
    """Create scheduled task to start VAs when Armoury Crate starts"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 SETTING UP VA STARTUP WITH ARMOURY CRATE")
        logger.info("=" * 80)
        logger.info("")

        script_path = project_root / "scripts" / "python" / "startup_vas_with_armoury_crate.py"
        python_exe = sys.executable

        if not script_path.exists():
            logger.error(f"❌ Startup script not found: {script_path}")
            return {
                "success": False,
                "error": "Startup script not found"
            }

        # Create task XML
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</Date>
    <Author>JARVIS - LUMINA VA Startup</Author>
    <Description>Starts all Virtual Assistants (JARVIS, ACE, etc.) when Armoury Crate starts up. Waits for Armoury Crate to be ready, then displays all VAs on desktop.</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
    </LogonTrigger>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT2M</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
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
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <DeleteExpiredTaskAfter>PT0S</DeleteExpiredTaskAfter>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{script_path}"</Arguments>
      <WorkingDirectory>"{project_root}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        # Save XML to file
        xml_file = project_root / "data" / "va_startup_with_armoury_crate_task.xml"
        xml_file.parent.mkdir(parents=True, exist_ok=True)

        with open(xml_file, 'w', encoding='utf-16') as f:
            f.write(task_xml)
            logger.info(f"✅ Task XML created: {xml_file.name}")
    except Exception as e:
        logger.error(f"❌ Error creating XML file: {e}")
        return {
            "success": False,
            "error": f"XML creation failed: {e}"
        }

        # Create the task using schtasks command directly (simpler approach)
        logger.info("")
        logger.info("STEP 1: Creating Windows scheduled task...")
        # Delete existing task if it exists
        subprocess.run(
            ['schtasks', '/Delete', '/TN', 'LUMINA-VA-Startup-With-ArmouryCrate', '/F'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Ignore errors if task doesn't exist

        # Create task using schtasks command (more reliable than XML)
        # Delay format: mmmm:ss (e.g., "0001:00" for 1 minute, "0002:00" for 2 minutes)
        result = subprocess.run(
            [
                'schtasks', '/Create',
                '/TN', 'LUMINA-VA-Startup-With-ArmouryCrate',
                '/TR', f'"{python_exe}" "{script_path}"',
                '/SC', 'ONLOGON',
                '/DELAY', '0001:00',  # 1 minute delay in mmmm:ss format
                '/RL', 'HIGHEST',
                '/F'
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info("✅ Logon trigger task created")

            # Also add boot trigger
            boot_result = subprocess.run(
                [
                    'schtasks', '/Create',
                    '/TN', 'LUMINA-VA-Startup-With-ArmouryCrate-Boot',
                    '/TR', f'"{python_exe}" "{script_path}"',
                    '/SC', 'ONSTART',
                    '/DELAY', '0002:00',  # 2 minute delay in mmmm:ss format
                    '/RL', 'HIGHEST',
                    '/F'
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if boot_result.returncode == 0:
                logger.info("✅ Boot trigger task created")

            logger.info("✅ Startup tasks created successfully")
            logger.info("   Task Names:")
            logger.info("     • LUMINA-VA-Startup-With-ArmouryCrate (On Logon, 1 min delay)")
            logger.info("     • LUMINA-VA-Startup-With-ArmouryCrate-Boot (On Boot, 2 min delay)")
            logger.info("")

            return {
                "success": True,
                "task_name": "LUMINA-VA-Startup-With-ArmouryCrate",
                "xml_file": str(xml_file),
                "message": "Startup tasks created successfully"
            }
        else:
            logger.error(f"❌ Failed to create task: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr
            }

    except subprocess.TimeoutExpired:
        logger.error("❌ Task creation timed out")
        return {
            "success": False,
            "error": "Task creation timed out"
        }
    except Exception as e:
            logger.error(f"❌ Error creating startup task: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    except Exception as e:
        logger.error(f"❌ Error in create_va_startup_task: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def verify_startup_task() -> bool:
    """Verify the startup task exists and is enabled"""
    try:
        result = subprocess.run(
            ['schtasks', '/Query', '/TN', 'LUMINA-VA-Startup-With-ArmouryCrate', '/FO', 'LIST', '/V'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.info("✅ Startup task verified and enabled")
            return True
        else:
            logger.warning("⚠️  Could not verify task (may not exist yet)")
            return False
    except Exception as e:
        logger.debug(f"Verification error: {e}")
        return False


def main():
    """Main setup function"""
    logger.info("=" * 80)
    logger.info("🌟 LUMINA VA STARTUP SETUP")
    logger.info("=" * 80)
    logger.info("")
    logger.info("This will create a Windows scheduled task that:")
    logger.info("  1. Waits for Armoury Crate to start")
    logger.info("  2. Starts all Virtual Assistants (JARVIS, ACE, etc.)")
    logger.info("  3. Displays all VAs on desktop")
    logger.info("")
    logger.info("The task will run:")
    logger.info("  • On user logon (1 minute delay)")
    logger.info("  • On system boot (2 minute delay)")
    logger.info("")

    # Create the task
    result = create_va_startup_task()

    if result.get("success"):
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SETUP COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("  1. Run the PowerShell script as Administrator:")
        logger.info("     scripts\\powershell\\Setup-VAStartupWithArmouryCrate.ps1")
        logger.info("  2. Reboot your laptop")
        logger.info("  3. Wait for Armoury Crate to start")
        logger.info("  4. All VAs should appear on desktop automatically")
        logger.info("")
        logger.info("⚠️  NOTE: Creating scheduled tasks requires Administrator privileges")
        logger.info("   The PowerShell script will handle this properly")
        logger.info("")

        # Verify
        verify_startup_task()

        logger.info("=" * 80)
        return 0
    else:
        logger.error("")
        logger.error("=" * 80)
        logger.error("❌ SETUP FAILED")
        logger.error("=" * 80)
        logger.error(f"   Error: {result.get('error', 'Unknown error')}")
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)