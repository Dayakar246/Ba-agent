# Playwright C# Test Automation Coding Standards & Guidelines

This document establishes coding standards, folder structures, naming conventions, and best practices for maintaining the Playwright C# test automation framework.

---

## 1. Directory & Folder Structure

All test automation assets are structured under `src/PlaywrightAutomation.Tests/`:

```text
src/PlaywrightAutomation.Tests/
├── Config/               # Multi-environment appsettings.json and options models
├── Pages/                # Page Object Model (POM) classes inheriting BasePage
├── Steps/                # Business workflow step classes encapsulating multi-page logic
├── Selectors/            # Reusable UI locators and CSS/XPath/Aria constants
├── Utilities/            # Dynamic waiters, Polly retries, API helpers, storage state
├── Logging/              # Serilog logger wrapper, ExtentReports manager, Playwright Trace manager
└── Tests/                # NUnit test fixtures inheriting BaseTest
```

---

## 2. Naming Conventions

* **Classes & Interfaces:** Use `PascalCase`.
  * Page Objects must be suffixed with `Page` (e.g., `LoginPage.cs`, `DashboardPage.cs`).
  * Step classes must be suffixed with `Steps` (e.g., `AuthSteps.cs`).
  * Test classes must be suffixed with `Tests` (e.g., `LoginTests.cs`).
* **Methods:** Use `PascalCase`.
  * Async methods **MUST** end with the `Async` suffix (e.g., `LoginAsync()`, `ClickSubmitAsync()`).
  * Test methods should follow the pattern: `Test[Feature]_[ExpectedBehavior]` (e.g., `TestValidLogin_Succeeds()`).
* **Properties & Fields:**
  * Public properties and Locators: `PascalCase` (e.g., `public ILocator UsernameInput => ...`).
  * Private fields: `camelCase` with leading underscore (e.g., `private readonly IPage _page;`).
* **Constants:** Use `PascalCase` or `UPPER_SNAKE_CASE`.

---

## 3. Playwright & Locator Best Practices

1. **Accessibility-First Locators:** Always prefer Playwright's user-facing accessibility locators in this priority:
   1. `GetByRole` (e.g., `GetByRole(AriaRole.Button, new PageGetByRoleOptions { Name = "Login" })`)
   2. `GetByTestId` (e.g., `GetByTestId("submit-btn")`)
   3. `GetByLabel`, `GetByPlaceholder`, `GetByText`
   4. CSS / XPath (Use **only** as a last resort when semantic locators are unavailable).
2. **Explicit Async Await:** EVERY Playwright method returning a `Task` must be awaited (`await Page.ClickAsync(...)`).
3. **No Hardcoded Sleep:** Never use `Thread.Sleep()`. Rely on Playwright's built-in auto-waiting or custom dynamic waiters (`WaitHelpers`).
4. **Strict Separation of Concerns:**
   * **Pages:** Define element locators and atomic UI interactions. Do **NOT** place NUnit assertions (`Assert.That`) inside Page classes.
   * **Steps:** Combine page interactions into domain workflows (e.g., login, checkout).
   * **Tests:** Execute step flows and perform clean NUnit assertions.

---

## 4. Logging & Failure Diagnostics

* Use `Logger.Info()`, `Logger.Warn()`, and `Logger.Error()` across Pages and Steps to track execution progress.
* Ensure all test failures auto-capture:
  1. Full-page screenshot attached to ExtentReports (`reports/screenshots/`).
  2. Playwright Trace archive (`traces/*.zip`).
  3. Serilog console & file log entries (`logs/execution.log`).

---

## 5. Code Review Checklist

Before opening a Pull Request:
- [ ] Code builds cleanly with zero warnings or errors (`dotnet build`).
- [ ] All async methods have `Async` suffix and `await` keyword.
- [ ] Page objects contain no NUnit assertions.
- [ ] Test methods have `[Test]` and `[Description]` attributes.
- [ ] New locators prioritize `GetByRole` or `GetByTestId`.
- [ ] CI pipeline passes successfully in GitHub Actions / Azure DevOps.
