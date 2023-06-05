import discord

from GameSession.Settings import Settings
import GameSession.SettingsMenu.Main as Main


class GameModeScreen(discord.ui.View):

    def __init__(self, settings: Settings):
        options = [
            discord.SelectOption(label="Back", emoji='⬅'),
            discord.SelectOption(label="Bot", emoji='🤖', default=settings.game_mode_auto,
                                 description="Noire Mafia bot will lead you through this game."),
            discord.SelectOption(label="Human", emoji='🤵', default=not settings.game_mode_auto,
                                 description="Your host will lead you through this game.")
        ]
        super().__init__()
        select = discord.ui.Select(placeholder="GameMode", min_values=1, max_values=1, options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.data.get("values")[0] == "Back":
            await interaction.response.edit_message(view=Main.MainScreen(self.settings))
        elif interaction.data.get("values")[0] == "Bot":
            self.settings.game_mode_auto = True
            await interaction.response.edit_message(view=GameModeScreen(self.settings))
        elif interaction.data.get("values")[0] == "Human":
            self.settings.game_mode_auto = False
            await interaction.response.edit_message(view=GameModeScreen(self.settings))
