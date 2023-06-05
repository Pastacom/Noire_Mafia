import discord

from GameSession.Settings import Settings


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
        if interaction.data.get("values")[0] == "Game Mode":
            await interaction.response.edit_message(view=GameModeScreen(self.settings))
        elif interaction.data.get("values")[0] == "Mute":
            await interaction.response.edit_message(view=MuteScreen(self.settings))
        elif interaction.data.get("values")[0] == "Time":
            await interaction.response.edit_message(view=TimeScreen(self.settings))
        elif interaction.data.get("values")[0] == "Reveal Roles":
            await interaction.response.edit_message(view=RevealScreen(self.settings))
        elif interaction.data.get("values")[0] == "Save":
            await interaction.response.send_message("Changes applied.")
            # confirm(self.settings, interaction.user)
        elif interaction.data.get("values")[0] == "Discard":
            await interaction.response.send_message("Changes discarded.")


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
            await interaction.response.edit_message(view=MainScreen(self.settings))
        elif interaction.data.get("values")[0] == "Enabled":
            self.settings.mutes = True
            await interaction.response.edit_message(view=MuteScreen(self.settings))
        elif interaction.data.get("values")[0] == "Disabled":
            self.settings.mutes = False
            await interaction.response.edit_message(view=MuteScreen(self.settings))


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
            await interaction.response.edit_message(view=MainScreen(self.settings))
        elif interaction.data.get("values")[0] == "Bot":
            self.settings.game_mode_auto = True
            await interaction.response.edit_message(view=GameModeScreen(self.settings))
        elif interaction.data.get("values")[0] == "Human":
            self.settings.game_mode_auto = False
            await interaction.response.edit_message(view=GameModeScreen(self.settings))


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
                                 description="Time allotted for day speech."),
            discord.SelectOption(label="Justification speech: {}"
                                 .format(get_time(settings.time_limits.get("justification speech"))), emoji='🗣',
                                 description="Time allotted for justification speech."),
            discord.SelectOption(label="Voting: {}"
                                 .format(get_time(settings.time_limits.get("vote"))), emoji='📢',
                                 description="Time allotted for voting."),
            discord.SelectOption(label="Condemned speech: {}"
                                 .format(get_time(settings.time_limits.get("condemned speech"))), emoji='⚖',
                                 description="Time allotted for condemned speech."),
            discord.SelectOption(label="Single role: {}"
                                 .format(get_time(settings.time_limits.get("single role"))), emoji='👤',
                                 description="Time allotted for action of a single role."),
            discord.SelectOption(label="Team role: {}"
                                 .format(get_time(settings.time_limits.get("team role"))), emoji='👥',
                                 description="Time allotted for action of a team role."),
        ]
        super().__init__()
        select = discord.ui.Select(placeholder="Time", min_values=1, max_values=1, options=options)
        select.callback = self.select_callback
        self.add_item(select)
        self.settings = settings

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.data.get("values")[0] == "Back":
            await interaction.response.edit_message(view=MainScreen(self.settings))
        elif interaction.data.get("values")[0] == \
                ("Day speech: {}".format(get_time(self.settings.time_limits.get("day speech")))):
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "day speech"))
        elif interaction.data.get("values")[0] == \
                ("Justification speech: {}".format(get_time(self.settings.time_limits.get("justification speech")))):
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "justification speech"))
        elif interaction.data.get("values")[0] == \
                ("Voting: {}".format(get_time(self.settings.time_limits.get("vote")))):
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "vote"))
        elif interaction.data.get("values")[0] == \
                ("Condemned speech: {}".format(get_time(self.settings.time_limits.get("condemned speech")))):
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "condemned speech"))
        elif interaction.data.get("values")[0] == \
                ("Single role: {}".format(get_time(self.settings.time_limits.get("single role")))):
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "single role"))
        elif interaction.data.get("values")[0] == \
                ("Team role: {}".format(get_time(self.settings.time_limits.get("team role")))):
            await interaction.response.edit_message(view=TimeOptionScreen(self.settings, "team role"))


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
            await interaction.response.edit_message(view=MainScreen(self.settings))
        elif interaction.data.get("values")[0] == "Hide":
            self.settings.hide = True
            await interaction.response.edit_message(view=RevealScreen(self.settings))
        elif interaction.data.get("values")[0] == "Reveal":
            self.settings.hide = False
            await interaction.response.edit_message(view=RevealScreen(self.settings))
