import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor

class LinkValidator:
    def __init__(self):
        self.timeout = 10
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self._executor = ThreadPoolExecutor(max_workers=10)

    def is_link_valid_sync(self, url):
        """
        Check if the given URL is accessible synchronously.
        """
        if not url or not url.startswith("http"):
            return False

        try:
            # We use GET with stream=True so we don't download the whole payload if it's large,
            # but we can get the status code. Some servers block HEAD requests.
            response = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True, verify=False)
            
            # Treat 403 (Forbidden) or 401 (Unauthorized) as "valid link, but we are blocked/need login"
            # We don't want to mark a scholarship as dead just because of a bot-blocker.
            if response.status_code in [200, 301, 302, 303, 307, 308, 401, 403, 405, 503]:
                return True
                
            # If it's a hard 404, or 410, it's definitely dead.
            if response.status_code in [404, 410]:
                return False
                
            # For other 4xx and 5xx errors, we assume invalid
            return False

        except requests.exceptions.Timeout:
            # Timeouts can happen due to temporary server load. We might treat them as invalid for now,
            # or treat them as valid if we want to be very lenient. Let's be moderately strict but 
            # allow some leniency for slow university servers? Let's treat them as invalid.
            return False
        except requests.exceptions.ConnectionError:
            # DNS failure or connection refused -> invalid
            return False
        except Exception as e:
            return False

    async def is_link_valid(self, url):
        """
        Asynchronously check if the link is valid.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.is_link_valid_sync, url)

validator = LinkValidator()
