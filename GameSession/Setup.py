import string
import random
from enum import Enum

import discord
from discord.ext import commands
from discord import app_commands
import asyncio

from GameSession.SettingMenu import MainScreen
from GameSession.Settings import Settings
from Utils.CogStatus import Status


class Setup(commands.Cog, name="Setup"):
    player_settings = {}

    def __init__(self, client: discord.ext.commands.Bot, mode: Status):
        self.client = client
        self.status = mode

    @app_commands.command(name="settings", description="Change game settings")
    async def settings(self, interaction: discord.Interaction):
        settings = Settings()
        await interaction.response.send_message(view=MainScreen())
