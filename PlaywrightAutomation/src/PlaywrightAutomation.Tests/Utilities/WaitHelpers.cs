using System;
using System.Threading.Tasks;
using Microsoft.Playwright;
using PlaywrightAutomation.Tests.Logging;

namespace PlaywrightAutomation.Tests.Utilities
{
    public static class WaitHelpers
    {
        public static async Task WaitForNetworkIdleAsync(IPage page, float timeout = 30000)
        {
            Logger.Debug("Waiting for network idle state...");
            await page.WaitForLoadStateAsync(LoadState.NetworkIdle, new PageWaitForLoadStateOptions { Timeout = timeout });
        }

        public static async Task WaitForConditionAsync(Func<Task<bool>> condition, TimeSpan timeout, TimeSpan pollingInterval)
        {
            var startTime = DateTime.UtcNow;
            while (DateTime.UtcNow - startTime < timeout)
            {
                if (await condition())
                {
                    return;
                }
                await Task.Delay(pollingInterval);
            }
            throw new TimeoutException($"Condition was not met within {timeout.TotalSeconds} seconds.");
        }
    }
}
