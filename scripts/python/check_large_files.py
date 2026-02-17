import sys
from pathlib import Path
sys.path.insert(0, 'scripts/python')
from jarvis_storage_engineering_team import StorageEngineeringTeam

team = StorageEngineeringTeam(Path('.'))
large_files = team.find_large_files(min_size_gb=0.1)
print(f'Found {len(large_files)} files > 100MB')
for f in large_files[:20]:
    print(f' - {f["path"]} ({f["size_gb"]}GB)')
