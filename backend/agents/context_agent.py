import json
from datetime import datetime, timedelta
from services.ado_service import AzureDevOpsService
from services.llm_service import LLMService
from models.models import ProjectContext

class ContextAgent:
    """
    Project DNA Architect.
    Manages long-term memory, institutional knowledge, and user preferences.
    """
    def __init__(self):
        self.ado = AzureDevOpsService()
        self.llm = LLMService()
        self.cached_summary = None

    async def get_dna(self, db, dna_type: str = "GENERAL"):
        """
        Retrieves specific institutional knowledge from the DNA Vault.
        """
        project_name = self.ado.project
        dna_record = db.query(ProjectContext).filter(
            ProjectContext.id == project_name,
            ProjectContext.dna_type == dna_type
        ).first()
        
        if dna_record:
            return dna_record.context_text
        return None

    async def get_project_context(self, db=None, force_refresh: bool = False):
        """
        Scans existing ADO project to build the 'Base DNA'.
        Uses persistent DB caching (10 days) to minimize AI load.
        """
        project_name = self.ado.project
        
        # 1. Check persistent DB cache first
        if db and not force_refresh:
            db_context = db.query(ProjectContext).filter(
                ProjectContext.id == project_name,
                ProjectContext.dna_type == "GENERAL"
            ).first()
            if db_context:
                age = datetime.utcnow() - db_context.last_scan_date
                if age < timedelta(days=10):
                    print(f"--- Using persistent Project DNA from Vault ({age.days} days old) ---")
                    return db_context.context_text

        # 2. Fresh Scan
        print(f"--- Performing fresh scan for project: {project_name} ---")
        try:
            items = await self.ado.get_all_work_items()
            if not items:
                return "New Project: No existing work items found in ADO."

            # Summarize the existing scope to keep the prompt small
            summary_data = [
                {"id": i["id"], "title": i["title"], "type": i["type"], "status": i["status"]}
                for i in items[:50] 
            ]

            prompt = f"""
            Below is a list of existing work items from an Azure DevOps project ({project_name}).
            Summarize the current functional scope of the project in 3-5 bullet points.
            Include any recurring technical patterns or terminology used.
            
            Existing Items:
            {json.dumps(summary_data, indent=2)}
            """
            
            summary = await self.llm.call(prompt, provider="azure")
            
            if db:
                db_context = db.query(ProjectContext).filter(
                    ProjectContext.id == project_name,
                    ProjectContext.dna_type == "GENERAL"
                ).first()
                if not db_context:
                    db_context = ProjectContext(id=project_name, dna_type="GENERAL")
                    db.add(db_context)
                
                db_context.context_text = summary
                db_context.last_scan_date = datetime.utcnow()
                db.commit()
                print(" Project DNA Vault updated.")

            return summary
        except Exception as e:
            print(f"WARN: Failed to scan project context: {e}")
            return "Context Unavailable: Proceeding with document-only analysis."
