import discord
from discord.ext import commands
from discord import app_commands

from GameSettings.Settings import Settings
from GameSettings.SettingsMenu.Main import MainScreen
from Utils.CogStatus import Status


class Setup(commands.Cog, name="Setup"):

    player_settings = {}

    def __init__(self, client: discord.ext.commands.Bot, mode: Status):
        self.client = client
        self.status = mode

    @app_commands.command(name="settings", description="Change game settings")
    async def settings(self, interaction: discord.Interaction):
        if self.player_settings.get(interaction.user.id) is None:
            self.player_settings[interaction.user.id] = Settings()
        settings = self.player_settings.get(interaction.user.id)
        await interaction.response.send_message(view=MainScreen(settings), ephemeral=True)

    async def get_settings(self, user_id):
        settings = self.player_settings.get(user_id)
        if settings is None:
            return Settings()
        return settings
