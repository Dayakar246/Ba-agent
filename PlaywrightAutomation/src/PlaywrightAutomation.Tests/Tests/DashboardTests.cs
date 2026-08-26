using System.Threading.Tasks;
using NUnit.Framework;
using PlaywrightAutomation.Tests.Pages;
using PlaywrightAutomation.Tests.Steps;
using PlaywrightAutomation.Tests.Tests.Base;

namespace PlaywrightAutomation.Tests.Tests
{
    [TestFixture]
    [Category("Dashboard")]
    public class DashboardTests : BaseTest
    {
        private AuthSteps _authSteps = null!;
        private LoginPage _loginPage = null!;

        [SetUp]
        public void InitPages()
        {
            _authSteps = new AuthSteps(Page);
            _loginPage = new LoginPage(Page);
        }

        [Test]
        [Description("Verify user logout redirects back to Login page")]
        public async Task TestUserLogout_RedirectsToLoginPage()
        {
            var dashboardPage = await _authSteps.PerformDefaultUserLoginAsync();
            Assert.That(await dashboardPage.IsLoadedAsync(), Is.True);

            await _authSteps.PerformLogoutAsync();
            var isLoginDisplayed = await _loginPage.IsVisibleAsync(_loginPage.LoginButton);
            Assert.That(isLoginDisplayed, Is.True, "Logout should redirect user back to Login page.");
        }
    }
}
