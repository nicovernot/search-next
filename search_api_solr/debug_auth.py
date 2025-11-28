import httpx
import asyncio
from urllib.parse import quote_plus

async def check_auth():
    remote_ip = "127.0.0.1"
    docs_urls = ["https://books.openedition.org/pur/30504"]
    urls_str = quote_plus(','.join(docs_urls))
    url = f"http://auth.openedition.org/auth_by_url/?ip={remote_ip}&url={urls_str}"
    
    print(f"Calling URL: {url}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, follow_redirects=True, timeout=10.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response JSON: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_auth())
