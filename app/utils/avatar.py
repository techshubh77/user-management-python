import httpx
import aiofiles
import os
import time
from app.utils.logger import logger

async def generate_random_avatar(name: str):
    formatted_name = name.replace(" ", "+")

    url = f"https://ui-avatars.com/api/?name={formatted_name}&background=random&size=256"

    save_dir = "uploads/avatars"
    filename = f"{int(time.time())}.png"
    file_path = os.path.join(save_dir, filename)

    os.makedirs(save_dir, exist_ok=True)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()

            image_data = response.read()
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(image_data)

            logger.info(f"Avatar generated successfully: {file_path}")
            return filename
        except Exception as e:
            logger.error(f"Failed to generate avatar: {e}")
            return None


