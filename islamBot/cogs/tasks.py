import discord
from discord.ext import commands, tasks
from globals import *
from typing import Dict, Any

class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check_vcs.start()

    @tasks.loop(minutes=5)
    async def check_vcs(self):
        connection = None
        cursor = None
        try:
            connection = cnxPool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM voice")
            results = cursor.fetchall()
            
            for row in results:
                await self.process_voice_channel(row)
                
        except Exception as e:
            print(f"Error in check_vcs: {e}")
        finally:
            if connection and cursor:
                return_connection_to_pool(connection, cursor)

    async def process_voice_channel(self, row: Dict[str, Any]):
        guild_id = int(row["guild_id"])
        channel_id = int(row["channel_id"])
        url = row["url"]

        try:
            guild = await self.client.fetch_guild(guild_id)
            channel = await self.client.fetch_channel(channel_id)
            
            if not isinstance(channel, discord.VoiceChannel):
                return

            voice_client = discord.utils.get(self.client.voice_clients, guild=guild)

            if not voice_client:
                await self.connect_and_play(channel, url)
            elif len(channel.members) <= 1:
                await voice_client.disconnect()
            elif not voice_client.is_playing():
                await self.reconnect_and_play(voice_client, channel, url)

        except discord.errors.NotFound:
            pass
            # print(f"Guild or channel not found: {guild_id}, {channel_id}")
        except Exception as e:
            pass
            # print(f"Error processing voice channel: {e}")

    async def connect_and_play(self, channel: discord.VoiceChannel, url: str):
        if len(channel.members) == 0:
            return
        
        voice_client = await channel.connect()
        await self.play_audio(voice_client, url)

    async def reconnect_and_play(self, voice_client: discord.VoiceClient, channel: discord.VoiceChannel, url: str):
        await voice_client.disconnect()
        if len(channel.members) <= 1:
            return
        
        new_voice_client = await channel.connect()
        await self.play_audio(new_voice_client, url)

    async def play_audio(self, voice_client: discord.VoiceClient, url: str):
        ffmpeg_options = {
            'options': '-vn',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }
        audio_source = discord.FFmpegPCMAudio(url, options=ffmpeg_options)
        voice_client.play(audio_source, after=None)

async def setup(client):
    await client.add_cog(Tasks(client))
