"""Explicitly configure the vector index after backing up the database."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from knowledge.database import open_store


def configure(store, strategy, upgrade=False):
    if not hasattr(store, "configure_vector_index"):
        raise ValueError("Vector indexes require PostgreSQL")
    if upgrade:
        store.upgrade_vector_extension()
    return store.configure_vector_index(strategy)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("strategy", choices=["exact", "ivfflat", "hnsw"])
    parser.add_argument(
        "--upgrade-extension",
        action="store_true",
        help="Explicitly upgrade installed vector 0.4.0 to 0.5.0 before indexing",
    )
    args = parser.parse_args()
    store = open_store(os.environ["DATABASE_URL"])
    try:
        print(configure(store, args.strategy, args.upgrade_extension))
    finally:
        store.close()
