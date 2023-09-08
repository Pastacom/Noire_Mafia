import discord
from discord.ext import commands
from discord import app_commands

from GameSettings.Setup import Setup
from LobbyManager.Manager import Manager
from Roles.Civilian import Civilian
from Utils.CogStatus import Status
from config import token

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
client.remove_command("help")


@client.event
async def on_ready():
    # Comment later
    await client.add_cog(Manager(client, Status.WORKING))
    await client.add_cog(Setup(client, Status.WORKING))
    print("I think it's time to blow this scene!")


@client.command(name='test')
@commands.is_owner()
async def test(ctx: commands.Context):
    await client.add_cog(Manager(client, Status.TEST))


@client.command(name='work')
@commands.is_owner()
async def work(ctx: commands.Context):
    await client.add_cog(Manager(client, Status.WORKING))


@client.command(name="shutdown")
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    client.get_cog("Manager").status = Status.SHUTDOWN


@client.command(name='sync')
@commands.is_owner()
async def sync(ctx: commands.Context):
    data = await client.tree.sync()
    await ctx.send(f"Synced {len(data)} commands.")

client.run(token)
