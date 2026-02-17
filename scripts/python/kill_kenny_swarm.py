import psutil
import os
import signal

def kill_swarm():
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and any('kenny_imva_enhanced' in arg for arg in cmdline):
                print(f"💀 Killing Kenny PID {proc.info['pid']}")
                os.kill(proc.info['pid'], signal.SIGTERM)
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    print(f"✅ Terminated {killed} Kenny instances.")

if __name__ == "__main__":
    kill_swarm()
