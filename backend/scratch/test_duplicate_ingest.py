import os
import sys
import asyncio
import hashlib
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(dotenv_path=env_path)

from services.db_service import SessionLocal
from models.models import Document, ProjectStateModel

def test_hash_logic():
    print("\n================================================================================")
    print(" [TEST: SHA-256 DUPLICATE DETECTION LOGIC]")
    print("================================================================================")

    sample_content = b"Sample Commercial Property Requirement BRD PDF Content v1.0"
    sample_hash = hashlib.sha256(sample_content).hexdigest()
    print(f" -> Sample File Hash: {sample_hash}")

    db = SessionLocal()
    try:
        # Check existing documents for matching hash
        all_docs = db.query(Document).all()
        print(f" -> Total Documents in DB: {len(all_docs)}")

        matched_doc = None
        for doc in all_docs:
            if doc.meta and isinstance(doc.meta, dict) and doc.meta.get("file_hash") == sample_hash:
                matched_doc = doc
                break

        if matched_doc:
            print(f" -> Match Found in DB! Doc ID: {matched_doc.id}")
            print(f" -> DUPLICATE DETECTED -> Skipping expensive AI processing.")
        else:
            print(f" -> No Match Found -> Proceeding with new document ingestion flow.")

        print("\n================================================================================")
        print(" [TEST COMPLETE]")
        print("================================================================================\n")
    finally:
        db.close()

if __name__ == "__main__":
    test_hash_logic()
