using System.Threading.Tasks;
using Microsoft.Playwright;
using PlaywrightAutomation.Tests.Config;
using PlaywrightAutomation.Tests.Logging;
using PlaywrightAutomation.Tests.Pages;

namespace PlaywrightAutomation.Tests.Steps
{
    public class AuthSteps : BaseSteps
    {
        public AuthSteps(IPage page) : base(page) { }

        public async Task<DashboardPage> PerformLoginAsync(string username, string password)
        {
            Logger.Info($"[STEP] Performing login for user: {username}");
            await LoginPage.NavigateToAsync(EnvironmentConfig.Options.BaseUrl);
            await LoginPage.LoginAsync(username, password);
            return DashboardPage;
        }

        public async Task<DashboardPage> PerformDefaultUserLoginAsync()
        {
            var creds = EnvironmentConfig.Options.DefaultCredentials;
            return await PerformLoginAsync(creds.Username, creds.Password);
        }

        public async Task PerformLogoutAsync()
        {
            Logger.Info("[STEP] Performing user logout");
            await DashboardPage.LogoutAsync();
        }
    }
}
