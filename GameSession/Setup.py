import discord
from discord.ext import commands
from discord import app_commands

from GameSession.SettingsMenu import MainScreen
from GameSession.Settings import Settings
from Utils.CogStatus import Status


class Setup(commands.Cog, name="Setup"):
    player_settings = {}

    def __init__(self, client: discord.ext.commands.Bot, mode: Status):
        self.client = client
        self.status = mode

    async def confirm(self, settings: Settings, user: discord.User):
        self.player_settings[user.id] = settings

    @app_commands.command(name="settings", description="Change game settings")
    async def settings(self, interaction: discord.Interaction):
        if self.player_settings.get(interaction.user.id) is None:
            settings = Settings()
        else:
            settings = self.player_settings.get(interaction.user.id)
        await interaction.response.send_message(view=MainScreen(settings))
