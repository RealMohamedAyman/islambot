import discord
from discord.ext import commands
from discord import Interaction, ChannelType, app_commands
from discord.abc import GuildChannel
import asyncio
from globals import DBConnect

class qariSelect(discord.ui.Select):
    def __init__(self,client, channel, interactor):
        # self.voice_client = voice_client
        self.interactor = interactor
        self.client = client
        self.channel = channel
        self.used = False
        options = [discord.SelectOption(label="Maher Al-Meaqli"),
                   discord.SelectOption(label="Mohammed Ayyub"),
                   discord.SelectOption(label="Mohammed Siddiq Al-Minshawi"),
                   discord.SelectOption(label="Mahmoud Khalil Al-Hussary"),
                   discord.SelectOption(label="Mishary Al-Afasi"),
                   discord.SelectOption(label="Nasser Al-Qatami"),
                   discord.SelectOption(label="Khalid Al-Jileel"),
                   discord.SelectOption(label="Yasser Al-Dosari"),
                   discord.SelectOption(label="Ali Jaber")]
        super().__init__(placeholder="Choose Reader Name", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if self.used == True:
            return
        
        if not interaction.user.id ==  self.interactor.id:
            return
        embed = discord.Embed(color=discord.Colour.dark_gold(), title="Quran Player")
        embed.description = f"You chose **{self.values[0]}**, Bot is getting ready and joining voice channel"
        embed.set_footer(text="We are doing our best to solve all issues with 'quranPlayer',\nTry waiting about 60 seconds if an issue appeared\nYou can also try disconnecting the bot and requesting it again")
        await interaction.response.send_message(embed=embed)

        
        sheikh = ['https://qurango.net/radio/maher',
            'https://Qurango.net/radio/mohammed_ayyub',
            'https://Qurango.net/radio/mohammed_siddiq_alminshawi ',
            'https://Qurango.net/radio/mahmoud_khalil_alhussary ',
            'https://Qurango.net/radio/mishary_alafasi ',
            'https://Qurango.net/radio/nasser_alqatami ',
            'https://Qurango.net/radio/khalid_aljileel ',
            'https://qurango.net/radio/yasser_aldosari',
            'https://backup.qurango.net/radio/ali_jaber']
        

        channel: discord.VoiceChannel = await self.client.fetch_channel(self.channel.id)
        voice_client: discord.VoiceClient = discord.utils.get(
            self.client.voice_clients, guild=interaction.guild)

        if voice_client == None:
            await channel.connect()
        else:
            await voice_client.disconnect()
            await channel.connect()

        voice_client: discord.VoiceClient = discord.utils.get(
            self.client.voice_clients, guild=interaction.guild)

        for i in self.options:
            if i.label == self.values[0]:
                ind = self.options.index(i)

        url = sheikh[ind]
        await startPlaying(voice_client=voice_client, url=url, var1=str(interaction.guild.id))
        self.used = True

class qariView(discord.ui.View):
    def __init__(self,client, channel, interactor):
        super().__init__()
        self.interactor = interactor
        self.client = client
        self.channel = channel
        self.add_item(qariSelect(self.client, self.channel, self.interactor))

class QuranPlayer(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="quran", description="Set a voice channel to play quran 24/7")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def _quran(self, interaction: Interaction,  channel: discord.VoiceChannel):

        # 0 Maher Al-Meaqli
        # 1 Mohammed Ayyub
        # 2 Mohammed Siddiq Al-Minshawi
        # 3 Mahmoud Khalil Al-Hussary
        # 4 Mishary Al-Afasi
        # 5 Nasser Al-Qatami
        # 6 Khalid Al-Jileel
        # 7 Yasser Al-Dosari
        # 8 Ali Jaber



        listS = ['Maher Al-Meaqli', 'Mohammed Ayyub', 'Mohammed Siddiq Al-Minshawi',
                 'Mahmoud Khalil Al-Hussary', 'Mishary Al-Afasi', 'Nasser Al-Qatami', 
                 'Khalid Al-Jileel', 'Yasser Al-Dosari', 'Ali Jaber']
        listNums = ['<:1_:1105951745504452618>', '<:2_:1105951748260102144>',
            '<:3_:1105951749996548186>', '<:4_:1105951752500559872>', 
            '<:5_:1105951754312487032>', '<:6_:1105951756707434527>', 
            '<:7_:1105951758716510310>', '<:8_:1105951761010806877>', 
            '<:9_:1105951763212804147>']
        db, cursor = DBConnect()
        query1 = "SELECT * FROM voice WHERE guild_id=%s"
        var1 = str(interaction.guild.id)
        cursor.execute(query1, (var1,))
        results1 = cursor.fetchall()
        if not len(results1) == 0:
            query2 = "UPDATE voice SET channel_id=%s WHERE guild_id=%s"
            cursor.execute(query2, (str(channel.id), var1))
        else:
            query2 = "INSERT INTO voice (guild_id, channel_id, url) VALUES (%s, %s, %s)"
            cursor.execute(query2, (var1, str(channel.id), "None"))

        db.commit()



        sheikhEmbed = discord.Embed(color=discord.Color.dark_gold(),
                                    title="💠 Please choose Qari name from the following list:", description="\n".join("{} {}".format(num, name) for num, name in zip(listNums, listS)))
        sheikhEmbed.set_thumbnail(url=self.client.user.avatar.url)
        view = qariView(self.client, channel, interaction.user)
        sheikhMsg = await interaction.response.send_message(embed=sheikhEmbed, view=view)




async def setup(client):
    await client.add_cog(QuranPlayer(client))


async def startPlaying(voice_client, url, var1):
    ffmpeg_options = {
        'options': '-vn',
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }
    audio_source = discord.FFmpegPCMAudio(
        url, options=ffmpeg_options)
    voice_client.play(audio_source, after=None)

    db, cursor = DBConnect()
    queryURL = "UPDATE voice SET url=%s WHERE guild_id=%s"
    cursor.execute(queryURL, (url, var1))
    db.commit()
