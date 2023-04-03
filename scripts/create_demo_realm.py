"""Write a local Keycloak import file; the password comes from the environment."""
import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from knowledge.demo_identity import realm
if __name__=="__main__":
 target=Path(sys.argv[1] if len(sys.argv)>1 else ".runtime/realm.json")
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(realm(os.environ["DEMO_PASSWORD"]),indent=2)+"\n")
 target.chmod(0o600)
 print("Created local identity import; keep it private.")
