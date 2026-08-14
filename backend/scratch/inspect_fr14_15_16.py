import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import SessionLocal
from models.models import Document, Analysis

db = SessionLocal()
try:
    target_analysis = db.query(Analysis).filter(Analysis.id == "f514a740-cc12-410d-b1d9-2e2d9db30525").first()
    if not target_analysis:
        target_analysis = db.query(Analysis).filter(Analysis.document_id == "fe30d725-dacc-4654-a13b-ee8ad49d3742").first()

    if target_analysis:
        print(f"Target Analysis Found: {target_analysis.id} (Doc ID: {target_analysis.document_id})")
        extraction = target_analysis.extraction or (target_analysis.results.get("extraction") if target_analysis.results else {})
        frs = extraction.get("functional_requirements", [])
        print(f"Total Requirements Extracted: {len(frs)}")
        for fr in frs:
            rid = fr.get("id") or fr.get("req_id")
            if rid in ["FR-014", "FR-015", "FR-016", "REQ-014", "REQ-015", "REQ-016"]:
                print(f"\n  Extraction Item {rid}: {fr}")

        # Inspect Critic Findings JSON
        critic = target_analysis.critic_review or (target_analysis.results.get("critic_review") if target_analysis.results else {})
        print("\n--- Critic Review Findings ---")
        print(json.dumps(critic, indent=2))
    else:
        print("Target analysis not found directly, showing latest 5 analyses:")
        for a in db.query(Analysis).all()[-5:]:
            print(f"  * ID: {a.id} | DocID: {a.document_id}")
finally:
    db.close()
