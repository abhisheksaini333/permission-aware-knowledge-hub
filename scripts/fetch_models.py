"""Fetch original model files and verify every byte before use."""
import argparse,json,sys,urllib.request,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from knowledge.artifacts import verify_file,target_path

def main():
 p=argparse.ArgumentParser();p.add_argument("destination");p.add_argument("--manifest",default="models/manifest.json");args=p.parse_args()
 for item in json.loads(Path(args.manifest).read_text()):
  target=target_path(args.destination,item)
  if verify_file(target,item):print("Verified",target.name);continue
  if target.exists():raise RuntimeError("Existing artifact failed checksum: "+str(target))
  target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_suffix(target.suffix+".part")
  for attempt in range(3):
   try:
    with urllib.request.urlopen(item["url"],timeout=90) as source,temp.open("wb") as out:
     total=0
     while chunk:=source.read(1024*1024):
      total+=len(chunk)
      if total>item["bytes"]:raise ValueError("Artifact exceeds expected size")
      out.write(chunk)
    if not verify_file(temp,item):raise ValueError("Artifact checksum mismatch")
    temp.replace(target);break
   except Exception:
    if temp.exists():temp.unlink()
    if attempt==2:raise
    time.sleep(2**attempt)
  print("Fetched and verified",target.name)
if __name__=="__main__":main()
