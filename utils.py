import httpx


# Helper function to get API response
async def get_api_response(url: str, headers: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # This will raise an exception for 4xx and 5xx status codes
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while getting {url}: {exc.response.text}")
            raise
        except Exception as exc:
            print(f"An error occurred while getting {url}: {exc}")
            raise
    return response.json()
