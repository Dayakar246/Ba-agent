# BA Agent Pro - Enterprise Installation & Deployment Guide 🚀
**Document Version**: 2.5.1  
**Target Audience**: Executive Leadership, CISO, Solution Architects, Enterprise Infrastructure Engineers, DevOps Teams  
**Solution**: BA Agent Pro (Requify Agent Pro - Intelligent Enterprise Discovery & Governance Engine)

---

## 🏛️ Section 1: Executive Summary & High-Level Deployment Roadmap

### 1.1 Management Overview & Value Proposition
**BA Agent Pro** is an enterprise AI engine designed to automate pre-development workflows—converting raw requirements (BRD/PRD) into engineering-ready user stories, technical specifications (TRD), and visual process models directly synced with Azure DevOps.

#### Executive Highlights
- **60% Turnaround Acceleration**: Dramatically shortens discovery to backlog execution cycles.
- **Strict Microsoft Entra ID Security**: Uses 100% Entra ID OAuth 2.0 (Azure AD) tokens for Azure DevOps. **Zero Personal Access Tokens (PATs)** allowed.
- **Zero-Knowledge Privacy Shield**: Automatic PII masking before external AI processing.
- **Traceability & Governance**: Automated Requirement Traceability Matrix (RTM) linking source text to ADO work items with immutable audit logging.

---

### 1.2 High-Level 5-Phase Deployment Roadmap (3-4 Days Turnkey)

```mermaid
flowchart LR
    P1["Phase 1: Day 1<br/>Security & Identity Governance"] --> P2["Phase 2: Day 1-2<br/>Network & Infrastructure"]
    P2 --> P3["Phase 3: Day 2-3<br/>App & AI Engine Deploy"]
    P3 --> P4["Phase 4: Day 3<br/>Schema & Vector Migration"]
    P4 --> P5["Phase 5: Day 4<br/>Verification & Sign-off"]
```

| Phase | Milestone Name | Key Objective & Activities | Primary Responsibility |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Security & Identity Governance** | Register App in Entra ID, assign ADO Service Principal permissions, eliminate PAT risks. | IAM / Security Team |
| **Phase 2** | **Network & Subnet Provisioning** | Create isolated subnets, configure firewall outbound FQDN rules, provision PostgreSQL DB. | Infrastructure Team |
| **Phase 3** | **App & AI Engine Deployment** | Deploy FastAPI backend, React dashboard, and configure Key Vault environment secrets. | DevOps / App Team |
| **Phase 4** | **Schema & Storage Migration** | Run `migrate.py` DB script, initialize persistent vector store for RAG context caching. | DB Admin / Architect |
| **Phase 5** | **Verification & CISO Sign-off** | Validate ADO sync via `/ado-work-items`, perform sample BRD upload, obtain final acceptance. | CISO & Lead Architect |

---

### 1.3 Governance & RACI Responsibility Matrix

| Deployment Task | Security / IAM | Network / Infra | DevOps / Engineering | DB Admin | Management Sign-off |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Entra ID App Registration** | **A / R** | C | I | - | I |
| **ADO Service Principal Permissions** | **A / R** | C | I | - | I |
| **VNet & Firewall Whitelisting** | C | **A / R** | I | - | I |
| **PostgreSQL Database Provisioning** | - | C | I | **A / R** | - |
| **App Service / Container Deployment** | - | C | **A / R** | I | - |
| **End-to-End ADO Sync Verification** | I | I | **A / R** | - | **Sign-off** |

*Legend: **A** = Accountable, **R** = Responsible, **C** = Consulted, **I** = Informed*

---

## 🏗️ Section 2: Technical Architecture & Network Topology

```mermaid
flowchart TD
    subgraph Client ["Client Boundary"]
        User["Browser Client"]
    end

    subgraph DMZ ["DMZ / Ingress Layer"]
        AGW["Application Gateway / WAF"]
    end

    subgraph AppVNet ["Application VNet (Private Subnet)"]
        FE["Frontend Service (Port 443 / 5173)"]
        BE["Backend FastAPI API (Port 8000)"]
        MCP["MCP Azure DevOps Server"]
    end

    subgraph DataSubnet ["Data Subnet (Isolated)"]
        DB["PostgreSQL DB (Port 5432)"]
        VEC["ChromaDB Vector Storage"]
    end

    subgraph External ["External Cloud & Sovereign Services"]
        EntraID["Microsoft Entra ID / Azure AD"]
        ADO["Azure DevOps Services"]
        Groq["Groq AI Cloud"]
        AOAI["Azure OpenAI Service"]
    end

    User -->|HTTPS 443| AGW
    AGW -->|HTTPS 443| FE
    FE -->|REST API 8000| BE
    BE -->|SQL 5432| DB
    BE -->|Internal File Access| VEC
    BE -->|Stdio Process| MCP
    MCP -->|Bearer Token / HTTPS 443| EntraID
    MCP -->|HTTPS 443| ADO
    BE -->|HTTPS 443| Groq
    BE -->|HTTPS 443| AOAI
```

---

## 💻 Section 3: Hardware & Software Prerequisites

### Hardware Specifications

| Component | Minimum Specification | Recommended Specification (Production) |
| :--- | :--- | :--- |
| **CPU** | 4 vCPU | 8 vCPU |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 50 GB SSD | 100 GB NVMe SSD |
| **OS** | Ubuntu 22.04 LTS / RHEL 8+ / Windows Server 2022 | Ubuntu 22.04 LTS / Azure Linux |

### Software Prerequisites

| Software | Version Required | Notes |
| :--- | :--- | :--- |
| **Python** | `3.10.x` or `3.11.x` | Required for FastAPI backend & MCP server |
| **Node.js** | `18.x` or `20.x` (LTS) | Required for React/Vite frontend build |
| **PostgreSQL** | `14.0+` or Azure Flexible Server | PostgreSQL DB engine |
| **Docker** | `24.0+` | Required if deploying via containers |
| **Docker Compose** | `2.20+` | Container orchestration |

---

## 🌐 Section 4: Network Architecture & Security Requirements

### Inbound Firewall Rules

| Source | Destination | Protocol / Port | Purpose |
| :--- | :--- | :--- | :--- |
| Client Browsers / Users | Application Gateway / Frontend | TCP / 443 (HTTPS) | Web Interface Access |
| Frontend Subnet | Backend API Subnet | TCP / 8000 (HTTP/HTTPS) | Internal REST API Communication |
| Backend API Subnet | Database Subnet | TCP / 5432 | PostgreSQL Database Connection |

### Outbound Network Rules & FQDN Whitelist

| FQDN / Endpoint Domain | Port / Protocol | Category | Technical Purpose |
| :--- | :--- | :--- | :--- |
| `login.microsoftonline.com` | TCP / 443 (HTTPS) | Identity & Access | Microsoft Entra ID OAuth 2.0 token acquisition |
| `dev.azure.com` | TCP / 443 (HTTPS) | DevOps Integration | Azure DevOps REST API calls |
| `*.dev.azure.com` | TCP / 443 (HTTPS) | DevOps Integration | Azure DevOps Organization endpoints |
| `*.visualstudio.com` | TCP / 443 (HTTPS) | DevOps Integration | Azure DevOps legacy organization URLs |
| `management.azure.com` | TCP / 443 (HTTPS) | Cloud Management | Azure Managed Identity token discovery |
| `api.groq.com` | TCP / 443 (HTTPS) | External AI Engine | Requirement extraction & reasoning |
| `<your-resource>.openai.azure.com` | TCP / 443 (HTTPS) | Azure AI Service | Azure OpenAI Embeddings & Vision parsing |
| `pypi.org`, `files.pythonhosted.org` | TCP / 443 (HTTPS) | Deployment / Build | Python package installation (`pip`) |
| `registry.npmjs.org` | TCP / 443 (HTTPS) | Deployment / Build | Frontend package installation (`npm`) |

---

## 🔐 Section 5: Microsoft Entra ID Setup for Azure DevOps (No PAT)

> [!CAUTION]
> **Enterprise Compliance Directive**: Personal Access Tokens (PATs) are strictly disabled. The solution connects to Azure DevOps exclusively using **Microsoft Entra ID (Azure AD)** OAuth 2.0 / Service Principal Bearer tokens.

### Step 5.1: Register Application in Microsoft Entra ID
1. Log in to [Azure Portal](https://portal.azure.com) ➔ **Microsoft Entra ID** ➔ **App registrations** ➔ **+ New registration**.
2. Name: `BA-Agent-Pro-ADO-Connector`.
3. Note **Application (client) ID** (`AZURE_CLIENT_ID`) and **Directory (tenant) ID** (`AZURE_TENANT_ID`).

### Step 5.2: Create Client Secret or Assign Managed Identity
- **Option A (Secret)**: Go to **Certificates & secrets** ➔ **+ New client secret** ➔ Copy value (`AZURE_CLIENT_SECRET`).
- **Option B (Managed Identity)**: Enable System-Assigned Managed Identity on Azure App Service / VM.

### Step 5.3: Grant Azure DevOps Organization & Project Permissions
1. Go to Azure DevOps (`https://dev.azure.com/{Org}`) ➔ **Organization Settings** ➔ **Users** ➔ **Service Principals**.
2. Add `BA-Agent-Pro-ADO-Connector` with **Access Level**: `Basic`.
3. Open target Project (`https://dev.azure.com/{Org}/{Project}`) ➔ **Project Settings** ➔ **Permissions**.
4. Grant `Contributor` rights and allow **Create work items** & **Edit work items**.

### Step 5.4: Audience & OAuth Scope
- **Resource Scope**: `499b84ac-1321-427f-aa17-267ca6975798/.default`
- **Header**: `Authorization: Bearer <Entra_ID_Token>`

---

## 🗄️ Section 6: Database Setup & Schema Migration

### Step 6.1: Provision PostgreSQL Database
```sql
CREATE DATABASE baagent_db;
CREATE USER baagent_user WITH ENCRYPTED PASSWORD 'ComplexPass#2026!';
GRANT ALL PRIVILEGES ON DATABASE baagent_db TO baagent_user;
```

### Step 6.2: Execute Database Migrations
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python migrate.py
```

---

## ⚙️ Section 7: Environment Variables Matrix

| Variable Name | Required | Default / Example Value | Description |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | **Yes** | `postgresql://baagent_user:Pass@localhost:5432/baagent_db` | Connection string for PostgreSQL database |
| `ADO_ORGANIZATION` | **Yes** | `https://dev.azure.com/my-org-name` | Full Azure DevOps Organization URL |
| `ADO_PROJECT` | **Yes** | `Enterprise-Platform` | Target Azure DevOps Project Name |
| `AZURE_TENANT_ID` | **Yes** | `a1b2c3d4-e5f6-7890-abcd-1234567890ab` | Microsoft Entra ID Tenant ID |
| `AZURE_CLIENT_ID` | **Yes** | `f8e7d6c5-b4a3-2109-dcba-0987654321fe` | Entra ID App Client ID or Managed Identity Client ID |
| `AZURE_CLIENT_SECRET` | Conditional | `secret_value_here` | Entra ID Client Secret (Not needed for Managed Identity) |
| `GROQ_API_KEY` | **Yes** | `gsk_...` | API Key for Groq Llama-3.1 engine |
| `AZURE_OPENAI_KEY` | **Yes** | `azure_openai_key_here` | Key for Azure OpenAI Embeddings & Vision |
| `AZURE_OPENAI_ENDPOINT` | **Yes** | `https://my-ai.openai.azure.com/` | Azure OpenAI Resource Endpoint URL |
| `FRONTEND_URL` | **Yes** | `https://baagent.customer.com` | Production Frontend domain for CORS whitelist |
| `PORT` | No | `8000` | Backend web server port |

---

## 🚀 Section 8: Detailed Technical Installation Options

### Option A: Azure Enterprise Cloud Deployment (Recommended)
1. **Backend (App Service)**: Linux Python 3.11, Startup Command: `gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 --worker-class uvicorn.workers.UvicornWorker main:app`.
2. **Frontend (Static Web App)**: App location `/frontend`, Output location `dist`, Environment Variable `VITE_API_BASE_URL`.

### Option B: Docker Containerized Deployment
```bash
docker-compose up -d --build
```

### Option C: On-Premises / VM Deployment
Use `gunicorn` systemd service unit file + Nginx reverse proxy SSL configuration.

---

## 🔍 Section 9: Verification, Testing & Diagnostics

1. **Context Health Endpoint Check**: `curl -i https://<backend-url>/project-context`
2. **Entra ID ADO Connection Test**: `curl -i https://<backend-url>/ado-work-items`
3. **Troubleshooting Entra ID Issues**: Check `HTTP 401/403` or `AADSTS` error codes in diagnostic matrix.
