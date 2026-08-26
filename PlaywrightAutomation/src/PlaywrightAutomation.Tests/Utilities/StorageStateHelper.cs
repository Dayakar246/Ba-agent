using System.IO;
using System.Threading.Tasks;
using Microsoft.Playwright;
using PlaywrightAutomation.Tests.Logging;

namespace PlaywrightAutomation.Tests.Utilities
{
    public static class StorageStateHelper
    {
        public static async Task SaveStorageStateAsync(IBrowserContext context, string path)
        {
            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            Logger.Info($"Saving authentication storage state to: {path}");
            await context.StorageStateAsync(new BrowserContextStorageStateOptions { Path = path });
        }

        public static bool StorageStateExists(string path)
        {
            return File.Exists(path);
        }
    }
}
