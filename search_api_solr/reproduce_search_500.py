import httpx
import asyncio

async def test_search():
    url = "http://localhost:8007/search"
    payload = {
        "query": {
            "query": "history"
        },
        "filters": [
            {"identifier": "platform", "value": "OB"}
        ],
        "pagination": {
            "from": 0,
            "size": 10
        },
        "facets": []
    }
    
    print(f"Calling URL: {url}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_search())
