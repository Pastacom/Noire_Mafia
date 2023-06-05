import discord

from GameSession.Settings import Settings
import GameSession.SettingsMenu.Role as Role
import GameSession.SettingsMenu.GameMode as GameMode
import GameSession.SettingsMenu.Mute as Mute
import GameSession.SettingsMenu.Time as Time
import GameSession.SettingsMenu.Reveal as Reveal


class MainScreen(discord.ui.View):
    def __init__(self, settings: Settings):
        options = [
            discord.SelectOption(label="Roles", emoji='🤠',
                                 description="Choose which roles will be envolved in game."),
            discord.SelectOption(label="Game Mode", emoji='⚙',
                                 description="Choose whether human or bot will lead this game."),
            discord.SelectOption(label="Mute", emoji='🔇',
                                 description="Choose whether players can be muted during the game."),
            discord.SelectOption(label="Time", emoji='⏰',
                                 description="Choose time limits for different game events."),
            discord.SelectOption(label="Reveal Roles", emoji='🕵️‍♂️',
                                 description="Choose whether role can be revealed after player's death."),
            discord.SelectOption(label="Save", emoji='✅',
                                 description="Confirm and save all changes."),
            discord.SelectOption(label="Discard", emoji='❌',
                                 description="Discard all changes.")
        ]
        super().__init__()
        select = discord.ui.Select(placeholder="Settings", min_values=1, max_values=1, options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.data.get("values")[0] == "Roles":
            await interaction.response.edit_message(view=Role.RoleScreen(self.settings))
        elif interaction.data.get("values")[0] == "Game Mode":
            await interaction.response.edit_message(view=GameMode.GameModeScreen(self.settings))
        elif interaction.data.get("values")[0] == "Mute":
            await interaction.response.edit_message(view=Mute.MuteScreen(self.settings))
        elif interaction.data.get("values")[0] == "Time":
            await interaction.response.edit_message(view=Time.TimeScreen(self.settings))
        elif interaction.data.get("values")[0] == "Reveal Roles":
            await interaction.response.edit_message(view=Reveal.RevealScreen(self.settings))
        elif interaction.data.get("values")[0] == "Save":
            await interaction.response.send_message("Changes applied.")
        elif interaction.data.get("values")[0] == "Discard":
            await interaction.response.send_message("Changes discarded.")
