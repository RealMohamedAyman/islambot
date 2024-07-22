import discord
from discord.ext import commands, tasks
from discord import app_commands, Interaction
import datetime
from contextlib import asynccontextmanager
from globals import *

class Mushaf(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.checkPages.start()

    @asynccontextmanager
    async def get_db_cursor(self):
        connection = None
        cursor = None
        try:
            connection = cnxPool.get_connection()
            yield connection
        finally:
            return_connection_to_pool(connection, cursor)

    def format_page(self, page: int) -> str:
        return f"{page:03d}"

    @tasks.loop(minutes=3)
    async def checkPages(self):
        await self.sendPage()

    @app_commands.command(name="mushaf", description="Get an image of a page from mushaf")
    @app_commands.describe(page="Page Number [1:569]")
    async def _mushaf(self, interaction: Interaction, page: int):
        if page < 1 or page > 569:
            await interaction.response.send_message(content="Page number must be between 1 and 569")
            return

        formatted_page = self.format_page(page)
        embed = discord.Embed(
            color=discord.Colour.dark_gold(), 
            title=f"Al-Mushaf - Page ( {formatted_page} / 569 )"
        )
        embed.set_footer(
            text=f"Requested by: {interaction.user} ( {interaction.user.id} )"
        )
        embed.set_image(url=f"https://qurango.com/images/arabic/{formatted_page}.jpg")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nkhtm", description="Set a channel to send one page from Quran every day")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    @app_commands.describe(channel="Choose a text channel", num="Number of pages to be sent per day")
    async def _nkhtm(self, interaction: Interaction, channel: discord.TextChannel, num: int = 1):
        await interaction.response.defer()

        if num < 1 or num > 5:
            numErrEmbed = discord.Embed(color=discord.Color.dark_red(), 
                                        description="Number of pages must be between 1 and 5 per day")
            return await interaction.followup.send(embed=numErrEmbed)

        async with self.get_db_cursor() as cnx:
            cursor = cnx.cursor()
            cursor.execute("SELECT * FROM nkhtm WHERE guild_id=%s", (str(interaction.guild.id),))
            results = cursor.fetchall()
            time = str(datetime.datetime.utcnow())
            
            if results:
                cursor.execute("UPDATE nkhtm SET channel_id=%s, timestamp=%s, page=%s, num=%s WHERE guild_id=%s",
                                     (str(channel.id), time, 1, num, str(interaction.guild.id)))
                cnx.commit()
            else:
                cursor.execute("INSERT INTO nkhtm (guild_id, channel_id, page, timestamp, num) VALUES (%s, %s, %s, %s, %s)",
                                     (str(interaction.guild.id), str(channel.id), 1, time, num))
                cnx.commit()

        try:
            testPermEmbed = discord.Embed(color=discord.Color.dark_gold(), 
                                          title="This channel has been set for daily Quran pages", 
                                          description="IslamBot will start sending pages here starting from tomorrow!")
            await channel.send(embed=testPermEmbed)
        except discord.Forbidden:
            permErrEmbed = discord.Embed(color=discord.Color.dark_red(), 
                                         description="I don't have enough permissions in that channel. I need permission to send messages, media and embeds")
            return await interaction.followup.send(f"I don't have permission to send messages in {channel.mention}", embed=permErrEmbed)
        
        await interaction.followup.send(f"Changed your daily mushaf channel to {channel.mention}")

    async def sendPage(self):
        async with self.get_db_cursor() as cnx:
            cursor = cnx.cursor()
            cursor.execute("SELECT * FROM nkhtm")
            results =  cursor.fetchall()
            now = datetime.datetime.now(datetime.UTC)

            for row in results:
                guild_id, channel_id, page, timestamp, num = row
                diff_hours = (now.timestamp() - timestamp) / 3600

                if diff_hours < 24:
                    continue

                try:
                    channel = await self.client.fetch_channel(int(channel_id))
                except:
                    continue

                for i in range(num):
                    current_page = int(page) + i
                    if current_page > 569:
                        break
                    await self.sendDaily(channel, current_page)

                if current_page >= 569:
                    cursor.execute("DELETE FROM nkhtm WHERE guild_id=%s", (guild_id,))
                    cnx.commit()
                else:
                    cursor.execute("UPDATE nkhtm SET page=%s, timestamp=%s WHERE guild_id=%s", 
                                         (current_page, now.timestamp(), guild_id))
                    cnx.commit()
                

    async def sendDaily(self, channel: discord.TextChannel, page: int):
        formatted_page = self.format_page(page)
        embed = discord.Embed(
            color=discord.Colour.dark_gold(), 
            title=f"Al-Mushaf - Page ( {formatted_page} / 569 )"
        )
        embed.set_image(url=f"https://qurango.com/images/arabic/{formatted_page}.jpg")

        if page == 569:
            embed.description = f"{self.doaa1}\n\n{self.doaa2}\n\n{self.doaa3}"

        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            print(f"Failed to send daily page to channel {channel.id}")

    doaa1 = """
    «اللهم ارحمني بالقرآن وَاجعَله لِي إِماماً ونوراً وَهُدى وَرَحْمَة.. اللهم ذَكِّرْنِي مِنْهُ مَا نَسِيتُ وَعَلِّمْنِي مِنْهُ مَا جَهِلْتُ وَارْزُقْنِي تِلاَوَتَهُ آنَاءَ الليلِ وَأَطْرَافَ النَّهَارِ وَاجْعَلْهُ لِي حُجَّةً يَا رَبَّ العَالَمِينَ تحول به بيننا وبين معصيتك ومن طاعتك ما تبلغنا بها جنتك ومن اليقين ما تهون به علينا مصائب الدنيا ومتعنا بأسماعنا وأبصارنا وقوتنا ما أحييتنا واجعله الوارث منا وأجعل ثأرنا على من ظلمنا وانصرنا على من عادانا ولا تجعل مصيبتنا في ديننا ولا تجعل الدنيا أكبر همنا ولا مبلغ علمنا ولا تسلط علينا من لا يرحمنا».
    """
    doaa2 = """
    «اللهم لا تدع لنا ذنباً إلّا غفرته ولا هماً إلّا فرجته ولا ديناً إلّا قضيته ولا حاجة من حوائج الدنيا والآخرة إلّا قضيتها يا أرحم الراحمين.. اللهم اجعل خير عمري آخره وخير عملي خواتمه وخير أيامي يوم ألقاك فيه».
    """

    doaa3 = """
    «اللهم إني أسألك خير المسألة وخير الدعاء وخير النجاح وخير العلم وخير العمل وخير الثواب وخير الحياة وخير الممات وثبتني وثقل موازيني وحقق إيماني وارفع درجتي وتقبل صلاتي واغفر خطيئاتي وأسألك العلا من الجنة.. اللهم أحسن عاقبتنا في الأمور كلها، وأجرنا من خزي الدنيا وعذاب الآخرة».
    """

async def setup(client):
    await client.add_cog(Mushaf(client))




