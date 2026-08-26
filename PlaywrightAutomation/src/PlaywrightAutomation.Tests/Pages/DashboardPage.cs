using System.Threading.Tasks;
using Microsoft.Playwright;

namespace PlaywrightAutomation.Tests.Pages
{
    public class DashboardPage : BasePage
    {
        public DashboardPage(IPage page) : base(page) { }

        public ILocator AppLogo => GetByText("Swag Labs");
        public ILocator InventoryContainer => GetByTestId("inventory-container");
        public ILocator MenuButton => Page.Locator("#react-burger-menu-btn");
        public ILocator LogoutLink => Page.Locator("#logout_sidebar_link");

        public async Task<bool> IsLoadedAsync()
        {
            return await IsVisibleAsync(AppLogo);
        }

        public async Task LogoutAsync()
        {
            await ClickAsync(MenuButton, "Menu Button");
            await ClickAsync(LogoutLink, "Logout Link");
        }
    }
}
