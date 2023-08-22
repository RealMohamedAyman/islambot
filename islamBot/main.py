import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import mysql.connector
from globals import DBConnect
from globals import PREFIX

# All you need here is pasting token at the last line in run function

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
# intents.message_content = True
client = commands.Bot(command_prefix=PREFIX, intents=intents)
client.remove_command('help')
tree = client.tree


@client.event
async def setup_hook():
    loaded = []
    for i in os.listdir('./islamBot/cogs'):
        if i.endswith('.py'):
            try:
                await client.load_extension(f"cogs.{i[:-3]}")
                loaded.append(f"✅ {i[:-3]} | Loaded")
            except Exception as e:
                print(e)
                loaded.append(f"❌ {i[:-3]} | Failed")
    cogsStatus = "Modules Status:"
    for i in loaded:
        cogsStatus += f"\n{i}"
    cogsStatus += "\nMade with 💖 by Mohamed Ayman\nNarox © 2022. All rights reserved."
    print(cogsStatus)


@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')
    await ctx.reply(f'Loaded **{extension}**!')


@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await ctx.reply(f'UN-Loaded **{extension}**!')


@client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')
    await ctx.reply(f'Reloaded **{extension}**!')


@client.command(hidden=True)
@commands.is_owner()
async def modules(ctx):
    modulesList = []
    for filename in os.listdir('./islamBot/cogs'):
        if filename.endswith('.py'):
            modulesList.append(filename[:-3])
    embed = discord.Embed(title="Bot Modules", description="\n".join(
        i for i in modulesList), color=0x00FF00)
    await ctx.reply(embed=embed)


@client.command(hidden=True)
@commands.is_owner()
async def sync(ctx: commands.Context):
    message = await ctx.reply(f"🔁 Trying to sync ...")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
        await message.edit(content=f"Synced {len(synced)} command(s).")
    except Exception as e:
        await message.edit(content=f"## Failed to sync..\n**Exception:** {e}")


@load.error
async def load_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.ExtensionAlreadyLoaded):
        error = discord.Embed(color=0xdf1111)
        error.add_field(
            name="ERROR", value=f"**Command Invoke Error!** This Extension is already loaded", inline=False)
        await ctx.reply(embed=error)


@unload.error
async def unload_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.ExtensionNotLoaded):
        error = discord.Embed(color=0xdf1111)
        error.add_field(
            name="ERROR", value=f"**Command Invoke Error!** This Extension is already unloaded", inline=False)
        await ctx.reply(embed=error)


client.run("TOKEN")
