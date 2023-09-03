import asyncio
from enum import Enum

import discord

from GameSession.Player import Player


class Lobby:
    class Status(Enum):
        SETUP = "setup"
        READY = "ready"
        PLAYING = "playing"

    def __init__(self, category: discord.CategoryChannel,
                 text_channel: discord.TextChannel, voice_channel: discord.VoiceChannel, code,
                 role: discord.Role, host: discord.User, public=True):
        self.category = category
        self.text_channel = text_channel
        self.voice_channel = voice_channel
        self.status = self.Status.SETUP
        self.code = code
        self.role = role
        self.host = host
        self.public = public
        self.players = []
        self.waiting_players = 0

    async def set_default_nicknames(self):
        for player in self.players:
            try:
                await player.user.edit(nick=player.user.name)
            except discord.Forbidden:
                pass

    async def create_session(self):
        self.status = self.Status.READY
        for user in self.voice_channel.members:
            self.players.append(Player(user))
        self.waiting_players = len(self.voice_channel.members)
        text = "Пожалуйста, подтвердите свою готовность к игре.\n"
        for player in self.players:
            text += player.user.mention + '\n'
            try:
                await player.user.edit(nick=player.user.name + ' ❌')
            except discord.Forbidden:
                pass
        await self.text_channel.send(text)

    async def cleanup(self):
        await asyncio.sleep(10)
        while len(self.voice_channel.members) != 0:
            await asyncio.sleep(10)
        if self.role != self.category.guild.default_role:
            await self.role.delete()
        await self.text_channel.delete()
        await self.voice_channel.delete()
        await self.category.delete()
        await self.set_default_nicknames()
        del self
