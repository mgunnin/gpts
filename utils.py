import httpx


# Helper function to get API response
async def get_api_response(RIOT_API_URL: str, headers: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(RIOT_API_URL, headers=headers)
            response.raise_for_status()  # This will raise an exception for 4xx and 5xx status codes
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while getting {RIOT_API_URL}: {exc.response.text}")
            raise
        except Exception as exc:
            print(f"An error occurred while getting {RIOT_API_URL}: {exc}")
            raise
    return response.json()
