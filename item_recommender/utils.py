import logging

import httpx

# Configure logging
logging.basicConfig(
    filename="api_errors.log",
    level=logging.ERROR,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# Helper function to get API response
async def get_api_response(RIOT_API_URL: str, headers: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(RIOT_API_URL, headers=headers)
            response.raise_for_status()
            return {"data": response.json(), "status_code": response.status_code}
        except httpx.HTTPStatusError as exc:
            logging.error(f"HTTPStatusError for {RIOT_API_URL}: {exc.response.text}")
            return {"data": None, "status_code": exc.response.status_code}
        except Exception as exc:
            logging.error(f"Exception for {RIOT_API_URL}: {exc}")
            return {"data": None, "status_code": 500}
