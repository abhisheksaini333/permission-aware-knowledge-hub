import os,threading,time
from pathlib import Path
from .database import open_store
from .service import KnowledgeHub
from .worker import IndexWorker

def build_hub(database_url,model_cache=None):
 store=open_store(database_url);encoder=None;generator=None
 if model_cache:
  from .models import MiniLMEncoder,FlanGenerator
  from .chain import GroundedChain
  root=Path(model_cache)
  encoder=MiniLMEncoder(str(root/"all-MiniLM-L6-v2"))
  generator=GroundedChain(FlanGenerator(str(root/"flan-t5-small")))
 return KnowledgeHub(store,encoder,generator)

def application():
 from .api import create_app
 from .settings import Settings
 hub=build_hub(Settings.from_env().database_url,os.getenv("MODEL_CACHE"))
 app=create_app(hub);stop=threading.Event()
 def loop():
  worker=IndexWorker(hub.store,hub.encoder)
  while not stop.is_set():
   if not worker.once():stop.wait(.25)
 thread=threading.Thread(target=loop,name="index-worker",daemon=True)
 @app.on_event("startup")
 def start():thread.start()
 @app.on_event("shutdown")
 def shutdown():
  stop.set();thread.join(timeout=10)
  if not thread.is_alive():hub.store.close()
 return app
