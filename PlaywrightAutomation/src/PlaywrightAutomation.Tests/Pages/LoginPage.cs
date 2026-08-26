using System.Threading.Tasks;
using Microsoft.Playwright;

namespace PlaywrightAutomation.Tests.Pages
{
    public class LoginPage : BasePage
    {
        public LoginPage(IPage page) : base(page) { }

        // Locators using Playwright's GetByPlaceholder, GetByRole, and CSS data-test attribute
        public ILocator UsernameInput => GetByPlaceholder("Username");
        public ILocator PasswordInput => GetByPlaceholder("Password");
        public ILocator LoginButton => GetByRole(AriaRole.Button, new PageGetByRoleOptions { Name = "Login" });
        public ILocator ErrorMessage => Page.Locator("[data-test='error']");

        public async Task LoginAsync(string username, string password)
        {
            await FillAsync(UsernameInput, username, "Username");
            await FillAsync(PasswordInput, password, "Password");
            await ClickAsync(LoginButton, "Login Button");
        }

        public async Task<string> GetErrorMessageAsync()
        {
            return await GetTextAsync(ErrorMessage);
        }

        public async Task<bool> IsErrorMessageDisplayedAsync()
        {
            return await IsVisibleAsync(ErrorMessage);
        }
    }
}
