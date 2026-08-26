using System;
using System.IO;
using Microsoft.Extensions.Configuration;

namespace PlaywrightAutomation.Tests.Config
{
    public static class EnvironmentConfig
    {
        private static readonly Lazy<IConfigurationRoot> ConfigurationLazy = new Lazy<IConfigurationRoot>(BuildConfiguration);

        public static IConfigurationRoot Configuration => ConfigurationLazy.Value;

        public static TestOptions Options
        {
            get
            {
                var options = new TestOptions();
                Configuration.GetSection("TestOptions").Bind(options);
                return options;
            }
        }

        private static IConfigurationRoot BuildConfiguration()
        {
            var env = Environment.GetEnvironmentVariable("TEST_ENVIRONMENT") ?? "Development";
            var basePath = AppContext.BaseDirectory;

            var builder = new ConfigurationBuilder()
                .SetBasePath(basePath)
                .AddJsonFile("Config/appsettings.json", optional: true, reloadOnChange: true)
                .AddJsonFile($"Config/appsettings.{env}.json", optional: true, reloadOnChange: true)
                .AddEnvironmentVariables();

            return builder.Build();
        }
    }
}
