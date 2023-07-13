import os,subprocess,sys,stat
from pathlib import Path

def test_identity_export_protects_parent_directory_and_allows_container_read(tmp_path):
 target=tmp_path/"private"/"realm.json";env={**os.environ,"DEMO_PASSWORD":"a-long-test-only-password"}
 subprocess.run([sys.executable,"scripts/create_demo_realm.py",str(target)],env=env,check=True,capture_output=True)
 assert stat.S_IMODE(target.parent.stat().st_mode)==0o700
 assert stat.S_IMODE(target.stat().st_mode)==0o644
