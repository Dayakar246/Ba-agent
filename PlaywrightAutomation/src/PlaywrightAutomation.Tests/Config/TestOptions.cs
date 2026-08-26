namespace PlaywrightAutomation.Tests.Config
{
    public class TestOptions
    {
        public string BaseUrl { get; set; } = "https://saucedemo.com";
        public string Browser { get; set; } = "Chromium";
        public bool Headless { get; set; } = true;
        public float SlowMo { get; set; } = 0;
        public float Timeout { get; set; } = 30000;
        public float NavigationTimeout { get; set; } = 30000;
        public bool ScreenshotOnFailure { get; set; } = true;
        public bool RecordTrace { get; set; } = true;
        public bool RecordVideo { get; set; } = false;
        public string ReportsDirectory { get; set; } = "reports";
        public string LogsDirectory { get; set; } = "logs";
        public Credentials DefaultCredentials { get; set; } = new Credentials();
    }

    public class Credentials
    {
        public string Username { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }
}
