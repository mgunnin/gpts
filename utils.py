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
            return response.json(), response.status_code
        except httpx.HTTPStatusError as exc:
            logging.error(f"HTTPStatusError for {RIOT_API_URL}: {exc.response.text}")
            return None, exc.response.status_code
        except Exception as exc:
            logging.error(f"Exception for {RIOT_API_URL}: {exc}")
            return (
                None,
                500,
            )  # Return 500 as a general error code for unexpected exceptions
