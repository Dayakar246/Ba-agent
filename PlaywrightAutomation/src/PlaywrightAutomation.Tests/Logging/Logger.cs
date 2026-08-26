using System;
using System.IO;
using NUnit.Framework;
using Serilog;

namespace PlaywrightAutomation.Tests.Logging
{
    public static class Logger
    {
        private static readonly Serilog.ILogger LogInstance;

        static Logger()
        {
            var logDir = Path.Combine(AppContext.BaseDirectory, "logs");
            if (!Directory.Exists(logDir))
            {
                Directory.CreateDirectory(logDir);
            }

            var logFilePath = Path.Combine(logDir, $"execution_{DateTime.Now:yyyyMMdd_HHmmss}.log");

            LogInstance = new LoggerConfiguration()
                .MinimumLevel.Debug()
                .WriteTo.Console()
                .WriteTo.File(logFilePath, rollingInterval: RollingInterval.Day, outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}")
                .CreateLogger();
        }

        public static void Info(string message)
        {
            LogInstance.Information(message);
            TestContext.Progress.WriteLine($"[INFO] {message}");
        }

        public static void Warn(string message)
        {
            LogInstance.Warning(message);
            TestContext.Progress.WriteLine($"[WARN] {message}");
        }

        public static void Error(string message, Exception? ex = null)
        {
            if (ex != null)
            {
                LogInstance.Error(ex, message);
                TestContext.Progress.WriteLine($"[ERROR] {message} | Exception: {ex.Message}");
            }
            else
            {
                LogInstance.Error(message);
                TestContext.Progress.WriteLine($"[ERROR] {message}");
            }
        }

        public static void Debug(string message)
        {
            LogInstance.Debug(message);
            TestContext.Progress.WriteLine($"[DEBUG] {message}");
        }
    }
}
