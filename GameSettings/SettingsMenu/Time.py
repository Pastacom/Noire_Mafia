import discord

from GameSettings.Settings import Settings
import GameSettings.SettingsMenu.Main as Main


def get_time(seconds):
    ans = ""
    if seconds >= 60:
        ans += f"{seconds // 60} min"
        seconds %= 60
    if seconds != 0:
        ans += f" {seconds} sec"
    return ans


class TimeOptionScreen(discord.ui.View):
    def __init__(self, settings: Settings, time):
        options = [
            discord.SelectOption(label="{}".format(get_time(x)), default=(x == settings.time_limits[time]))
            for x in range(5, 125, 5)
        ]
        options.insert(0, discord.SelectOption(label="Back", emoji='⬅'))
        super().__init__()
        select = discord.ui.Select(placeholder="TimeOption", min_values=1, max_values=1, options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.time = time
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.data.get("values")[0] == "Back":
            await interaction.response.edit_message(view=TimeScreen(self.settings))
        else:
            for i in range(5, 125, 5):
                if interaction.data.get("values")[0] == get_time(i).strip():
                    self.settings.time_limits[self.time] = i
                    break
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, self.time))


class TimeScreen(discord.ui.View):

    def __init__(self, settings: Settings):
        options = [
            discord.SelectOption(label="Back", emoji='⬅'),
            discord.SelectOption(label="Day speech: {}"
                                 .format(get_time(settings.time_limits.get("day speech"))), emoji='☀',
                                 description="Time allotted for day speech.", value="Day"),
            discord.SelectOption(label="Justification speech: {}"
                                 .format(get_time(settings.time_limits.get("justification speech"))), emoji='🗣',
                                 description="Time allotted for justification speech.", value="Justification"),
            discord.SelectOption(label="Voting: {}"
                                 .format(get_time(settings.time_limits.get("vote"))), emoji='📢',
                                 description="Time allotted for voting.", value="Voting"),
            discord.SelectOption(label="Condemned speech: {}"
                                 .format(get_time(settings.time_limits.get("condemned speech"))), emoji='⚖',
                                 description="Time allotted for condemned speech.", value="Condemned"),
            discord.SelectOption(label="Single role: {}"
                                 .format(get_time(settings.time_limits.get("single role"))), emoji='👤',
                                 description="Time allotted for action of a single role.", value="Single"),
            discord.SelectOption(label="Team role: {}"
                                 .format(get_time(settings.time_limits.get("team role"))), emoji='👥',
                                 description="Time allotted for action of a team role.", value="Team"),
        ]
        super().__init__()
        select = discord.ui.Select(placeholder="Time", min_values=1, max_values=1, options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.data.get("values")[0] == "Back":
            await interaction.response.edit_message(view=Main.MainScreen(self.settings))
        elif interaction.data.get("values")[0] == "Day":
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "day speech"))
        elif interaction.data.get("values")[0] == "Justification":
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "justification speech"))
        elif interaction.data.get("values")[0] == "Voting":
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "vote"))
        elif interaction.data.get("values")[0] == "Condemned":
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "condemned speech"))
        elif interaction.data.get("values")[0] == "Single":
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "single role"))
        elif interaction.data.get("values")[0] == "Team":
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "team role"))
