from globals import DBConnect
from globals import PREFIX
import discord
from discord.ext import commands, tasks
from discord import app_commands, Interaction
import datetime


class Mushaf(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.checkPages.start()

    @tasks.loop(seconds=60)
    async def checkPages(self):
        await sendPage(self.client)

    @app_commands.command(name="mushaf", description="Get an image of a page from mushaf")
    @app_commands.describe(page="Page Number [1:569]")
    async def _mushaf(self, interaction: Interaction, page: int):
        if len(str(page)) == 1:
            page = f"00{page}"
        elif len(str(page)) == 2:
            page = f"0{page}"
        elif len(str(page)) == 3:
            page = f"{page}"

        if (page == 000) or (page == "000"):
            await interaction.response.send_message(content="Page argument must be an integer number and not 0")
            return

        if int(page) > 569:
            await interaction.response.send_message(content="Maximum number of pages is 569")
            return

        embed = discord.Embed(
            color=discord.Colour.dark_gold(), title=f"Al-Mushaf - Page ( {page} / 569 )")
        embed.set_footer(
            text=f"Requested by: {interaction.user.name}#{interaction.user.discriminator} ( {interaction.user.id} )")
        embed.set_image(url=f"https://qurango.com/images/arabic/{page}.jpg")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nkhtm", description="set a channel to send one page from quran every day")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    @app_commands.describe(channel="Choose a text channel")
    async def _nkhtm(self, interaction: Interaction, channel: discord.TextChannel):
        db, cursor = DBConnect()
        try:
            doaa = """
            روي عن الإمام جعفر الصادق (عليه السلام) أنه كان من دعائه إذا قرأ القرآن: "بسم الله، اللهم إني أشهد أن هذا كتابك المنزل من عندك على رسولك محمد (صلى الله عليه وآله وسلم)، وكتابك الناطق على لسان رسولك، فيه حكمك وشرائع دينك، أنزلته على نبيك، وجعلته عهداً منك إلى خلقك وحبلا متصلا فيما بينك وبين عبادك.
اللهم إني نشرت عهدك وكتابك، اللهم فاجعل نظري فيه عبادة وقراءتي تفكراً وفكري اعتباراً، واجعلني ممن اتعظ ببيان مواعظك فيه واجتنب معاصيك، ولا تطبع عند قراءتي كتابك على قلبي ولا على سمعي، ولا تجعل على بصري غشاوة، ولا تجعل قراءتي قراءة لا تدبر فيها، بل اجعلني أتدبر آياته وأحكامه آخذاً بشرائع دينك، ولا تجعل نظري فيه غفلة ولا قراءتي هذرمة، إنك أنت الرؤف الرحيم."""
            msgTime = "بداية من الغد في مثل هذا التوقيت سوف نرسل صفحة من القرآن يوميا\n\
                حتى لا يهجر"
            query1 = "SELECT * FROM nkhtm WHERE guild_id=%s"
            var1 = str(interaction.guild.id)
            time = str(datetime.datetime.utcnow())
            cursor.execute(query1, (var1,))
            results1 = cursor.fetchall()
            if not len(results1) == 0:
                query2 = "UPDATE nkhtm SET channel_id=%s, timestamp=%s, page=%s WHERE guild_id=%s"
                cursor.execute(query2, (str(channel.id), time, 1, var1))
            else:
                query2 = "INSERT INTO nkhtm (guild_id, channel_id,page, timestamp) VALUES (%s, %s, %s, %s)"
                cursor.execute(query2, (var1, str(channel.id), 1, time))
            db.commit()
            await channel.send(f"{doaa}\n\n{msgTime}")

        except:
            await interaction.response.send_message(f"I don't have permission to send messages in {channel.mention} or an error has occured")
            return
        await interaction.response.send_message(f"Changed your daily mushaf channel to {channel.mention}")


async def sendPage(client):
    db, cursor = DBConnect()
    query = "SELECT * FROM nkhtm"
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        guildID = int(row[0])
        channelID = int(row[1])
        page = row[2]
        timestampDB = row[3]
        now = datetime.datetime.utcnow()
        diff = now - timestampDB
        diff_in_hours = diff.total_seconds() / 3600
        if not diff_in_hours >= 24:
            continue
        try:
            channel = client.get_channel(int(channelID))
        except:
            continue

        sendChannel = client.get_channel(channelID)

        if len(str(page)) == 1:
            page = f"00{page}"
        elif len(str(page)) == 2:
            page = f"0{page}"
        elif len(str(page)) == 3:
            page = f"{page}"

        doaa1 = """
        «اللهم ارحمني بالقرآن وَاجعَله لِي إِماماً ونوراً وَهُدى وَرَحْمَة.. اللهم ذَكِّرْنِي مِنْهُ مَا نَسِيتُ وَعَلِّمْنِي مِنْهُ مَا جَهِلْتُ وَارْزُقْنِي تِلاَوَتَهُ آنَاءَ الليلِ وَأَطْرَافَ النَّهَارِ وَاجْعَلْهُ لِي حُجَّةً يَا رَبَّ العَالَمِينَ تحول به بيننا وبين معصيتك ومن طاعتك ما تبلغنا بها جنتك ومن اليقين ما تهون به علينا مصائب الدنيا ومتعنا بأسماعنا وأبصارنا وقوتنا ما أحييتنا واجعله الوارث منا وأجعل ثأرنا على من ظلمنا وانصرنا على من عادانا ولا تجعل مصيبتنا في ديننا ولا تجعل الدنيا أكبر همنا ولا مبلغ علمنا ولا تسلط علينا من لا يرحمنا».
        """
        doaa2 = """
        «اللهم لا تدع لنا ذنباً إلّا غفرته ولا هماً إلّا فرجته ولا ديناً إلّا قضيته ولا حاجة من حوائج الدنيا والآخرة إلّا قضيتها يا أرحم الراحمين.. اللهم اجعل خير عمري آخره وخير عملي خواتمه وخير أيامي يوم ألقاك فيه».
        """

        doaa3 = """
        «اللهم إني أسألك خير المسألة وخير الدعاء وخير النجاح وخير العلم وخير العمل وخير الثواب وخير الحياة وخير الممات وثبتني وثقل موازيني وحقق إيماني وارفع درجتي وتقبل صلاتي واغفر خطيئاتي وأسألك العلا من الجنة.. اللهم أحسن عاقبتنا في الأمور كلها، وأجرنا من خزي الدنيا وعذاب الآخرة».
        """

        embed = discord.Embed(
            color=discord.Colour.dark_gold(), title=f"Al-Mushaf - Page ( {page} / 569 )")
        embed.set_image(url=f"https://qurango.com/images/arabic/{page}.jpg")
        if page == "569":
            embed.description = f"{doaa1}\n\n{doaa2}\n\n{doaa3}"

        try:
            await sendChannel.send(embed=embed)
        except:
            continue

        if not page == "569":
            # UPDATE PAGE AND TIME
            query2 = "UPDATE nkhtm SET page=%s, timestamp=%s WHERE guild_id=%s"
            cursor.execute(query2, (int(page) + 1, now, guildID))
            db.commit()
        else:
            query2 = "DELETE FROM nkhtm WHERE guild_id=%s"
            cursor.execute(query2, (guildID,))
            db.commit()


async def setup(client):
    await client.add_cog(Mushaf(client))
