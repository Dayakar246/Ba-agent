using System.Threading.Tasks;
using NUnit.Framework;
using PlaywrightAutomation.Tests.Config;
using PlaywrightAutomation.Tests.Pages;
using PlaywrightAutomation.Tests.Steps;
using PlaywrightAutomation.Tests.Tests.Base;

namespace PlaywrightAutomation.Tests.Tests
{
    [TestFixture]
    [Category("Authentication")]
    public class LoginTests : BaseTest
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
        [Description("Verify valid user login succeeds and navigates to Dashboard")]
        public async Task TestValidLogin_Succeeds()
        {
            var dashboardPage = await _authSteps.PerformDefaultUserLoginAsync();
            var isLoaded = await dashboardPage.IsLoadedAsync();
            Assert.That(isLoaded, Is.True, "Dashboard page should be loaded after valid login.");
        }

        [Test]
        [Description("Verify invalid login shows error message")]
        public async Task TestInvalidLogin_DisplaysErrorMessage()
        {
            await _loginPage.NavigateToAsync(EnvironmentConfig.Options.BaseUrl);
            await _loginPage.LoginAsync("invalid_user", "invalid_password");

            var isErrorDisplayed = await _loginPage.IsErrorMessageDisplayedAsync();
            Assert.That(isErrorDisplayed, Is.True, "Error message should be displayed for invalid credentials.");

            var errorText = await _loginPage.GetErrorMessageAsync();
            Assert.That(errorText, Does.Contain("Username and password do not match"), "Error text should match expected message.");
        }
    }
}
