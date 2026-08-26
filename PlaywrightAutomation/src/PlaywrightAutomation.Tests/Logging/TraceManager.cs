using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.Playwright;

namespace PlaywrightAutomation.Tests.Logging
{
    public static class TraceManager
    {
        public static async Task StartTracingAsync(IBrowserContext context, string testName)
        {
            await context.Tracing.StartAsync(new TracingStartOptions
            {
                Title = testName,
                Screenshots = true,
                Snapshots = true,
                Sources = true
            });
        }

        public static async Task StopTracingAsync(IBrowserContext context, string testName, bool isFailure)
        {
            var traceDir = Path.Combine(AppContext.BaseDirectory, "traces");
            if (!Directory.Exists(traceDir))
            {
                Directory.CreateDirectory(traceDir);
            }

            var safeTestName = string.Join("_", testName.Split(Path.GetInvalidFileNameChars()));
            var tracePath = Path.Combine(traceDir, $"{safeTestName}_{DateTime.Now:yyyyMMdd_HHmmss}.zip");

            if (isFailure)
            {
                await context.Tracing.StopAsync(new TracingStopOptions
                {
                    Path = tracePath
                });
                Logger.Info($"Playwright Trace captured on failure: {tracePath}");
            }
            else
            {
                // Discard trace for passing tests to save disk space
                await context.Tracing.StopAsync(new TracingStopOptions());
            }
        }
    }
}
