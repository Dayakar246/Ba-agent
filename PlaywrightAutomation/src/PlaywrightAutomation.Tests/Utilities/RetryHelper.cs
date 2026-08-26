using System;
using System.Threading.Tasks;
using Polly;
using PlaywrightAutomation.Tests.Logging;

namespace PlaywrightAutomation.Tests.Utilities
{
    public static class RetryHelper
    {
        public static async Task<T> ExecuteWithRetryAsync<T>(Func<Task<T>> action, int maxRetries = 3, int delayMilliseconds = 1000)
        {
            var policy = Policy
                .Handle<Exception>()
                .WaitAndRetryAsync(
                    maxRetries,
                    retryAttempt => TimeSpan.FromMilliseconds(delayMilliseconds * Math.Pow(2, retryAttempt - 1)),
                    (exception, timeSpan, retryCount, context) =>
                    {
                        Logger.Warn($"Retry attempt {retryCount} after {timeSpan.TotalMilliseconds}ms due to: {exception.Message}");
                    });

            return await policy.ExecuteAsync(action);
        }

        public static async Task ExecuteWithRetryAsync(Func<Task> action, int maxRetries = 3, int delayMilliseconds = 1000)
        {
            await ExecuteWithRetryAsync<bool>(async () =>
            {
                await action();
                return true;
            }, maxRetries, delayMilliseconds);
        }
    }
}
