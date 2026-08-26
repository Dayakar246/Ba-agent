using System;
using System.IO;
using AventStack.ExtentReports;
using AventStack.ExtentReports.Reporter;
using AventStack.ExtentReports.Reporter.Config;

namespace PlaywrightAutomation.Tests.Logging
{
    public static class ExtentReportManager
    {
        private static readonly Lazy<ExtentReports> InstanceLazy = new Lazy<ExtentReports>(InitExtentReports);
        public static ExtentReports Instance => InstanceLazy.Value;

        [ThreadStatic]
        private static ExtentTest? _currentTest;

        public static ExtentTest? CurrentTest
        {
            get => _currentTest;
            set => _currentTest = value;
        }

        private static ExtentReports InitExtentReports()
        {
            var reportDir = Path.Combine(AppContext.BaseDirectory, "reports");
            if (!Directory.Exists(reportDir))
            {
                Directory.CreateDirectory(reportDir);
            }

            var reportPath = Path.Combine(reportDir, "ExecutionReport.html");
            var sparkReporter = new ExtentSparkReporter(reportPath);
            sparkReporter.Config.DocumentTitle = "Playwright C# Test Execution Report";
            sparkReporter.Config.ReportName = "Automation Test Execution Summary";
            sparkReporter.Config.Theme = Theme.Standard;

            var extent = new ExtentReports();
            extent.AttachReporter(sparkReporter);
            extent.AddSystemInfo("OS", Environment.OSVersion.ToString());
            extent.AddSystemInfo("Framework", ".NET 8.0 / Playwright NUnit");
            extent.AddSystemInfo("Environment", Environment.GetEnvironmentVariable("TEST_ENVIRONMENT") ?? "Development");

            return extent;
        }

        public static ExtentTest CreateTest(string testName, string? category = null)
        {
            var test = Instance.CreateTest(testName);
            if (!string.IsNullOrEmpty(category))
            {
                test.AssignCategory(category);
            }
            _currentTest = test;
            return test;
        }

        public static void Flush()
        {
            Instance.Flush();
        }
    }
}
