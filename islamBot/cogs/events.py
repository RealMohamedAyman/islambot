import discord
from discord.ext import commands
from globals import *
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @asynccontextmanager
    async def get_db_cursor(self):
        connection = None
        cursor = None
        try:
            connection = cnxPool.get_connection()
            cursor = connection.cursor()
            yield cursor
        finally:
            return_connection_to_pool(connection, cursor)

    async def play_audio(self, channel, url):
        try:
            voice_client = await channel.connect()
            ffmpeg_options = {
                'options': '-vn',
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            }
            audio_source = discord.FFmpegPCMAudio(url, options=ffmpeg_options)
            voice_client.play(audio_source, after=None)
        except Exception as e:
            print(f"Error playing audio: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        wh_id = os.getenv('WEBHOOK_ID_BOT_STATUS')
        wh_token = os.getenv('WEBHOOK_TOKEN_BOT_STATUS')
        wh = discord.SyncWebhook.partial(id=wh_id, token=wh_token)
        
        embed = discord.Embed(title="🤖 Bot Status", color=discord.Colour.dark_gold())
        embed.description = "IslamBot is back online & Getting ready to sync commands!"
        wh.send(embed=embed)
        
        synced = await self.client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
        print(f'Logged in as {self.client.user}')
        
        status = "أَلا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ"
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
        
        async with self.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM voice")
            results = cursor.fetchall()
            for row in results:
                guildID, channelID, urlDB = int(row[0]), int(row[1]), row[2]
                try:
                    channel = await self.client.fetch_channel(channelID)
                    if len(channel.members) >= 1:
                        await self.play_audio(channel, urlDB)
                except discord.errors.NotFound:
                    pass
                    # print(f"Channel {channelID} not found")
                except Exception as e:
                    pass
                    # print(f"Error setting up voice channel {channelID}: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async with self.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM voice WHERE guild_id=%s", (str(member.guild.id),))
            results = cursor.fetchall()
            if not results:
                return

            channelID, urlDB = results[0][1], results[0][2]

            if str(member) == str(self.client.user) and before.channel != after.channel:
                if before.channel:
                    voice_client = discord.utils.get(self.client.voice_clients, guild=member.guild)
                    if voice_client:
                        await voice_client.disconnect()

                if after.channel and after.channel.id == int(channelID):
                    await self.play_audio(after.channel, urlDB)

            elif before.channel and before.channel.id == int(channelID):
                if len(before.channel.members) == 1:
                    voice_client = discord.utils.get(self.client.voice_clients, guild=member.guild)
                    if voice_client:
                        await voice_client.disconnect()

            elif after.channel and after.channel.id == int(channelID):
                if len(after.channel.members) >= 1:
                    await self.play_audio(after.channel, urlDB)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        wh_id = os.getenv('WEBHOOK_ID_GUILD_JOIN')
        wh_token = os.getenv('WEBHOOK_TOKEN_GUILD_JOIN')
        wh = discord.SyncWebhook.partial(id=wh_id, token=wh_token)
        
        embed = discord.Embed(title='Joined a new guild', color=discord.Colour.dark_green())
        embed.description = f"Guild Name: {guild.name}\nGuild ID: {guild.id}\nOwnerID: {guild.owner_id}"
        wh.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        wh_id = os.getenv('WEBHOOK_ID_GUILD_REMOVE')
        wh_token = os.getenv('WEBHOOK_TOKEN_GUILD_REMOVE')
        wh = discord.SyncWebhook.partial(id=wh_id, token=wh_token)
        
        embed = discord.Embed(title='Guild was removed', color=discord.Colour.dark_red())
        embed.description = f"Guild Name: {guild.name}\nGuild ID: {guild.id}\nOwnerID: {guild.owner_id}"
        wh.send(embed=embed)

async def setup(client):
    await client.add_cog(Events(client))
