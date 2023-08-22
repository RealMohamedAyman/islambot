import discord
from discord.ext import commands
from globals import DBConnect

# All you need in this file is changing webhooks ID&Token (can be found in webhook url)


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        wh = discord.SyncWebhook.partial(id=123456789, token="ABCDEFGH_123456789")
        embed = discord.Embed(title="🤖 Bot Status",
                              color=discord.Colour.dark_gold())
        embed.description = "IslamBot is back online & Getting ready to sync commands!"
        wh.send(embed=embed)
        synced = await self.client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
        print(f'Logged in as {self.client.user}')
        status =  "أَلا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ"
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
        db, cursor = DBConnect()
        cursor.execute("SELECT * FROM voice")
        results = cursor.fetchall()
        for row in results:
            guildID = int(row[0])
            channelID = int(row[1])
            urlDB = row[2]
            try:
                guild = self.client.get_guild(guildID)
                channel = await self.client.fetch_channel(channelID)
                members = channel.members
                if not len(members) >= 1:
                    return
                await channel.connect()
                voice_client: discord.VoiceClient = discord.utils.get(
                    self.client.voice_clients, guild=guild)
                url = urlDB
                ffmpeg_options = {
                    'options': '-vn',
                    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                }
                audio_source = discord.FFmpegPCMAudio(
                    url, options=ffmpeg_options)
                voice_client.play(audio_source, after=None)
            except:
                continue

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        db, cursor = DBConnect()
        guildID = member.guild.id
        guild = self.client.get_guild(guildID)
        query = "SELECT * FROM voice WHERE guild_id=%s"
        cursor.execute(query, (str(guildID),))
        results = cursor.fetchall()
        if len(results) == 0:
            return
        for row in results:
            channelID = row[1]
            urlDB = row[2]

        if (f"{member.name}#{member.discriminator}" == f"{self.client.user}") and (not before.channel == None) and (not after.channel == None):
            try:
                voice_client: discord.VoiceClient = discord.utils.get(
                    self.client.voice_clients, guild=guild)
                await voice_client.disconnect()

                channel = await self.client.fetch_channel(int(channelID))
                members = channel.members
                if len(members) >= 1:
                    await channel.connect()
                    voice_client: discord.VoiceClient = discord.utils.get(
                        self.client.voice_clients, guild=guild)
                    url = urlDB
                    ffmpeg_options = {
                        'options': '-vn',
                        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                    }
                    audio_source = discord.FFmpegPCMAudio(
                        url, options=ffmpeg_options)
                    voice_client.play(audio_source, after=None)
            except:
                pass

        if not before.channel == None:
            if (before.channel.id == int(channelID)):
                try:
                    channel = await self.client.fetch_channel(int(channelID))
                    members = channel.members
                    if len(members) == 1:
                        voice_client: discord.VoiceClient = discord.utils.get(
                            self.client.voice_clients, guild=guild)
                        await voice_client.disconnect()
                except:
                    return
        if not after.channel == None:
            if (after.channel.id == int(channelID)):
                try:
                    channel = await self.client.fetch_channel(int(channelID))
                    members = channel.members
                    if len(members) >= 1:
                        await channel.connect()
                        voice_client: discord.VoiceClient = discord.utils.get(
                            self.client.voice_clients, guild=guild)
                        url = urlDB
                        ffmpeg_options = {
                            'options': '-vn',
                            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                        }
                        audio_source = discord.FFmpegPCMAudio(
                            url, options=ffmpeg_options)
                        voice_client.play(audio_source, after=None)
                except:
                    return


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        
        wh = discord.SyncWebhook.partial(id=123456789, token="ABCDEFGH_123456789")
        embed = discord.Embed(title='Joined a new guild',
                              color=discord.Colour.dark_green())
        embed.description = f"Guild Name: {guild.name}\nGuild ID: {guild.id}\nOwnerID: {guild.owner_id}"
        wh.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        wh = discord.SyncWebhook.partial(id=123456789, token="ABCDEFGH_123456789")
        embed = discord.Embed(title='Guild was removed',
                              color=discord.Colour.dark_red())
        embed.description = f"Guild Name: {guild.name}\nGuild ID: {guild.id}\nOwnerID: {guild.owner_id}"
        wh.send(embed=embed)


async def setup(client):
    await client.add_cog(Events(client))
