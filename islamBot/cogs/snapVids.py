import discord
from discord.ext import commands, tasks
from discord import Interaction, ChannelType, app_commands
from discord.abc import GuildChannel
import datetime
import random
from globals import DBConnect


class QuranShorts(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="short_video", description="Replies with a random islamic video (Quran, Zekr, Duaa)")
    async def _shorts(self, interaction: Interaction):
        msg = await getVideos(self.client)
        await interaction.response.send_message(msg)


async def setup(client):
    await client.add_cog(QuranShorts(client))


async def getVideos(client):
    CHANNEL_ID = 976944211318431824
    CHANNEL = await client.fetch_channel(CHANNEL_ID)
    msgs = []
    async for i in CHANNEL.history():
        msgs.append(i)
    post = random.choice(msgs)
    sent = False
    for attachment in post.attachments:
        if sent:
            return
        if attachment.url.lower().endswith('.mp4'):
            try:
                return f"** ♥ URL: {attachment} **"
                sent = True
            except:
                pass
            return
        else:
            await getVideos(client)

