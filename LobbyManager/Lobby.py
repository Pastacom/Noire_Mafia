import asyncio
from enum import Enum

import discord


class Lobby:
    class Status(Enum):
        READY = "ready"
        SETUP = "setup"
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

    async def cleanup(self):
        await asyncio.sleep(10)
        while len(self.voice_channel.members) != 0:
            await asyncio.sleep(10)
        if self.role != self.category.guild.default_role:
            await self.role.delete()
        await self.text_channel.delete()
        await self.voice_channel.delete()
        await self.category.delete()
