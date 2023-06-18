import string
import random

import discord
from discord.ext import commands
from discord import app_commands
import asyncio

from LobbyManager.Lobby import Lobby
from Utils.CogStatus import Status

class Manager(commands.Cog, name="Manager"):

    name_mapping = {"category": "♣›GameSettings-{}‹♣", "text_channel": "📨-game-{}", "voice_channel": "🔈-Lobby-{}"}
    lobbies = {}
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

    async def destruction(self, lobby_id):
        await self.lobbies[lobby_id].cleanup()
        if self.lobbies[lobby_id].code != "0":
            self.join_codes.pop(self.lobbies[lobby_id].code)
        self.lobbies.pop(lobby_id)

    @app_commands.command(name="create_public_lobby", description="Creates a new public gaming room")
    async def create_public_lobby(self, interaction: discord.Interaction):
        lobby_id = await self.find_id()
        category = await interaction.guild.create_category(self.name_mapping.get("category").format(lobby_id))
        text = await interaction.guild.create_text_channel(self.name_mapping.get("text_channel").format(lobby_id),
                                                           category=category)
        voice = await interaction.guild.create_voice_channel(self.name_mapping.get("voice_channel").format(lobby_id),
                                                             category=category)
        invite = await voice.create_invite(max_age=180, max_uses=1)
        await interaction.response.send_message(invite, ephemeral=True)
        self.lobbies[lobby_id] = Lobby(category, text, voice, "0", interaction.guild.default_role, interaction.user)
        asyncio.create_task(self.destruction(lobby_id))

    @app_commands.command(name="join_public_lobby", description="Join public lobby that hasn't started the game yet")
    async def join_public_lobby(self, interaction: discord.Interaction):
        for lobby in self.lobbies.values():
            if lobby.public and lobby.status != Lobby.Status.PLAYING:
                invite = await lobby.voice_channel.create_invite(max_age=180, max_uses=1)
                await interaction.response.send_message(invite, ephemeral=True)
                return
        else:
            await interaction.response.send_message("No available lobbies, please try again later!", ephemeral=True)

    @app_commands.command(name="create_private_lobby", description="Creates a new private gaming room")
    async def create_private_lobby(self, interaction: discord.Interaction):
        lobby_id = await self.find_id()
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
        self.join_codes[code] = self.lobbies[lobby_id]
        message = await text.send(f"***=== LOBBY CODE ===***\n\t\t\t{code}\n***==================***", silent=True)
        await message.pin()
        asyncio.create_task(self.destruction(lobby_id))

    @app_commands.command(name="join_private_lobby", description="Join private lobby")
    @app_commands.describe(code="Lobby's join code")
    async def join_private_lobby(self, interaction: discord.Interaction, code: str):
        if self.check_code(code):
            invite = await self.join_codes.get(code).voice_channel.create_invite(max_age=180, max_uses=1)
            await interaction.user.add_roles(self.join_codes.get(code).role)
            await interaction.response.send_message(invite, ephemeral=True)
        else:
            await interaction.response.send_message("Lobby with such join code doesn't exist!", ephemeral=True)
