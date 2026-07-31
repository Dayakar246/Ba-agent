# Frontend Developer Guide: Requify Agent Pro Pages & Routing

Welcome to the team! This document details the frontend implementation of Requify Agent Pro. It is designed to get you up to speed quickly on each of the 12 sidebar menus, mapping them to their corresponding frontend components, backend APIs, specialized agents, and testing procedures.

---

## 1. Page-by-Page Architectural Breakdown

### 1. Command Center
*   **Purpose**: The central dashboard of the platform, showing recent ingestion runs, high-level metrics, and options to resume previous analyst sessions.
*   **Business Functionality**: Gives leaders and senior analysts a birds-eye view of requirement ingestion rates, success statistics of DevOps synchronization, and overall project compliance status.
*   **React Component**: `DashboardView` (inline in [frontend/src/App.jsx#L863-L992](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L863-L992)).
*   **Backend API(s) Called**:
    *   `GET /documents`
    *   `GET /analyses`
    *   `GET /project-context`
    *   `GET /sprint-metrics`
*   **Backend Agent/Service**:
    *   `/documents` and `/analyses` perform direct queries to the DB using SQLAlchemy models (`Document` and `Analysis` in [backend/models/models.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/models/models.py)).
    *   `/project-context` is handled by `ContextAgent` ([backend/agents/context_agent.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/context_agent.py)) which manages the "Project DNA" contexts stored in the DB.
    *   `/sprint-metrics` is handled by `AnalyticsAgent` ([backend/agents/analytics_agent.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/analytics_agent.py)) which fetches sprint statistics.
*   **User Input**:
    *   Dashboard filter tabs ("Documents" vs "Analyses") to switch the table data.
    *   Clicking "Resume Discovery" on a specific analysis.
*   **Output Displayed**:
    *   Key metric cards: Ingestion count, Governance (Analyses) count, and SDLC velocity.
    *   Hover-expandable "Project DNA" and "Sprint Planning" drawers.
    *   Table listing historical documents or analyses showing their reference name, ID, date, status, and Action button ("Resume Discovery").
*   **How to Test Locally**:
    *   *Sample Input*: Select the "Analyses" tab, find an item, and click "Resume Discovery".
    *   *Expected Output*: The UI switches view to the dynamic step-by-step workflow (`currentView === 'workflow'`) and populates the historical extraction, specs, backlog, and reviews.
    *   *API Flow*: UI calls `GET http://127.0.0.1:8000/analysis/{analysis_id}` to fetch details $\rightarrow$ loads previous state into React hooks.

---

### 2. Institutional Memory
*   **Purpose**: Search and browse domain-specific requirements, compliance guidelines, and technical patterns.
*   **Business Functionality**: Provides RAG (Retrieval-Augmented Generation) lookup to align new business specifications with corporate standards, preventing double-work and ensuring consistency.
*   **React Component**: `KnowledgeVaultView` (inline in [frontend/src/App.jsx#L3296-L3369](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L3296-L3369)).
*   **Backend API(s) Called**:
    *   `GET /knowledge/search?q={query}`
*   **Backend Agent/Service**:
    *   `KnowledgeAgent` ([backend/agents/knowledge_agent.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/knowledge_agent.py)) performs a semantic vector search (against ChromaDB or a mock database).
*   **User Input**: A search query string typed in the hero search box.
*   **Output Displayed**: A summary of semantic requirements indexed, and a markdown article displaying the retrieved and synthesized intelligence matches.
*   **How to Test Locally**:
    *   *Sample Input*: Type "MFA auth rules" and press "Query Brain".
    *   *Expected Output*: A markdown explanation displaying MFA validation rules.
    *   *API Flow*: UI calls `GET http://127.0.0.1:8000/knowledge/search?q=MFA%20auth%20rules` $\rightarrow$ handled by `KnowledgeAgent` $\rightarrow$ returns text results.

---

### 3. Discovery Swarm
*   **Purpose**: The main orchestration launchpad to initiate a full multi-agent analysis session on a new document.
*   **Business Functionality**: Transforms raw documents or recordings into structured engineering requirements, technical specifications, process flows, prioritizations, and test suites.
*   **React Component**: `SelectionView` (inline in [frontend/src/App.jsx#L995-L1144](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L995-L1144)).
*   **Backend API(s) Called**:
    *   `POST /ingest` (Ingestion node)
    *   `POST /analyze` (Gap Detective / Council node)
    *   `POST /generate-functional-spec` (Spec Architect node)
    *   `POST /generate-backlog` (Backlog node)
    *   `POST /api/agents/draft-test-cases` (Test Case node)
*   **Backend Agent/Service**:
    *   FastAPI endpoints delegate to the **LangGraph** workflow ([backend/graph/workflow.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/graph/workflow.py) and [nodes.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/graph/nodes.py)) and agent classes (`ExtractionAgent`, `AmbiguityAgent`, `AnalysisAgent`, `CriticAgent`, `FunctionalSpecAgent`, `BacklogGenAgent`, `TestCaseAgent`).
*   **User Input**:
    *   Channel selection (Document upload, Direct text input, wireframe image upload, or zoom transcript file).
    *   Target context (Line of Business - LOB chip selector).
    *   Optional target tech stack / integration context.
    *   Toolkit Configuration checkmarks (enabling/disabling Gap Analysis, Functional Spec, Backlog, and Test Cases).
*   **Output Displayed**: Initiates and steps through the `WorkflowView` rendering the current progress of each agent step in real-time, showing completed status nodes and final review packages.
*   **How to Test Locally**:
    *   *Sample Input*: Select LOB "Personal Auto", enable all agents, upload a sample BRD PDF, and click "Analyze Document".
    *   *Expected Output*: Transitions to step-by-step progress nodes showing extraction complete, gaps scanned, spec generated, and backlog items mapped.
    *   *API Flow*: `POST /ingest` (runs `ExtractionAgent` & `AmbiguityAgent`) $\rightarrow$ if ambiguities are found, interrupts to show `ClarificationView` $\rightarrow$ `POST /analyze` (runs `AnalysisAgent` / Council reviewers) $\rightarrow$ `POST /generate-functional-spec` (runs `FunctionalSpecAgent`) $\rightarrow$ `POST /generate-backlog` (runs `BacklogGenAgent`) $\rightarrow$ `POST /api/agents/draft-test-cases` (runs `TestCaseAgent`).

---

### 4. Quick Backlog
*   **Purpose**: Directly convert a raw Business Requirements Document (BRD) file into a backlog and draft test cases, bypassing the full multi-agent spec generation workflow to save time.
*   **Business Functionality**: Provides rapid backlog creation for simple projects, allowing quick sizing and effort estimates without needing to run the full, heavier analysis council.
*   **React Component**: `DirectBacklogView` ([frontend/src/components/Views/DirectBacklogView.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/Views/DirectBacklogView.jsx)).
*   **Backend API(s) Called**:
    *   `POST /generate-backlog-direct`
    *   `POST /generate-testcases-direct`
*   **Backend Agent/Service**:
    *   `BacklogGenAgent` ([backend/agents/backlog_gen.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/backlog_gen.py)) and `TestCaseAgent` ([backend/agents/test_case_agent.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/test_case_agent.py)) handle the request directly without stepping through the LangGraph workflow structure.
*   **User Input**: Drag-and-drop or select a BRD file (PDF or text).
*   **Output Displayed**: Metric summaries (Epics, Features, User Stories, Tasks count) and an interactive, editable tree diagram of the backlog hierarchy.
*   **How to Test Locally**:
    *   *Sample Input*: Drag a sample text file describing features of a CRM system and hit "Generate Backlog".
    *   *Expected Output*: The generated backlog grid populated with Epics and User stories.
    *   *API Flow*: Hits `POST /generate-backlog-direct` $\rightarrow$ processes text $\rightarrow$ outputs JSON backlog structure.

---

### 5. Backlog Explorer
*   **Purpose**: A search-and-inspect dashboard to view and manage work items that currently exist in the linked Azure DevOps project.
*   **Business Functionality**: Allows BAs to query live items, verify assignments and statuses, and update titles, assignees, and descriptions directly from the BA tool.
*   **React Component**: `WorkItemsView` (inline in [frontend/src/App.jsx#L2316-L2535](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2316-L2535)).
*   **Backend API(s) Called**:
    *   `GET /ado-work-items`
    *   `GET /ado-iterations`
    *   `GET /ado-team`
    *   `PATCH /update-ado-work-item`
*   **Backend Agent/Service**:
    *   `AzureDevOpsService` ([backend/services/ado_service.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/services/ado_service.py)) maps the calls directly to the Azure DevOps REST API.
*   **User Input**:
    *   Filters: Item type selector (All, Epic, Feature, User Story, Task) and Sprint selection.
    *   Row clicks to open item details.
    *   Modal edits: modifying title, assignee, or description.
*   **Output Displayed**: Interactive table of live ADO items, and a details/edit modal featuring a rich technical description view.
*   **How to Test Locally**:
    *   *Sample Input*: Select "Task" filter pill, click on a row, click "Edit in ADO", modify the title, and click "Save to ADO".
    *   *Expected Output*: The item details update, the modal saves, and the main grid reflects the new title.
    *   *API Flow*: `GET /ado-work-items` $\rightarrow$ selection $\rightarrow$ `PATCH /update-ado-work-item` (sends ID and fields) $\rightarrow$ refreshes table.

---

### 6. Governance Matrix
*   **Purpose**: Ensures end-to-end traceability of project artifacts.
*   **Business Functionality**: Provides visual mapping of each source requirement from the business document to the corresponding generated user stories, synchronized Azure DevOps item IDs, and QA test scenario numbers.
*   **React Component**: `TraceabilityMatrixView` (inline in [frontend/src/App.jsx#L3178-L3294](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L3178-L3294)).
*   **Backend API(s) Called**:
    *   `GET /documents`
    *   `GET /traceability/{document_id}`
    *   `GET /reports/traceability/{document_id}`
*   **Backend Agent/Service**:
    *   Handled via SQL database logic matching the cached extraction, backlog, and test case JSON artifacts from `storage_service` and `models.py`.
    *   `/reports/traceability/{document_id}` is handled by `ReportService` ([backend/services/report_service.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/services/report_service.py)) which outputs a downloadable governance PDF.
*   **User Input**: Dropdown selection of an ingested project/document.
*   **Output Displayed**: Grid mapping requirements side-by-side with user stories, ADO IDs, and test suites. A "Download Governance Report (PDF)" button.
*   **How to Test Locally**:
    *   *Sample Input*: Select a document from the dropdown.
    *   *Expected Output*: A table detailing the requirements lineage.
    *   *API Flow*: Hits `GET /traceability/{document_id}` $\rightarrow$ aggregates JSON payloads $\rightarrow$ returns mapping array.

---

### 7. Gap Detective
*   **Purpose**: Standalone studio to perform gap analysis and threat/risk assessment on a specification file.
*   **Business Functionality**: Stress-tests requirements against corporate business rules and developer constraints before coding, finding holes early when they are cheap to fix.
*   **React Component**: `GapDetectiveView` (inline in [frontend/src/App.jsx#L2596-L2720](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2596-L2720)).
*   **Backend API(s) Called**:
    *   `POST /ingest`
    *   `POST /analyze` (filtering `enabled_modules=['gaps']`)
*   **Backend Agent/Service**:
    *   `AnalysisAgent` ([backend/agents/analysis.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/analysis.py)), `CriticAgent` ([backend/agents/critic_agent.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/critic_agent.py)), and the specialist reviewers.
*   **User Input**: Drag-and-drop file upload.
*   **Output Displayed**: BRD quality score badge, the Critic's adversarial warnings, parallel persona review comments, and list cards of identified gaps.
*   **How to Test Locally**:
    *   *Sample Input*: Upload a requirements document for an auto insurance quote system.
    *   *Expected Output*: Scan screen finishes and displays gaps (e.g. "Missing coverage options details") and persona notes.
    *   *API Flow*: `POST /ingest` $\rightarrow$ `POST /analyze` $\rightarrow$ parses JSON gaps output.

---

### 8. Functional Architect
*   **Purpose**: Standalone studio to convert simple bullet-point requirements into a structured, formal Technical Requirements Document (TRD).
*   **Business Functionality**: Automates technical design writing, producing standardized spec blueprints (Overview, Architecture, Security, Performance, Error Handling) ready for engineers.
*   **React Component**: `SpecArchitectView` (inline in [frontend/src/App.jsx#L2722-L2837](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2722-L2837)).
*   **Backend API(s) Called**:
    *   `POST /ingest`
    *   `POST /analyze`
    *   `POST /generate-functional-spec`
*   **Backend Agent/Service**:
    *   `FunctionalSpecAgent` ([backend/agents/functional_spec.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/functional_spec.py)).
*   **User Input**: Spec source document upload.
*   **Output Displayed**: A Markdown preview editor rendering the completed TRD, with a "Download .md" button.
*   **How to Test Locally**:
    *   *Sample Input*: Upload a text sheet of features and click "Launch Architect".
    *   *Expected Output*: A rendered Markdown document containing structured sections (System Overview, Error Handling, etc.).
    *   *API Flow*: Ingests $\rightarrow$ baseline analyze $\rightarrow$ calls `POST /generate-functional-spec` to run the agent.

---

### 9. Flow Designer
*   **Purpose**: Standalone tool to translate requirements logic into visual diagrams.
*   **Business Functionality**: Produces process flows and sequence diagrams representing logical decision points, clarifying business rules for QA and Dev teams.
*   **React Component**: `FlowDesignerView` (inline in [frontend/src/App.jsx#L2839-L2950](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2839-L2950)).
*   **Backend API(s) Called**:
    *   `POST /ingest`
    *   `POST /analyze` (filtering `enabled_modules=['flow']`)
*   **Backend Agent/Service**:
    *   `DiagramAgent` ([backend/agents/diagram_gen.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/diagram_gen.py)).
*   **User Input**: File upload containing business rules (e.g. payment flow instructions).
*   **Output Displayed**: Visual flow chart rendered via Mermaid.js, list of process nodes, and a "Copy Mermaid Code" button.
*   **How to Test Locally**:
    *   *Sample Input*: Upload a step-by-step description of an invoice approval cycle.
    *   *Expected Output*: Mermaid flow diagram showing Start $\rightarrow$ Step 1 $\rightarrow$ Decision $\rightarrow$ End nodes.
    *   *API Flow*: Ingestion $\rightarrow$ `POST /analyze` returns a diagram JSON containing lists of nodes and edges $\rightarrow$ frontend renders them.

---

### 10. Test Case Agent
*   **Purpose**: Generates functional testing test cases and Playwright test automation scripts from stories.
*   **Business Functionality**: Accelerates QA cycles by providing automated test drafts and web test scripts right out of requirements design.
*   **React Component**: `TestCaseAgentView` ([frontend/src/components/Views/TestCaseAgentView.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/Views/TestCaseAgentView.jsx)).
*   **Backend API(s) Called**:
    *   `GET /ado-work-items`
    *   `POST /api/qa/generate`
    *   `POST /api/qa/sync`
*   **Backend Agent/Service**:
    *   `TestCaseAgent` ([backend/agents/test_case_agent.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/agents/test_case_agent.py)) coordinates formatting, runs a critic review on the tests, and handles ADO syncing.
*   **User Input**:
    *   Clicking a work item from the backlog panel list on the left.
    *   Clicking "Generate Tests".
    *   Clicking "Sync to Azure DevOps".
*   **Output Displayed**: Rendered test scenario lists, priorities, and TypeScript code panels; sync status badge.
*   **How to Test Locally**:
    *   *Sample Input*: Select "User Story 101" from the left pane and click "Generate Tests".
    *   *Expected Output*: Display of manual BDD steps and a generated TypeScript test block.
    *   *API Flow*: Hits `GET /ado-work-items` to load the list $\rightarrow$ `POST /api/qa/generate` $\rightarrow$ triggers `TestCaseAgent.generate_tests_for_workitem()` $\rightarrow$ returns tests.

---

### 11. Sprint Planner
*   **Purpose**: Organize work items into sprints.
*   **Business Functionality**: Helps the scrum master plan and distribute stories across sprints while viewing real-time effort allocations.
*   **React Component**: `SprintPlannerView` ([frontend/src/components/Views/SprintPlannerView.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/Views/SprintPlannerView.jsx)).
*   **Backend API(s) Called**:
    *   `GET /api/sprint-planning/backlog`
    *   `GET /api/sprint-planning/iterations`
    *   `POST /api/sprint-planning/assign`
*   **Backend Agent/Service**:
    *   `AzureDevOpsService` ([backend/services/ado_service.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/services/ado_service.py)).
*   **User Input**: Selecting work items, selecting target sprint, and clicking "Assign".
*   **Output Displayed**: Backlog grid, sprint list boxes showing points capacity, and drag-and-drop allocations.
*   **How to Test Locally**:
    *   *Sample Input*: Check the box next to User Story #12, select "Sprint 1" from the dropdown, and hit "Assign to Sprint".
    *   *Expected Output*: Selected items move out of the unassigned list and show up under Sprint 1's effort score.
    *   *API Flow*: Hitting `POST /api/sprint-planning/assign` triggers `ado.assign_to_sprint()`.

---

### 12. LLMOps Telemetry
*   **Purpose**: Admin monitoring board for the application's AI expenses and latencies.
*   **Business Functionality**: Provides cost governance and token analytics to prevent runaway API fees.
*   **React Component**: `TelemetryDashboard` ([frontend/src/components/TelemetryDashboard.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/TelemetryDashboard.jsx)).
*   **Backend API(s) Called**:
    *   `GET /api/telemetry`
*   **Backend Agent/Service**:
    *   Direct SQLAlchemy query to the `AgentTelemetry` table in [backend/models/models.py](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/backend/models/models.py).
*   **User Input**: Refresh actions.
*   **Output Displayed**: Logs table listing every AI prompt call, token details, model provider (Groq/Azure), latency in milliseconds, dollar cost, and success status.
*   **How to Test Locally**:
    *   *Sample Input*: Open the page and inspect the grid.
    *   *Expected Output*: Row logs showing details of recent generation tasks.
    *   *API Flow*: Hits `GET /api/telemetry` $\rightarrow$ loads items from database table `telemetry_logs`.

---

## 2. Sidebar Lookup Table

| Sidebar Menu | React Component | Backend API | Backend Agent | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Command Center** | `DashboardView` ([App.jsx:L863](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L863)) | `GET /documents`, `GET /analyses`, `GET /project-context`, `GET /sprint-metrics` | `ContextAgent`, `AnalyticsAgent` | Central dashboard showing session status and high-level KPIs. |
| **Institutional Memory** | `KnowledgeVaultView` ([App.jsx:L3296](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L3296)) | `GET /knowledge/search` | `KnowledgeAgent` | Search business rules and compliance requirements via RAG. |
| **Discovery Swarm** | `SelectionView` ([App.jsx:L995](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L995)) | `POST /ingest`, `POST /analyze`, `POST /generate-functional-spec`, `POST /generate-backlog`, `POST /api/agents/draft-test-cases` | LangGraph workflow swarm | Primary launch page for full end-to-end multi-agent discovery. |
| **Quick Backlog** | `DirectBacklogView` ([DirectBacklogView.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/Views/DirectBacklogView.jsx)) | `POST /generate-backlog-direct`, `POST /generate-testcases-direct` | `BacklogGenAgent`, `TestCaseAgent` | Fast BRD-to-backlog translation without generating specs first. |
| **Backlog Explorer** | `WorkItemsView` ([App.jsx:L2316](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2316)) | `GET /ado-work-items`, `GET /ado-iterations`, `GET /ado-team`, `PATCH /update-ado-work-item` | `AzureDevOpsService` | Inspect and edit work items directly inside the connected ADO board. |
| **Governance Matrix** | `TraceabilityMatrixView` ([App.jsx:L3178](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L3178)) | `GET /traceability/{id}`, `GET /reports/traceability/{id}` | Database / `ReportService` | Audit requirement lineage mapping specs, stories, and test suites. |
| **Gap Detective** | `GapDetectiveView` ([App.jsx:L2596](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2596)) | `POST /ingest`, `POST /analyze` | `AnalysisAgent`, `CriticAgent` | Standalone requirements scanner checking for technical gaps. |
| **Functional Architect** | `SpecArchitectView` ([App.jsx:L2722](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2722)) | `POST /ingest`, `POST /analyze`, `POST /generate-functional-spec` | `FunctionalSpecAgent` | Standalone blueprint engine to write full Technical Requirements specs. |
| **Flow Designer** | `FlowDesignerView` ([App.jsx:L2839](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/App.jsx#L2839)) | `POST /ingest`, `POST /analyze` | `DiagramAgent` | Standalone logic visualization generating Mermaid.js charts. |
| **Test Case Agent** | `TestCaseAgentView` ([TestCaseAgentView.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/Views/TestCaseAgentView.jsx)) | `GET /ado-work-items`, `POST /api/qa/generate`, `POST /api/qa/sync` | `TestCaseAgent` | QA panel to draft BDD scenarios and copy Playwright scripts. |
| **Sprint Planner** | `SprintPlannerView` ([SprintPlannerView.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/Views/SprintPlannerView.jsx)) | `GET /api/sprint-planning/backlog`, `GET /api/sprint-planning/iterations`, `POST /api/sprint-planning/assign` | `AzureDevOpsService` | Allocate backlog items to active team iterations. |
| **LLMOps Telemetry** | `TelemetryDashboard` ([TelemetryDashboard.jsx](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/frontend/src/components/TelemetryDashboard.jsx)) | `GET /api/telemetry` | Database logs | Track token usage, API latency, and operational expense logs. |

---

## 3. Recommended Code Exploration Path

To quickly master this codebase, explore the pages in this order:

1.  **Discovery Swarm (`SelectionView`)**: Focus on how files are ingested and how the modular checkmarks configure the downstream pipeline. This maps directly to the FastAPI `/ingest` route.
2.  **Workflow Processing (`WorkflowView`)**: Study how React steps through stages using `activeStep` and renders intermediate agent metrics.
3.  **Backlog Tree (`BacklogTree`)**: Explore this to see how multi-layered JSON hierarchies (Epics $\rightarrow$ Features $\rightarrow$ Stories $\rightarrow$ Tasks) are handled, edited, and committed.
4.  **Test Case Agent (`TestCaseAgentView`)**: Focus here for QA enhancements. Trace how stories are parsed, and how the Critic Loop formats BDD and Playwright TypeScript outputs.
5.  **Backlog Explorer (`WorkItemsView`) & Sprint Planner (`SprintPlannerView`)**: Look at how bidirectional REST requests sync edits back to Azure DevOps.
6.  **Governance Matrix (`TraceabilityMatrixView`)**: See how requirements are linked end-to-end for compliance audits.
