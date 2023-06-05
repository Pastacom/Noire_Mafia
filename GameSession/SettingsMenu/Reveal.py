import discord

from GameSession.Settings import Settings
import GameSession.SettingsMenu.Main as Main


class RevealScreen(discord.ui.View):

    def __init__(self, settings: Settings):
        options = [
            discord.SelectOption(label="Back", emoji='⬅'),
            discord.SelectOption(label="Hide", emoji='❓', default=settings.hide,
                                 description="Role won't be revealed after player's death."),
            discord.SelectOption(label="Reveal", emoji='👁', default=not settings.hide,
                                 description="Role will be revealed after player's death.")
        ]
        super().__init__()
        select = discord.ui.Select(placeholder="Reveal", min_values=1, max_values=1, options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.data.get("values")[0] == "Back":
            await interaction.response.edit_message(view=Main.MainScreen(self.settings))
        elif interaction.data.get("values")[0] == "Hide":
            self.settings.hide = True
            await interaction.response.edit_message(view=RevealScreen(self.settings))
        elif interaction.data.get("values")[0] == "Reveal":
            self.settings.hide = False
            await interaction.response.edit_message(view=RevealScreen(self.settings))
