import asyncio
import os

from sechat import Credentials, Room

async def main():
    credentials = await Credentials.load_or_authenticate("credentials.dat", os.environ["BOT_EMAIL"], os.environ["BOT_PASSWORD"])
    async with Room.join(credentials, 1) as room:
        await room.send("Hello World!")

asyncio.run(main())
