import os
import json
import asyncio
from services.llm_service import LLMService
from services.vector_service import VectorSearchService

class KnowledgeAgent:
    """
    The 'Hidden Brain' of Requify.
    Manages Organizational Memory and Domain Knowledge via Azure AI Search.
    """
    def __init__(self):
        self.llm = LLMService()
        self.vector_store = VectorSearchService()
        print("--- [SUCCESS] KnowledgeAgent initialized with Azure AI Search Integration ---")

    async def _get_embedding(self, text: str) -> list:
        """
        Generates a vector embedding for the text using Azure OpenAI.
        """
        return await self.llm.get_embeddings(text)

    async def ingest_project_requirements(self, doc_id: str, extraction: dict, lob: str = "General"):
        """
        Indexes extracted requirements into the organizational memory.
        """
        if not self.vector_store.endpoint: 
            print("--- [WARN] KnowledgeAgent: Vector Store endpoint is MISSING. Indexing skipped. ---")
            return 0
        
        reqs = extraction.get("functional_requirements", [])
        print(f"--- [DEBUG] KnowledgeAgent: Processing {len(reqs)} requirements for Doc: {doc_id} ---")
        indexed_count = 0
        
        for req in reqs:
            content = req.get("description", "")
            req_id = req.get("id", "UNKNOWN")
            
            # Generate Embedding
            vector = await self._get_embedding(content)
            
            # Index to Azure
            try:
                await self.vector_store.index_requirement(
                    doc_id=doc_id,
                    req_id=req_id,
                    content=content,
                    lob=lob,
                    vector=vector
                )
                indexed_count += 1
            except Exception as e:
                print(f"--- [ERROR] KnowledgeAgent: Failed to index requirement {req_id}: {e} ---")
                
            # Rate limiting delay to avoid 429 Too Many Requests from Azure AI Search
            await asyncio.sleep(0.5)
            
        print(f"--- [SUCCESS] KnowledgeAgent: Successfully indexed {indexed_count}/{len(reqs)} requirements to Azure. ---")
        return indexed_count

    async def sync_vault(self):
        """
        Migrates existing requirements from the DB to Azure AI Search.
        This is a 'Catch-up' mechanism to ensure the index is always populated.
        """
        if not self.vector_store.endpoint: return
        
        from services.db_service import SessionLocal
        from models.models import Document
        
        db = SessionLocal()
        try:
            docs = db.query(Document).all()
            print(f"--- [INFO] Syncing Vault: Found {len(docs)} documents to re-index. ---")
            
            total_indexed = 0
            for doc in docs:
                if doc.meta and "extraction" in doc.meta:
                    extraction = doc.meta["extraction"]
                    # We pass 'General' as fallback LOB if not found in doc
                    lob = doc.meta.get("lob", "General")
                    count = await self.ingest_project_requirements(doc.id, extraction, lob=lob)
                    total_indexed += count
            
            print(f"--- [SUCCESS] Vault Synchronization Complete. Total requirements indexed: {total_indexed} ---")
        except Exception as e:
            print(f"--- [ERROR] Vault Sync Failed: {e} ---")
        finally:
            db.close()

    async def retrieve_relevant_context(self, query_text: str, lob: str = "General", n_results: int = 3):
        """
        Searches both past requirements AND official P&C domain guidelines.
        Returns a unified markdown context block.
        """
        if not self.vector_store.endpoint: 
            return "Organizational Memory is currently disabled (Missing Azure Search Config)."
        
        query_vector = await self._get_embedding(query_text)
        
        # Check if the embedding silently failed (returned all zeros)
        if sum(query_vector) == 0.0:
            return "ERROR: Failed to generate search embedding. Please verify your AZURE_OPENAI_EMBEDDING_KEY and AZURE_OPENAI_EMBEDDING_DEPLOYMENT in the Azure App Service Environment Variables."
        
        # 1. Search Past Requirements (Institutional Memory)
        past_reqs = await self.vector_store.search_memory(query_vector, top=n_results)
        
        # 2. Search Domain Guidelines (P&C Insurance Rules)
        guidelines = await self.vector_store.search_guidelines(query_vector, lob=lob, top=n_results)
        
        context = ""
        found_knowledge = False
        
        if past_reqs:
            found_knowledge = True
            context += "\n### RELEVANT INSTITUTIONAL MEMORY (Similar Past Projects)\n"
            for req in past_reqs:
                context += f"- [{req.get('lob', 'General')}] Req {req.get('requirement_id', 'Unknown')}: {req.get('content', '')}\n"
                
        if guidelines:
            found_knowledge = True
            context += "\n### OFFICIAL P&C DOMAIN GUIDELINES\n"
            for rule in guidelines:
                file_name = rule.get('doc_id', 'Manual')
                context += f"- [Source: {file_name}] {rule.get('content', '')}\n"
                
        if not found_knowledge:
            return "No domain guidelines or similar past requirements found in memory."
            
        # Format the raw text into a readable response using the LLM
        formatting_prompt = f"""
        You are an expert Property & Casualty Insurance Knowledge Assistant.
        The user asked: "{query_text}"
        
        Here is the raw information retrieved from the enterprise knowledge base:
        {context}
        
        Please synthesize and format this information into a clean, highly readable Markdown response. 
        - Directly answer the user's question using ONLY the provided text.
        - Remove any repetitive or messy proprietary disclaimers (e.g. "All Information contained herein is proprietary & confidential...").
        - Use bolding, bullet points, and headers to make the text easy to read.
        - Clearly cite the [Source: File Name] at the bottom.
        """
        
        try:
            formatted_response = await self.llm.call(formatting_prompt, provider="azure")
            return formatted_response
        except Exception as e:
            # Fallback to raw text if LLM formatting fails
            print(f"WARN: LLM formatting failed, returning raw text: {e}")
            return context
