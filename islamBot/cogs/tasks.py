import discord
from discord.ext import commands, tasks
from itertools import cycle
from globals import DBConnect


class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client
        # self.change_status.start()
        self.check_vcs.start()

    @tasks.loop(seconds=60)
    async def check_vcs(self):
        # await asyncio.sleep(30)
        db, cursor = DBConnect()
        cursor.execute("SELECT * FROM voice")
        results = cursor.fetchall()
        for row in results:
            guildID = int(row[0])
            channelID = int(row[1])
            urlDB = row[2]
            try:
                guild = self.client.get_guild(int(guildID))
                channel: discord.VoiceChannel = await self.client.fetch_channel(int(channelID))
                voice_client: discord.VoiceClient = discord.utils.get(
                    self.client.voice_clients, guild=guild)
                if voice_client == None:
                    try:
                        members = channel.members
                        if len(members) == 0:
                            continue
                        await channel.connect()
                        url = urlDB
                        ffmpeg_options = {
                            'options': '-vn',
                            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                        }
                        audio_source = discord.FFmpegPCMAudio(
                            url, options=ffmpeg_options)
                        voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=guild)
                        voice_client.play(audio_source, after=None)
                        continue
                    except:
                        continue
                else:
                    members = channel.members
                    if len(members) == 1:
                        await voice_client.disconnect()
                        continue
                if not voice_client.is_playing():
                    url = urlDB
                    ffmpeg_options = {
                        'options': '-vn',
                        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                    }
                    audio_source = discord.FFmpegPCMAudio(
                        url, options=ffmpeg_options)
                    members = channel.members
                    if len(members) == 1:
                        continue
                    voice_client.play(audio_source, after=None)
            except:
                continue

#     @tasks.loop(seconds=5)
#     async def change_status(self):
#         await self.client.wait_until_ready()
#         await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=next(status)))


# status = cycle(["أَلا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ",
#                "https://islambot.narox.xyz/"])


async def setup(client):
    await client.add_cog(Tasks(client))
