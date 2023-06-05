import discord

from GameSession.Settings import Settings
import GameSession.SettingsMenu.Main as Main


class RoleScreen(discord.ui.View):

    def __init__(self, settings: Settings):
        options = [
            discord.SelectOption(label="{}".format(role.capitalize()), default=settings.role_seed[role])
            for role in settings.role_seed.keys()
        ]
        options.insert(0, discord.SelectOption(label="Back", emoji='⬅'))
        super().__init__()
        select = discord.ui.Select(placeholder="RoleSeed", min_values=1, max_values=len(settings.role_seed) + 1,
                                   options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        for role in self.settings.role_seed.keys():
            self.settings.role_seed[role] = False
        for value in interaction.data.get("values"):
            if value != "Back":
                self.settings.role_seed[value.lower()] = True
        if "Back" in interaction.data.get("values"):
            await interaction.response.edit_message(view=Main.MainScreen(self.settings))
        else:
            await interaction.response.edit_message(view=RoleScreen(self.settings))
