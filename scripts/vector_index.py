"""Explicitly configure the vector index after backing up the database."""
import argparse, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from knowledge.database import open_store

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("strategy", choices=["exact", "ivfflat"])
    args=parser.parse_args()
    store=open_store(os.environ["DATABASE_URL"])
    try:
        if not hasattr(store,"configure_vector_index"):
            raise SystemExit("Vector indexes require PostgreSQL")
        print(store.configure_vector_index(args.strategy))
    finally: store.close()
