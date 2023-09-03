import asyncio
from enum import Enum

import discord

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

    def __init__(self, text_channel: discord.TextChannel,
                 voice_channel: discord.VoiceChannel, players, settings: Settings):
        self.text_channel = text_channel
        self.voice_channel = voice_channel
        self.players = players
        self.settings = settings
        self.turn = None
        self.status = None
        self.timer_break = False

    async def mute(self, player, mute=True):
        if self.settings.mutes:
            try:
                await player.user.edit(mute=mute)
            except discord.HTTPException:
                pass

    async def mute_all(self, mute=True):
        if self.settings.mutes:
            for player in self.players:
                try:
                    await player.user.edit(mute=mute)
                except discord.HTTPException:
                    pass

    async def end(self, user: discord.User):
        if ((self.status == self.Status.DAY_SPEECH_WITHOUT_VOTES or
             self.status == self.Status.DAY_SPEECH or
             self.status == self.Status.JUSTIFICATION_SPEECH or
             self.status == self.Status.CONDEMNED_SPEECH)
                and self.turn == user):
            self.timer_break = True

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

    async def day_timer(self, time, player):
        message = await self.text_channel.send('Ваш ход ' + player.user.mention)
        await self.timer(time)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    async def meeting_day(self):
        self.status = self.Status.DAY_SPEECH_WITHOUT_VOTES
        await self.mute_all()
        await self.text_channel.send("🤝 **Начинается день знакомств** 🤝")
        for player in self.players:
            self.turn = player.user
            await self.mute(player, False)
            await self.day_timer(self.settings.time_limits.get("day speech"), player)
            await self.mute(player)

    async def start(self):
        await self.text_channel.send("💠 **ИГРА НАЧАЛАСЬ** 💠")
        await self.meeting_day()
