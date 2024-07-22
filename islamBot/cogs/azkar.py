import discord
from discord.ext import commands
from discord import app_commands
import json


class counterButton(discord.ui.Button):
    def __init__(self, counterStart, user):
        super().__init__(label=f"Counter: [ {counterStart} ]", emoji="🔽",  style=discord.ButtonStyle.green, custom_id="counter", row=0)
        self.counterStart = counterStart
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.user.id:
            await interaction.response.send_message(content=f"This embed is being controlled by {self.user.name}, Please start your own Azkar embed using `/azkar`", ephemeral=True)
            return
        self.counterStart -= 1
        self.label = f"Counter: [ {self.counterStart} ]"
        if self.counterStart == 0:
            self.disabled = True

        await interaction.response.defer()
        await interaction.message.edit(view=self.view)

class resCounterButton(discord.ui.Button):
    def __init__(self, counterStart, user):
        super().__init__(label=f"Restart Counter", emoji="🔁",  style=discord.ButtonStyle.red, custom_id="counterRes", row=0)
        self.counterStart = counterStart
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.user.id:
            await interaction.response.send_message(content=f"This embed is being controlled by {self.user.name}, Please start your own Azkar embed using `/azkar`", ephemeral=True)
            return
        self.view.children[2].label = f"Counter: [ {self.counterStart} ]"
        self.view.children[2].counterStart = self.counterStart

        if self.view.children[2].disabled:
            self.view.children[2].disabled = False
        await interaction.response.defer()
        await interaction.message.edit(view=self.view)

class azkarView(discord.ui.View):
    def __init__(self, azkar, page, embed, user, timeout = 1800):
        super().__init__(timeout=timeout)
        self.page = page
        self.azkar = azkar
        self.embed= embed
        zekrCon = azkar["content"][page - 1]
        counterStart = zekrCon["repeat"]
        self.counterStart = counterStart
        self.user = user

        self.add_item(counterButton(counterStart=self.counterStart, user=self.user))
        self.add_item(resCounterButton(counterStart=self.counterStart, user=self.user))


    @discord.ui.button(label="Previous", emoji="◀", style=discord.ButtonStyle.gray, custom_id="prevZekr", row=1)
    async def _prevZekr(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.id == self.user.id:
            await interaction.response.send_message(content=f"This embed is being controlled by {self.user.name}, Please start your own Azkar embed using `/azkar`", ephemeral=True)
            return
        counterBtn = self.children[2]
        resCounterBtn = self.children[3]
        if self.page == 1:
            self.page = len(self.azkar["content"])
        else:
            self.page -= 1

        self.counterStart = self.azkar["content"][self.page - 1]["repeat"]
        counterBtn.counterStart = self.counterStart
        resCounterBtn.counterStart = self.counterStart
        if counterBtn.disabled:
            counterBtn.disabled = False
        counterBtn.label = f"Counter: [ {self.counterStart} ]"
        setZekrPage(self.azkar, self.page, self.embed)
        await interaction.response.defer()
        await interaction.message.edit(embed=self.embed, view=self)



    @discord.ui.button(label="Next", emoji="▶", style=discord.ButtonStyle.gray, custom_id="nextZekr", row=1)
    async def _nextZekr(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.id == self.user.id:
            await interaction.response.send_message(content=f"This embed is being controlled by {self.user.name}, Please start your own Azkar embed using `/azkar`", ephemeral=True)
            return
        counterBtn = self.children[2]
        resCounterBtn = self.children[3]

        if self.page == len(self.azkar["content"]):
            self.page = 1
        else:
            self.page += 1

        self.counterStart = self.azkar["content"][self.page - 1]["repeat"]
        counterBtn.counterStart = self.counterStart
        resCounterBtn.counterStart = self.counterStart
        if counterBtn.disabled:
            counterBtn.disabled = False
        counterBtn.label = f"Counter: [ {self.counterStart} ]"
        
        setZekrPage(self.azkar, self.page, self.embed)
        await interaction.response.defer()
        await interaction.message.edit(embed=self.embed, view=self)




class Azkar(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="azkar", description="returns an embed with azkar sabah, massa or post prayer")
    @app_commands.describe(title="Choose azkar sabah, massa or post prayer")
    @app_commands.choices(title=[
        app_commands.Choice(name="Sabah", value=1),
        app_commands.Choice(name="Massa", value=2),
        app_commands.Choice(name="Post Prayer", value=3)
    ])
    async def azkar(self, interaction: discord.Interaction, title: app_commands.Choice[int]):
        if title.value == 1:
            azkar = await azkarSabah()
        elif title.value == 2:
            azkar = await azkarMassa()
        elif title.value == 3:
            azkar = await azkarPostPrayer()
        else:
            return
        
        embed = discord.Embed(color=discord.Color.dark_gold(), title=azkar["title"])
        page = 1
        setZekrPage(azkar, page, embed)
        await interaction.response.send_message(embed=embed, view=azkarView(azkar, page, embed, interaction.user))


async def azkarSabah():
    with open('./data/azkar_sabah.json', 'r', encoding='utf-8') as f:
        azkar = json.load(f)
    return azkar

async def azkarMassa():
    with open('./data/azkar_massa.json', 'r', encoding='utf-8') as f:
        azkar = json.load(f)
    return azkar

async def azkarPostPrayer():
    with open('./data/PostPrayer_azkar.json', 'r', encoding='utf-8') as f:
        azkar = json.load(f)
    return azkar

def setZekrPage(azkar, page, embed: discord.Embed):
    zekrContent = azkar["content"][page - 1]
    embed.description = zekrContent["zekr"]
    bless = zekrContent["bless"]
    reps = zekrContent["repeat"]
    zekrCon = azkar["content"]
    embed.set_author(name=f"Zekr: {page}/{len(zekrCon)}")
    embed.set_footer(text=f"Repeat: {reps}\n{bless}")

async def setup(client):
    await client.add_cog(Azkar(client))
