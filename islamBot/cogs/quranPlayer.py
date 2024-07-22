import discord
from discord.ext import commands
from discord import Interaction, app_commands
from globals import cnxPool, return_connection_to_pool
from typing import List, Dict
from contextlib import asynccontextmanager
import json

with open('./data/quranStations.json', 'r', encoding='utf-8') as f:
    QURAN_STATIONS = json.load(f)

async def quran_station_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=station['name_en'], value=station['name_en'])
        for station in QURAN_STATIONS
        if current.lower() in station['name_en'].lower()
    ][:25]  # Discord limits to 25 choices



class QariView(discord.ui.View):
    def __init__(self, client: commands.Bot, channel: discord.VoiceChannel, interactor: discord.User):
        super().__init__()

class QuranPlayer(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @asynccontextmanager
    async def get_db_cursor(self):
        connection = cnxPool.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        finally:
            return_connection_to_pool(connection, cursor)

    @app_commands.command(name="quran", description="Set a voice channel to play quran 24/7")
    @app_commands.describe(channel="The voice channel to join", station="The Quran station to play")
    @app_commands.autocomplete(station=quran_station_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def _quran(self, interaction: discord.Interaction, channel: discord.VoiceChannel, station: str):
        # Find the selected station
        selected_station = next((s for s in QURAN_STATIONS if s['name_en'] == station), None)
        
        if not selected_station:
            await interaction.response.send_message("Invalid station selected.", ephemeral=True)
            return

        # Update database
        async with self.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM voice WHERE guild_id=%s", (str(interaction.guild.id),))
            results = cursor.fetchall()
            if results:
                cursor.execute("UPDATE voice SET channel_id=%s, url=%s WHERE guild_id=%s",
                               (str(channel.id), selected_station['radio_url'], str(interaction.guild.id)))
            else:
                cursor.execute("INSERT INTO voice (guild_id, channel_id, url) VALUES (%s, %s, %s)",
                               (str(interaction.guild.id), str(channel.id), selected_station['radio_url']))

        # Connect and play
        await self.connect_and_play(interaction.guild, channel, selected_station['radio_url'])

        embed = discord.Embed(color=discord.Colour.dark_gold(), title="Quran Player")
        embed.description = f"Now playing **{selected_station['name_en']}** in {channel.mention}"
        await interaction.response.send_message(embed=embed)

    async def start_playing(self, voice_client: discord.VoiceClient, url: str, guild_id: str):
        ffmpeg_options = {
            'options': '-vn',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }
        audio_source = discord.FFmpegPCMAudio(url, options=ffmpeg_options)
        voice_client.play(audio_source, after=None)

        connection = cnxPool.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE voice SET url=%s WHERE guild_id=%s", (url, guild_id))
            connection.commit()
        finally:
            return_connection_to_pool(connection, cursor)

    async def connect_and_play(self, guild: discord.Guild, channel: discord.VoiceChannel, url: str):
        voice_client = discord.utils.get(self.client.voice_clients, guild=guild)
        if voice_client:
            await voice_client.disconnect()
        voice_client = await channel.connect()
        await self.start_playing(voice_client, url, str(guild.id))

async def setup(client: commands.Bot):
    await client.add_cog(QuranPlayer(client))



