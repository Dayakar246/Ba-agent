using System;
using System.IO;
using System.Threading.Tasks;
using AventStack.ExtentReports;
using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;
using NUnit.Framework.Interfaces;
using PlaywrightAutomation.Tests.Config;
using PlaywrightAutomation.Tests.Logging;

namespace PlaywrightAutomation.Tests.Tests.Base
{
    [TestFixture]
    [Parallelizable(ParallelScope.Self)]
    public abstract class BaseTest : PageTest
    {
        protected ExtentTest? TestNode;

        public override BrowserNewContextOptions ContextOptions()
        {
            var options = base.ContextOptions() ?? new BrowserNewContextOptions();
            options.ViewportSize = new ViewportSize { Width = 1920, Height = 1080 };
            options.IgnoreHTTPSErrors = true;
            return options;
        }

        [OneTimeSetUp]
        public void GlobalSetup()
        {
            Logger.Info("Initializing Test Suite Execution...");
        }

        [SetUp]
        public async Task Setup()
        {
            var testName = TestContext.CurrentContext.Test.Name;
            var category = TestContext.CurrentContext.Test.ClassName;
            TestNode = ExtentReportManager.CreateTest(testName, category);
            Logger.Info($"=== Starting Test: {testName} ===");

            if (EnvironmentConfig.Options.RecordTrace)
            {
                await TraceManager.StartTracingAsync(Context, testName);
            }
        }

        [TearDown]
        public async Task Teardown()
        {
            var testName = TestContext.CurrentContext.Test.Name;
            var resultStatus = TestContext.CurrentContext.Result.Outcome.Status;
            var errorMessage = TestContext.CurrentContext.Result.Message;
            var isFailure = resultStatus == TestStatus.Failed;

            if (isFailure)
            {
                Logger.Error($"Test FAILED: {testName}. Reason: {errorMessage}");
                TestNode?.Fail($"Test Failed: {errorMessage}");

                if (EnvironmentConfig.Options.ScreenshotOnFailure)
                {
                    try
                    {
                        var screenshotsDir = Path.Combine(AppContext.BaseDirectory, "reports", "screenshots");
                        if (!Directory.Exists(screenshotsDir))
                        {
                            Directory.CreateDirectory(screenshotsDir);
                        }

                        var screenshotPath = Path.Combine(screenshotsDir, $"{testName}_{DateTime.Now:yyyyMMdd_HHmmss}.png");
                        await Page.ScreenshotAsync(new PageScreenshotOptions { Path = screenshotPath, FullPage = true });
                        Logger.Info($"Failure screenshot saved to: {screenshotPath}");
                        TestNode?.AddScreenCaptureFromPath(screenshotPath);
                    }
                    catch (Exception ex)
                    {
                        Logger.Error("Failed to capture screenshot during teardown", ex);
                    }
                }
            }
            else
            {
                Logger.Info($"Test PASSED: {testName}");
                TestNode?.Pass("Test Execution Passed Successfully.");
            }

            if (EnvironmentConfig.Options.RecordTrace)
            {
                await TraceManager.StopTracingAsync(Context, testName, isFailure);
            }
        }

        [OneTimeTearDown]
        public void GlobalTeardown()
        {
            Logger.Info("Flushing ExtentReports HTML Report...");
            ExtentReportManager.Flush();
        }
    }
}
