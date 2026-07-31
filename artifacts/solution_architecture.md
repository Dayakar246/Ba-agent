# BA Agent Pro: Solution Architecture

This document provides a high-level architectural overview of the BA Agent Pro (Autonomous Delivery OS) platform. You can render the Mermaid diagram below to generate a detailed architectural schematic for management.

## System Architecture Diagram

```mermaid
graph TD
    %% Styling Definitions
    classDef frontend fill:#1e1e2e,stroke:#00f3ff,stroke-width:2px,color:#fff
    classDef backend fill:#1e1e2e,stroke:#b400ff,stroke-width:2px,color:#fff
    classDef aiLayer fill:#2b1b54,stroke:#ff00ea,stroke-width:2px,color:#fff
    classDef external fill:#1a2b3c,stroke:#00aeff,stroke-width:2px,color:#fff
    classDef db fill:#2c3e50,stroke:#f39c12,stroke-width:2px,color:#fff
    classDef tool fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff

    %% Components
    subgraph Frontend [Presentation Layer - React & Vite]
        UI[Glassmorphism UI]
        Dash[Command Center]
        Studios[Agentic Studios]
    end

    subgraph API [Integration & Routing Layer - FastAPI]
        Orchestrator[Multi-Agent Orchestrator]
        Endpoints[REST Endpoints]
        Telemetry[Telemetry Service\nLLMOps Interceptor]
    end

    subgraph Agents [Agentic Council - Python]
        Ingest[Extraction Agent]
        Ana[Analysis Agent]
        Arch[Architecture Agent]
        TRD[TRD Gen Agent]
        Backlog[Backlog Gen Agent]
        Gov[Approval & Audit Agent]
        Memory[Knowledge Agent]
        Auto[Automation Agent\n*Tool Empowered*]
    end

    subgraph AI_Core [LLM Routing & Tool Execution]
        Groq[Groq Llama 3.3 70B\nPrimary / High-Speed]
        AzureOpenAI[Azure OpenAI GPT-4o-mini\nTier-1 Fallback]
        AzureOpenAI[Azure OpenAI\nEmbeddings]
    end

    subgraph Data [Persistence Layer]
        PG[(PostgreSQL)\nState & Audit]
        AITelem[(PostgreSQL)\nAgent Telemetry Logs]
        AISearch[(Azure AI Search)\nVector Memory]
    end

    subgraph External [Enterprise Integrations]
        ADO[Azure DevOps]
        ACS[Azure Communication Services]
    end

    %% Connections
    UI --> |HTTP/REST| Endpoints
    Dash --> Endpoints
    Studios --> Endpoints
    
    Endpoints --> Orchestrator
    Orchestrator --> Agents
    
    Agents --> |Prompts/Context| AI_Core
    AI_Core --> |Tokens/Latency| Telemetry
    Telemetry --> |Write Metrics| AITelem
    
    AI_Core --> Groq
    AI_Core -.-> |Failover| AzureOpenAI
    AI_Core --> |Fallback/Embeddings| AzureOpenAI
    Memory --> |Semantic Indexing| AzureOpenAI
    AzureOpenAI --> |Vectors| AISearch
    Memory <--> |Query Context| AISearch
    
    Gov --> |Approval Workflows| ACS
    Backlog --> |Sync Epics/Stories| ADO
    
    Auto <--> |Function Calling| AI_Core
    Auto --> |Dynamic Tool Execution| ADO
    
    Orchestrator <--> |Save State| PG

    class UI,Dash,Studios frontend
    class Orchestrator,Endpoints,Telemetry backend
    class Ingest,Ana,Arch,TRD,Backlog,Gov,Memory,Auto aiLayer
    class Groq,AzureOpenAI aiLayer
    class ADO,ACS external
    class PG,AITelem,AISearch db
```

## Component Breakdown

### 1. Presentation Layer (Frontend)
- **Technology**: React, Vite, CSS (Glassmorphism).
- **Function**: Provides the "Command Center" dashboard and individual "Agentic Studios" (Gap Detective, Spec Architect, Flow Designer). It handles multimodal file drops (images, PDFs, text) and renders real-time Markdown and Mermaid logic.

### 2. Integration & Orchestration (Backend)
- **Technology**: Python, FastAPI.
- **Function**: Acts as the central nervous system. The `RequifyOrchestrator` manages the complex state transitions required for multi-agent handoffs. 
- **Observability (LLMOps)**: The newly integrated `TelemetryService` intercepts all LLM traffic to track token usage, latency (ms), and cost across all active agents.

### 3. Agentic Council
- **Technology**: Python Agent Classes.
- **Function**: A modular swarm of specialized personas. 
- **Autonomy Upgrade**: Select agents (like the `AutomationAgent`) are now upgraded with **Dynamic Tool Use**. Instead of running rigid Python scripts, they can formulate tool payloads (e.g., searching ADO for duplicates) and act autonomously based on real-time API responses.

### 4. AI Core (Redundant LLM Service)
- **Primary Engine**: Groq (Llama 3.3 70B) for ultra-fast, high-volume reasoning and function calling.
- **Enterprise Fallback**: Azure OpenAI (GPT-4o-mini) deployed as an automatic failover to guarantee 100% SLA, equipped with tool execution capabilities.
- **Multimodal & Embeddings**: Azure OpenAI for generating high-dimensional vector embeddings and fallback logic.

### 5. Persistence & Integration
- **Relational Data**: PostgreSQL handles immutable audit logs, approval session states, and highly granular **Agent Telemetry** logs for enterprise cost tracking.
- **Vector Memory**: Azure AI Search acts as the "Brain," storing historical requirements natively linked via semantic embeddings.
- **Enterprise Hooks**: Azure DevOps (via REST API) handles agile board synchronization, while Azure Communication Services dispatches formal review emails to stakeholders.
