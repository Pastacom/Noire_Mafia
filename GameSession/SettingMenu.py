import discord


class MainScreen(discord.ui.View):
    @discord.ui.select(
        placeholder="Settings",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Roles",
                emoji='🤠',
                description="Choose which roles will be envolved in game."
            ),
            discord.SelectOption(
                label="Game Mode",
                emoji='⚙',
                description="Choose whether human or bot will lead this game."
            ),
            discord.SelectOption(
                label="Mute",
                emoji='🔇',
                description="Choose whether players will be muted if they don't have the right to speak."
            ),
            discord.SelectOption(
                label="Time",
                emoji='⏰',
                description="Choose time limits for different game events."
            ),
            discord.SelectOption(
                label="Save",
                emoji='✅',
                description="Confirm and saves all changes."
            )
        ],)
    async def select_callback(self, interaction: discord.Interaction, select: discord.SelectOption):
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")
