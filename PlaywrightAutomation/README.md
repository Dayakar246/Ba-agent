# Playwright C# Test Automation Framework

An enterprise-grade Playwright C# test automation framework targeting **.NET 8.0** and **NUnit**, built using the **Page Object Model (POM)** and **Business Step Workflow** patterns.

Includes multi-environment JSON configuration, structured Serilog logging, ExtentReports interactive HTML reporting, Playwright trace archive & failure screenshot capture, Polly retries, and CI/CD pipelines for GitHub Actions and Azure DevOps.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* **.NET 8.0 SDK** (or higher)
* **PowerShell 5.1+** (Windows PowerShell or `pwsh`)
* **Node.js** (optional, for viewing Playwright traces via `npx playwright show-trace`)

---

### 2. Environment Setup & Build

1. Navigate to the `PlaywrightAutomation` solution folder:
   ```powershell
   cd PlaywrightAutomation
   ```

2. Restore NuGet packages and build the solution:
   ```powershell
   dotnet build PlaywrightAutomation.sln
   ```

3. Install Playwright browser binaries (one-time setup per machine):
   ```powershell
   powershell -ExecutionPolicy Bypass -File src/PlaywrightAutomation.Tests/bin/Debug/net8.0/playwright.ps1 install
   ```

---

### 3. Running Tests

#### Run All Tests
```powershell
dotnet test --logger "trx;LogFileName=test_results.trx"
```

#### Run Tests for a Specific Environment
Set the `TEST_ENVIRONMENT` variable to load `appsettings.{Environment}.json`:
```powershell
# Windows PowerShell
$env:TEST_ENVIRONMENT="Staging"; dotnet test

# CMD
set TEST_ENVIRONMENT=Staging && dotnet test

# Linux/macOS
TEST_ENVIRONMENT=Staging dotnet test
```

#### Run Tests by Category
```powershell
dotnet test --filter "Category=Authentication"
```

#### Run Tests in Parallel
NUnit parallel execution is configured at fixture level (`[Parallelizable(ParallelScope.Self)]`). Pass worker thread count via CLI if needed:
```powershell
dotnet test --NUnit.NumberOfTestWorkers=4
```

---

## 📁 Framework Architecture & Folder Structure

```text
PlaywrightAutomation/
├── PlaywrightAutomation.sln
├── NuGet.Config
├── README.md
└── src/
    └── PlaywrightAutomation.Tests/
        ├── Config/               # appsettings.json, appsettings.Staging.json, EnvironmentConfig.cs
        ├── Pages/                # BasePage.cs, LoginPage.cs, DashboardPage.cs (POM layer)
        ├── Steps/                # BaseSteps.cs, AuthSteps.cs (Reusable workflow steps)
        ├── Selectors/            # CommonSelectors.cs (Aria & UI locator constants)
        ├── Utilities/            # WaitHelpers.cs, RetryHelper.cs (Polly), ApiHelper.cs, StorageStateHelper.cs
        ├── Logging/              # Logger.cs (Serilog), ExtentReportManager.cs, TraceManager.cs
        ├── Tests/                # BaseTest.cs (NUnit fixture hooks), LoginTests.cs, DashboardTests.cs
        ├── CODING_STANDARDS.md   # Naming conventions, selector priorities, and style rules
        └── PlaywrightAutomation.Tests.csproj
```

---

## 📊 Logging, Reporting & Diagnostics

### 1. Structured Logging (Serilog)
All test actions, navigations, step descriptions, and errors are logged via Serilog to:
* **Console:** Live stdout stream during execution.
* **File:** Saved under `src/PlaywrightAutomation.Tests/bin/Debug/net8.0/logs/execution_yyyyMMdd_HHmmss.log`.
* **TestContext:** Attached to NUnit test execution output.

### 2. Interactive HTML Reports (ExtentReports)
Generates an interactive execution report after every run at:
`src/PlaywrightAutomation.Tests/bin/Debug/net8.0/reports/ExecutionReport.html`

### 3. Failure Screenshots & Playwright Traces
When a test fails, `BaseTest.cs` automatically:
* Captures a full-page screenshot in `src/PlaywrightAutomation.Tests/bin/Debug/net8.0/reports/screenshots/`.
* Saves a Playwright Trace zip in `src/PlaywrightAutomation.Tests/bin/Debug/net8.0/traces/`.

To inspect a Playwright trace interactively:
```powershell
npx playwright show-trace src/PlaywrightAutomation.Tests/bin/Debug/net8.0/traces/<trace_filename>.zip
```

---

## 🔄 CI/CD Pipelines

* **GitHub Actions:** `.github/workflows/playwright.yml`
* **Azure DevOps:** `azure-pipelines.yml`

Both pipelines automatically build the project, install Playwright browser dependencies, execute test suites, publish TRX test results, and attach HTML ExtentReports and trace archives as build artifacts.

---

## 📜 Coding Standards

For detailed coding standards, naming conventions, selector priorities (`GetByRole`, `GetByTestId`), and Playwright best practices, refer to [`src/PlaywrightAutomation.Tests/CODING_STANDARDS.md`](file:///c:/Users/VMADMIN/Videos/SURYA/baagent/PlaywrightAutomation/src/PlaywrightAutomation.Tests/CODING_STANDARDS.md).
