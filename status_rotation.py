import discord
import asyncio
import random
import aiofiles
import json

async def read_var(key, filename="variables.json"):
    async with aiofiles.open(filename, "r", encoding="utf-8") as file:
        contents = await file.read()
        data = json.loads(contents)
        return data[key]


# List of rotating statuses
statuses = [
    ("Playing", "Beach Buggy Racing 2"),
    ("Watching", "leaderboards"),
    ("Listening", "your engine roars"),
    ("Streaming", "races live!"),
    ("Playing", "Nova + Bone Shaker"),
    ("Watching", "Big Bang crush my car"),
    ("Streaming", "on yt/@vectorunit"),
    ("Playing", "with progression percentages"),
    ("Watching", "Blue mess up with me"),
    ("Streaming","hackers on VU's office TV"),
    ("Playing", 'annoying Tom by saying "when multiplayer"'),
    ("Listening", "Tom")
]

async def rotate_status(bot: discord.Client):
    await bot.wait_until_ready()
    
    while not bot.is_closed():
      if await read_var("overdrive_status") is False:

        activity_type, text = random.choice(statuses)

        if activity_type == "Playing":
            activity = discord.Game(name=text)
        elif activity_type == "Streaming":
            activity = discord.Streaming(name=text, url="https://discord.gg/vectorunit")
        elif activity_type == "Listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=text)
        elif activity_type == "Watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=text)
        else:
            activity = discord.Game(name="Beach Buggy Racing 2")

        await bot.change_presence(activity=activity)
        await asyncio.sleep(3600)  # Wait one hour (3600 seconds)
        print("Changed status")
