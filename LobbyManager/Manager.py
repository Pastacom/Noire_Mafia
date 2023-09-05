import string
import random

import discord
from discord.ext import commands
from discord import app_commands
import asyncio

from LobbyManager.Lobby import Lobby
from Utils.CogStatus import Status


def guild_only_check():
    async def predicate(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command is not allowed in DM.", ephemeral=True)
            return False
        return True
    return commands.check(predicate)


class Manager(commands.Cog, name="Manager"):

    name_mapping = {"category": "♣›GameSession-{}‹♣", "text_channel": "📨-game-{}", "voice_channel": "🔈-Lobby-{}"}
    lobbies = {}
    user_to_lobby_id = {}
    join_codes = {}

    def __init__(self, client: discord.ext.commands.Bot, mode: Status):
        self.client = client
        self.status = mode

    @staticmethod
    async def manage_permissions(category, interaction: discord.Interaction):
        overwrite = discord.PermissionOverwrite(view_channel=False)
        for role in category.guild.roles:
            await category.set_permissions(role, overwrite=overwrite)
        role = await interaction.guild.create_role(name=category.name, colour=discord.Color.from_rgb(199, 109, 13))
        overwrite = discord.PermissionOverwrite(view_channel=True)
        await category.set_permissions(role, overwrite=overwrite)
        await interaction.user.add_roles(role)
        return role

    async def find_id(self):
        lobby_id = -1
        while lobby_id == -1:
            for i in range(1, 30001):
                if self.lobbies.get(i) is None:
                    return i
            await asyncio.sleep(10000)

    async def generate_code(self):
        chars = string.ascii_uppercase + string.digits
        result = ""
        while len(result) == 0 or self.join_codes.get(result) is not None:
            result = ''.join(random.choices(chars, k=6))
        return result

    def check_code(self, code):
        return self.join_codes.get(code) is not None

    async def destruction(self, user_id):
        lobby_id = self.user_to_lobby_id[user_id]
        await self.lobbies[lobby_id].cleanup()
        if self.lobbies[lobby_id].code != "0":
            self.join_codes.pop(self.lobbies[lobby_id].code)
        self.lobbies.pop(lobby_id)
        self.user_to_lobby_id.pop(user_id)

    @app_commands.command(name="create_public_lobby", description="Creates a new public gaming room")
    @app_commands.guild_only()
    async def create_public_lobby(self, interaction: discord.Interaction):
        lobby_id = self.user_to_lobby_id.get(interaction.user.id)
        if lobby_id is not None:
            await interaction.response.send_message("You already are a player of another lobby.", ephemeral=True)
        else:
            lobby_id = await self.find_id()
            self.user_to_lobby_id[interaction.user.id] = lobby_id
            category = await interaction.guild.create_category(self.name_mapping.get("category").format(lobby_id))
            text = await interaction.guild.create_text_channel(self.name_mapping.get("text_channel").format(lobby_id),
                                                               category=category)
            voice = await interaction.guild.create_voice_channel(self.name_mapping.get("voice_channel").format(lobby_id),
                                                                 category=category)
            invite = await voice.create_invite(max_age=180, max_uses=1)
            await interaction.response.send_message(invite, ephemeral=True)
            self.lobbies[lobby_id] = Lobby(category, text, voice, "0", interaction.guild.default_role, interaction.user)
            asyncio.create_task(self.destruction(interaction.user.id))

    @app_commands.command(name="join_public_lobby", description="Join public lobby that hasn't started the game yet")
    async def join_public_lobby(self, interaction: discord.Interaction):
        for lobby_id in self.lobbies.keys():
            lobby = self.lobbies.get(lobby_id)
            if lobby.public and lobby.status == Lobby.Status.SETUP:
                self.user_to_lobby_id[interaction.user.id] = lobby_id
                invite = await lobby.voice_channel.create_invite(max_age=180, max_uses=1)
                await interaction.response.send_message(invite, ephemeral=True)
                return
        else:
            await interaction.response.send_message("No available lobbies, please try again later.", ephemeral=True)

    @app_commands.command(name="create_private_lobby", description="Creates a new private gaming room")
    @app_commands.guild_only()
    async def create_private_lobby(self, interaction: discord.Interaction):
        lobby_id = self.user_to_lobby_id.get(interaction.user.id)
        if lobby_id is not None:
            await interaction.response.send_message("You already are a player of another lobby.", ephemeral=True)
        else:
            lobby_id = await self.find_id()
            self.user_to_lobby_id[interaction.user.id] = lobby_id
            category = await interaction.guild.create_category(self.name_mapping.get("category").format(lobby_id))
            text = await interaction.guild.create_text_channel(self.name_mapping.get("text_channel").format(lobby_id),
                                                               category=category)
            voice = await interaction.guild.create_voice_channel(self.name_mapping.get("voice_channel").format(lobby_id),
                                                                 category=category)
            invite = await voice.create_invite(max_age=180, max_uses=1)
            await interaction.response.send_message(invite, ephemeral=True)
            role = await self.manage_permissions(category, interaction)
            code = await self.generate_code()
            self.lobbies[lobby_id] = Lobby(category, text, voice, code, role, interaction.user, False)
            self.join_codes[code] = lobby_id
            message = await text.send(f"***=== LOBBY JOIN CODE ===***\n\t\t\t\t**{code}**\n"
                                      f"***========================***", silent=True)
            await message.pin()
            asyncio.create_task(self.destruction(interaction.user.id))

    @app_commands.command(name="join_private_lobby", description="Join private lobby")
    @app_commands.describe(code="Lobby's join code")
    async def join_private_lobby(self, interaction: discord.Interaction, code: str):
        if self.check_code(code):
            lobby_id = self.join_codes.get(code)
            invite = await self.lobbies.get(lobby_id).voice_channel.create_invite(max_age=180, max_uses=1)
            await interaction.user.add_roles(self.lobbies.get(lobby_id).role)
            self.user_to_lobby_id[interaction.user.id] = lobby_id
            await interaction.response.send_message(invite, ephemeral=True)
        else:
            await interaction.response.send_message("Lobby with such join code doesn't exist.", ephemeral=True)

    @app_commands.command(name="start", description="Starts the game in current lobby")
    async def start(self, interaction: discord.Interaction):
        lobby_id = self.user_to_lobby_id.get(interaction.user.id)
        if lobby_id is not None:
            lobby = self.lobbies.get(lobby_id)
            if lobby.host == interaction.user and lobby.status == Lobby.Status.SETUP:
                if 1 <= len(lobby.voice_channel.members) <= 15:
                    await interaction.response.send_message("Ждем подтверждения игроков", ephemeral=True)
                    await self.lobbies.get(lobby_id).create_session()
                else:
                    await interaction.response.send_message(f"Игру можно запустить для количества игроков от 5 до 15."
                                                            f" На данный момент в лобби"
                                                            f" {len(lobby.voice_channel.members)} игроков",
                                                            ephemeral=True)
            else:
                await interaction.response.send_message("You already launched the game.", ephemeral=True)
        else:
            await interaction.response.send_message("You are not hosting any lobby.", ephemeral=True)

    @app_commands.command(name="ready", description="Change your readiness before the game")
    async def ready_up(self, interaction: discord.Interaction):
        lobby_id = self.user_to_lobby_id.get(interaction.user.id)
        if lobby_id is not None:
            lobby = self.lobbies.get(lobby_id)
            if lobby.status == Lobby.Status.READY:
                if interaction.user in lobby.user_to_player:
                    player = lobby.user_to_player[interaction.user]
                    player.ready = not player.ready
                    lobby.waiting_players -= 1 if player.ready else -1
                    try:
                        await interaction.user.edit(nick=interaction.user.name + (' ✅' if player.ready else ' ❌'))
                    except discord.Forbidden:
                        pass
                    await interaction.response.send_message("Вы готовы к игре." if player.ready
                                                            else "Вы не готовы к игре.",
                                                            ephemeral=True)
                else:
                    await interaction.response.send_message("You are not connected to voice channel.", ephemeral=True)
                if lobby.waiting_players == 0:
                    lobby.status = Lobby.Status.PLAYING
                    await lobby.set_default_nicknames()
                    await lobby.give_roles()
                    await lobby.text_channel.send("**\nПосмотрите свою роль в личных сообщениях.**")
                    await asyncio.sleep(10)
                    settings = await self.client.get_cog("Setup").get_settings(lobby.host.id)
                    if settings.game_mode_auto:
                        asyncio.create_task(lobby.launch_game(settings))
                    else:
                        await lobby.text_channel.send("Далее игру проведет ведущий. Приятной игры!")
            else:
                await interaction.response.send_message("You can't change your readiness now.", ephemeral=True)
        else:
            await interaction.response.send_message("You are not in lobby.", ephemeral=True)

    @app_commands.command(name="end_speech", description="Ends your speech earlier")
    async def end_turn(self, interaction: discord.Interaction):
        lobby_id = self.user_to_lobby_id.get(interaction.user.id)
        if lobby_id is not None:
            lobby = self.lobbies.get(lobby_id)
            if lobby.status == Lobby.Status.PLAYING:
                await lobby.session.end(interaction)
            else:
                await interaction.response.send_message("This command can be use only in game.", ephemeral=True)
        else:
            await interaction.response.send_message("You are not in lobby.", ephemeral=True)

    @app_commands.command(name="action", description="Make an action at the night if you have an active role!")
    @app_commands.describe(target="Player that would be affected by your action")
    async def action(self, interaction: discord.Interaction, target: discord.User):
        lobby_id = self.user_to_lobby_id.get(interaction.user.id)
        if lobby_id is not None:
            lobby = self.lobbies.get(lobby_id)
            if lobby.status == Lobby.Status.PLAYING:
                await lobby.session.action(interaction, target)
            else:
                await interaction.response.send_message("This command can be use only in game.", ephemeral=True)
        else:
            await interaction.response.send_message("You are not in lobby.", ephemeral=True)

