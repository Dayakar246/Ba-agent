using System.Threading.Tasks;
using Microsoft.Playwright;
using PlaywrightAutomation.Tests.Logging;

namespace PlaywrightAutomation.Tests.Pages
{
    public abstract class BasePage
    {
        protected readonly IPage Page;

        protected BasePage(IPage page)
        {
            Page = page;
        }

        public async Task NavigateToAsync(string url)
        {
            Logger.Info($"Navigating to URL: {url}");
            await Page.GotoAsync(url, new PageGotoOptions { WaitUntil = WaitUntilState.DOMContentLoaded });
        }

        public async Task ClickAsync(ILocator locator, string description = "element")
        {
            Logger.Info($"Clicking on {description}");
            await locator.WaitForAsync(new LocatorWaitForOptions { State = WaitForSelectorState.Visible });
            await locator.ClickAsync();
        }

        public async Task FillAsync(ILocator locator, string value, string description = "input field")
        {
            Logger.Info($"Filling '{description}' with value: {(description.ToLower().Contains("password") ? "*****" : value)}");
            await locator.WaitForAsync(new LocatorWaitForOptions { State = WaitForSelectorState.Visible });
            await locator.FillAsync(value);
        }

        public async Task<string> GetTextAsync(ILocator locator)
        {
            await locator.WaitForAsync(new LocatorWaitForOptions { State = WaitForSelectorState.Visible });
            return await locator.InnerTextAsync();
        }

        public async Task<bool> IsVisibleAsync(ILocator locator)
        {
            return await locator.IsVisibleAsync();
        }

        public ILocator GetByRole(AriaRole role, PageGetByRoleOptions? options = null)
        {
            return Page.GetByRole(role, options);
        }

        public ILocator GetByTestId(string testId)
        {
            return Page.GetByTestId(testId);
        }

        public ILocator GetByText(string text, PageGetByTextOptions? options = null)
        {
            return Page.GetByText(text, options);
        }

        public ILocator GetByPlaceholder(string text, PageGetByPlaceholderOptions? options = null)
        {
            return Page.GetByPlaceholder(text, options);
        }

        public async Task<byte[]> TakeScreenshotAsync(string path)
        {
            Logger.Info($"Taking page screenshot: {path}");
            return await Page.ScreenshotAsync(new PageScreenshotOptions { Path = path, FullPage = true });
        }
    }
}
