import discord

from GameSession.Settings import Settings
import GameSession.SettingsMenu.Main as Main


class MuteScreen(discord.ui.View):

    def __init__(self, settings: Settings):
        options = [
            discord.SelectOption(label="Back", emoji='⬅'),
            discord.SelectOption(label="Enabled", emoji='🔇', default=settings.mutes,
                                 description="Enable muting players during specific game stages."),
            discord.SelectOption(label="Disabled", emoji='🔊', default=not settings.mutes,
                                 description="Disable muting players during specific game stages.")
        ]
        super().__init__()
        select = discord.ui.Select(placeholder="Mute", min_values=1, max_values=1, options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.data.get("values")[0] == "Back":
            await interaction.response.edit_message(view=Main.MainScreen(self.settings))
        elif interaction.data.get("values")[0] == "Enabled":
            self.settings.mutes = True
            await interaction.response.edit_message(view=MuteScreen(self.settings))
        elif interaction.data.get("values")[0] == "Disabled":
            self.settings.mutes = False
            await interaction.response.edit_message(view=MuteScreen(self.settings))
