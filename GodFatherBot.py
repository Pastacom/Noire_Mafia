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


@client.tree.command(name="help", description="Shows all allowed commands")
async def help_command(interaction: discord.Interaction):
    emb = discord.Embed(title="Доступные команды:", colour=discord.Color.from_rgb(199, 109, 13))
    emb.add_field(name="/help", value="Показывает доступные команды", inline=False)
    emb.add_field(name="/create_public_lobby", value="Позволяет создать открытое лобби", inline=False)
    emb.add_field(name="/create_private_lobby", value="Позволяет создать закрытое лобби,"
                                                      " к которому можно подключиться по коду", inline=False)
    emb.add_field(name="/join_public_lobby", value="Ищет открытые лобби, в которых еще не началась игра", inline=False)
    emb.add_field(name="/join_private_lobby", value="Позволяет присоединиться к лобби"
                                                    " по коду подключения", inline=False)
    emb.add_field(name="/settings", value="Вызывает меню настроек для игр", inline=False)
    emb.add_field(name="/start", value="Позволяет хосту лобби начать игру", inline=False)
    emb.add_field(name="/ready", value="Позволяет участнику лобби изменить свою готовность перед игрой", inline=False)
    emb.add_field(name="/restart", value="Позволяет перезапустить подготовку к игре, на случай, если состав"
                                         " игроков во время подтверждения готовности изменился", inline=False)
    emb.add_field(name="/action", value="Команда позволяющая игрокам выставлять других на голосование,"
                                        " а активным ролям действовать ночью", inline=False)
    emb.add_field(name="/vote", value="Позволяет проголосовать против игрока", inline=False)
    emb.add_field(name="/end_of_speech", value="Позволяет досрочно завершить свою речь", inline=False)
    emb.add_field(name="/whisper", value="Позволяет отправить сообщение своей команде ночью", inline=False)
    await interaction.response.send_message(embed=emb, ephemeral=True)

client.run(token)
