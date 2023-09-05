import asyncio
from enum import Enum

import discord

from GameSession.Player import Player
from GameSettings.Settings import Settings
from Roles.Civilian import Civilian
from Roles.Commissioner import Commissioner
from Roles.Doctor import Doctor
from Roles.Don import Don
from Roles.Mafia import Mafia


class Session:
    class Status(Enum):
        DAY_SPEECH_WITHOUT_VOTES = "day speech without votes"
        DAY_SPEECH = "day speech"
        JUSTIFICATION_SPEECH = "justification speech"
        VOTE = "vote"
        CONDEMNED_SPEECH = "condemned speech"
        SINGLE_ROLE_TURN = "single role turn"
        TEAM_ROLE_TURN = "team role turn"

    turns_sequence = [Mafia, Don, Commissioner, Doctor]
    turns_status = [Status.TEAM_ROLE_TURN, Status.SINGLE_ROLE_TURN, Status.SINGLE_ROLE_TURN, Status.SINGLE_ROLE_TURN]

    def __init__(self, text_channel: discord.TextChannel,
                 voice_channel: discord.VoiceChannel, user_to_player, settings: Settings):
        self.text_channel = text_channel
        # Check if needed later
        self.voice_channel = voice_channel
        self.user_to_player = user_to_player
        self.settings = settings
        self.action_targets = []
        self.killed = []
        self.turn = None
        self.status = None
        self.current_role = None
        self.timer_break = False

    async def mute(self, user, mute=True):
        if self.settings.mutes:
            try:
                await user.edit(mute=mute)
            except discord.HTTPException:
                pass

    async def mute_all(self, mute=True):
        if self.settings.mutes:
            for user in self.user_to_player.keys():
                try:
                    await user.edit(mute=mute)
                except discord.HTTPException:
                    pass

    async def end(self, interaction: discord.Interaction):
        if ((self.status == self.Status.DAY_SPEECH_WITHOUT_VOTES or
             self.status == self.Status.DAY_SPEECH or
             self.status == self.Status.JUSTIFICATION_SPEECH or
             self.status == self.Status.CONDEMNED_SPEECH)
                and self.turn == interaction.user):
            self.timer_break = True
            await interaction.response.send_message("Вы досрочно завершили свою речь.", ephemeral=True)
        else:
            await interaction.response.send_message("Вы не можете завершить речь в данный момент.", ephemeral=True)

    async def timer(self, time):
        self.timer_break = False
        time_message = await self.text_channel.send(f"{time // 60}:{(time % 60) // 10}{(time % 60) % 10}")
        for i in range(time - 1, -1, -1):
            if self.timer_break:
                break
            await asyncio.sleep(1)
            try:
                await time_message.edit(content=f"{i // 60}:{(i % 60) // 10}{(i % 60) % 10}")
            except discord.NotFound:
                pass
        try:
            await time_message.delete()
        except discord.NotFound:
            pass

    async def day_timer(self, time, user):
        message = await self.text_channel.send('Ваш ход ' + user.mention)
        await self.timer(time)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    async def night_timer(self, time):
        message = await self.text_channel.send('Ходит ' + self.current_role.name)
        await self.timer(time)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    async def action(self, interaction: discord.Interaction, target: discord.User):
        if target not in self.user_to_player:
            await interaction.response.send_message(f"There is no player in game with name {target.mention}",
                                                    ephemeral=True)
            return
        player = self.user_to_player[interaction.user]
        if player.status != Player.Status.ALIVE:
            await interaction.response.send_message(f"Player with name {target.mention} is already dead", ephemeral=True)
            return
        if not player.action_available:
            await interaction.response.send_message(f"Wait for your turn to make an action", ephemeral=True)
            return
        if player.action_performed:
            await interaction.response.send_message(f"You have already made an action during the night",
                                                    ephemeral=True)
            return
        if player.role == Doctor:
            if target == interaction.user and player.special == 0:
                await interaction.response.send_message(f"Доктор может вылечить себя лишь раз за игру.", ephemeral=True)
                return
            if target == player.last_target:
                await interaction.response.send_message(f"Доктор не может лечить одного и того же человека"
                                                        f" два хода подряд.", ephemeral=True)
                return
        self.action_targets.append(target)
        player.action_performed = True
        player.last_target = target
        if issubclass(player.role, self.current_role):
            await self.current_role.night_info(interaction, target.mention, player)
        else:
            await player.role.night_info(interaction, target.mention, player)

    async def prepare_night_turn(self):
        for player in self.user_to_player.values():
            if player.role == self.current_role or issubclass(player.role, self.current_role):
                player.action_available = True
                player.action_performed = False

    async def mafia_turn(self):
        user_count = {}
        for user in self.action_targets:
            if user in user_count:
                user_count[user] += 1
            else:
                user_count[user] = 1
        top_users = sorted(user_count.items(), key=lambda x: x[1], reverse=True)[:2]
        if len(top_users) == 1 or (len(top_users) == 2 and top_users[0][1] != top_users[1][1]):
            self.killed.append(top_users[0][0])

    async def doctor_turn(self):
        for target in self.action_targets:
            for i in range(len(self.killed)):
                if target == self.killed[i]:
                    self.killed.pop(i)
                    break

    async def turn_result(self, case):
        if case == 0:
            await self.mafia_turn()
        elif case == 3:
            await self.doctor_turn()

    async def night(self):
        self.killed.clear()
        await self.text_channel.send("🌃 **Наступает ночь** 🌃")
        for i, role in enumerate(Session.turns_sequence):
            self.action_targets.clear()
            self.current_role = role
            self.status = Session.turns_status[i]
            await self.prepare_night_turn()
            key = "single role" if self.status == self.Status.SINGLE_ROLE_TURN else "team role"
            await self.night_timer(self.settings.time_limits.get(key))
            await self.turn_result(i)

    async def meeting_day(self):
        self.status = self.Status.DAY_SPEECH_WITHOUT_VOTES
        await self.mute_all()
        await self.text_channel.send("🤝 **Начинается день знакомств** 🤝")
        for user in self.user_to_player.keys():
            self.turn = user
            await self.mute(user, False)
            await self.day_timer(self.settings.time_limits.get("day speech"), user)
            await self.mute(user)
        await self.text_channel.send("💤 **Город засыпает** 💤")
        await asyncio.sleep(5)
        await self.night()

    async def start(self):
        await self.text_channel.send("💠 **ИГРА НАЧАЛАСЬ** 💠")
        await self.meeting_day()
