import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch
)

class VectorSearchService:
    def __init__(self, index_name: str = "requirement-memory"):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = index_name
        
        if self.endpoint and self.key:
            self.credential = AzureKeyCredential(self.key)
            self.index_client = SearchIndexClient(endpoint=self.endpoint, credential=self.credential)
            self.search_client = SearchClient(endpoint=self.endpoint, index_name=self.index_name, credential=self.credential)
            self.guidelines_client = SearchClient(endpoint=self.endpoint, index_name="insurance-guidelines", credential=self.credential)
            self._index_initialized = False

    def _ensure_initialized(self):
        if not getattr(self, '_index_initialized', False):
            try:
                self.create_index_if_not_exists()
                self._index_initialized = True
            except Exception as e:
                print(f"WARN: Could not auto-initialize Azure Index '{self.index_name}': {e}")

    def create_index_if_not_exists(self):
        """
        Creates the Azure AI Search index schema for vectors.
        """
        if not self.endpoint: return
        
        # We use a universal schema that works for both requirement-memory and insurance-guidelines
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="requirement_id", type=SearchFieldDataType.String, filterable=True), # Can be empty for guidelines
            SearchableField(name="doc_id", type=SearchFieldDataType.String, filterable=True), # Can be filename
            SearchableField(name="lob", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True), # e.g. Personal Lines
            # Vector field for semantic search (1536 dims for OpenAI embeddings)
            SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True, vector_search_dimensions=1536, vector_search_profile_name="my-vector-profile"),
            SimpleField(name="metadata", type=SearchFieldDataType.String)
        ]

        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="my-hnsw")],
            profiles=[VectorSearchProfile(name="my-vector-profile", algorithm_configuration_name="my-hnsw")]
        )

        index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search)
        
        try:
            self.index_client.create_or_update_index(index)
            print(f"SUCCESS: Azure AI Search Index '{self.index_name}' is ready.")
        except Exception as e:
            print(f"ERROR creating index '{self.index_name}': {e}")

    async def index_requirement(self, doc_id: str, req_id: str, content: str, lob: str, vector: list):
        """
        Uploads a single requirement to the organizational memory.
        """
        if not self.endpoint: return
        self._ensure_initialized()
        
        document = {
            "id": f"{doc_id}-{req_id}".replace("/", "-"),
            "content": content,
            "requirement_id": req_id,
            "doc_id": doc_id,
            "lob": lob,
            "content_vector": vector,
            "metadata": "{}"
        }
        
        try:
            self.search_client.upload_documents(documents=[document])
        except Exception as e:
            print(f"ERROR indexing document: {e}")
            raise e

    async def search_memory(self, query_vector: list, top: int = 3):
        """
        Performs vector search to find similar past requirements.
        """
        if not self.endpoint: return []
        self._ensure_initialized()
        
        try:
            results = self.search_client.search(
                search_text=None,
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_vector,
                    "fields": "content_vector",
                    "k": top
                }],
                select=["content", "lob", "requirement_id"]
            )
            return [r for r in results]
        except Exception as e:
            print(f"ERROR searching memory: {e}")
            return []

    async def search_guidelines(self, query_vector: list, lob: str = "General", top: int = 2):
        """
        Performs vector search against the official insurance guidelines index.
        """
        if not self.endpoint: return []
        self._ensure_initialized()
        
        try:
            # Build search params
            search_params = {
                "search_text": None,
                "vector_queries": [{
                    "kind": "vector",
                    "vector": query_vector,
                    "fields": "content_vector",
                    "k": top
                }],
                "select": ["content", "lob", "category", "doc_id"]
            }
            
            # Apply LOB filter if provided (exact match or Contains)
            if lob and lob != "General":
                # Assuming 'lob' field in index might be "2.2 Commercial" or "BOP"
                # Using simple eq or search.ismatch for partial matching
                search_params["filter"] = f"search.ismatch('{lob}', 'lob')"
                
            results = self.guidelines_client.search(**search_params)
            return [r for r in results]
        except Exception as e:
            print(f"ERROR searching guidelines: {e}")
            return []
