using Microsoft.Playwright;
using PlaywrightAutomation.Tests.Pages;

namespace PlaywrightAutomation.Tests.Steps
{
    public abstract class BaseSteps
    {
        protected readonly IPage Page;
        protected readonly LoginPage LoginPage;
        protected readonly DashboardPage DashboardPage;

        protected BaseSteps(IPage page)
        {
            Page = page;
            LoginPage = new LoginPage(page);
            DashboardPage = new DashboardPage(page);
        }
    }
}
