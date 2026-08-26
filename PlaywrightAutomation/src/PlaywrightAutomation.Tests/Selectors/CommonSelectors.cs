namespace PlaywrightAutomation.Tests.Selectors
{
    public static class CommonSelectors
    {
        // Common navigation & header selectors
        public static string AppLogo => ".app_logo";
        public static string ShoppingCartLink => ".shopping_cart_link";
        public static string MenuButton => "#react-burger-menu-btn";

        // Form fields & common buttons
        public static string SubmitButton => "input[type='submit'], button[type='submit']";
        public static string ErrorBanner => "[data-test='error']";

        // Role & Accessibility patterns (helper strings)
        public static string ButtonRole => "button";
        public static string TextboxRole => "textbox";
    }
}
