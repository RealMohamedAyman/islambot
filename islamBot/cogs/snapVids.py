import discord
from discord.ext import commands
from discord import Interaction, app_commands
import random

CHANNEL_ID = 976944211318431824

class QuranShorts(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="short_video", description="Replies with a random islamic video (Quran, Zekr, Duaa)")
    async def shorts(self, interaction: Interaction):
        await interaction.response.defer()
        msg = await get_videos(self.client)
        await interaction.followup.send(msg)

async def setup(client):
    await client.add_cog(QuranShorts(client))

async def get_videos(client):
    try:
        channel = await client.fetch_channel(CHANNEL_ID)
        msgs = [msg async for msg in channel.history()]
        
        while msgs:
            post = random.choice(msgs)
            for attachment in post.attachments:
                if attachment.url.lower().endswith('.mp4'):
                    return f"** ♥ URL: {attachment.url} **"
            msgs.remove(post)
        
        return "No suitable videos found."
    except discord.HTTPException:
        return "Failed to fetch videos. Please try again later."
