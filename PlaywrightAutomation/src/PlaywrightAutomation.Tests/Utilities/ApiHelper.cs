using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Playwright;
using PlaywrightAutomation.Tests.Logging;

namespace PlaywrightAutomation.Tests.Utilities
{
    public class ApiHelper
    {
        private readonly IAPIRequestContext _requestContext;

        public ApiHelper(IAPIRequestContext requestContext)
        {
            _requestContext = requestContext;
        }

        public async Task<IAPIResponse> GetAsync(string url, Dictionary<string, string>? headers = null)
        {
            Logger.Info($"[API GET] {url}");
            var options = new APIRequestContextOptions();
            if (headers != null)
            {
                options.Headers = headers;
            }
            return await _requestContext.GetAsync(url, options);
        }

        public async Task<IAPIResponse> PostAsync<T>(string url, T body, Dictionary<string, string>? headers = null)
        {
            Logger.Info($"[API POST] {url}");
            var options = new APIRequestContextOptions
            {
                Data = JsonSerializer.Serialize(body)
            };
            if (headers != null)
            {
                options.Headers = headers;
            }
            return await _requestContext.PostAsync(url, options);
        }
    }
}
