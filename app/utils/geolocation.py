import asyncio
import httpx
from app.utils.logger import logger


async def get_user_location(ip: str):
    url = f"http://ip-api.com/json/{ip}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)

            response.raise_for_status()

            data = response.json()

            if data.get("status") == "fail":
                logger.error(f"Failed to get user location: Invalid IP address {ip}")
                return None

            return {
                "city": data.get("city"),
                "country": data.get("country"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "timezone": data.get("timezone"),
                "isp": data.get("isp"),
            }
        except Exception as e:
            logger.error(f"Failed to get user location: {e}")


if __name__ == "__main__":
    async def main():
        location = await get_user_location("23.21.45.224")
        print(location)

    asyncio.run(main())
