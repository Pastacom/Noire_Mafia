import asyncio
import math
import random
from enum import Enum

import discord

from GameSession.Player import Player
from GameSession.Session import Session
from GameSettings.Settings import Settings
from Roles.Civilian import Civilian
from Roles.Commissioner import Commissioner
from Roles.Doctor import Doctor
from Roles.Don import Don
from Roles.Mafia import Mafia


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
        self.user_to_player = {}
        self.waiting_players = 0
        self.session = None

    async def set_default_nicknames(self):
        for user in self.user_to_player.keys():
            try:
                await user.edit(nick=user.name)
            except discord.Forbidden:
                pass

    async def restart_game(self):
        self.status = self.Status.SETUP
        if self.session is not None:
            await self.session.mute_all(False)
            self.session = None
        await self.set_default_nicknames()
        self.user_to_player.clear()

    async def launch_game(self, settings: Settings):
        self.session = Session(self.text_channel, self.user_to_player, settings)
        await self.session.start()

    async def create_session(self):
        self.status = self.Status.READY
        for user in self.voice_channel.members:
            self.user_to_player[user] = Player()
        self.waiting_players = len(self.voice_channel.members)
        text = "Пожалуйста, подтвердите свою готовность к игре.\n"
        for user in self.user_to_player.keys():
            text += user.mention + '\n'
            try:
                await user.edit(nick=user.name + ' ❌')
            except discord.Forbidden:
                pass
        await self.text_channel.send(text)

    async def cleanup(self):
        await asyncio.sleep(10)
        while len(self.voice_channel.members) != 0:
            await asyncio.sleep(10)
        await self.role.delete()
        await self.text_channel.delete()
        await self.voice_channel.delete()
        await self.category.delete()
        await self.set_default_nicknames()
        try:
            await self.session.mute_all(False)
        except AttributeError:
            pass

    async def give_roles(self):
        roles = [Don, Commissioner, Doctor]
        players_count = len(self.user_to_player) - 3
        mafia_count = max(0, math.ceil(players_count / 4) - 1)
        players_count -= mafia_count
        for i in range(mafia_count):
            roles.append(Mafia)
        for i in range(players_count):
            roles.append(Civilian)
        random.shuffle(roles)
        i = 0
        for user, player in self.user_to_player.items():
            player.set_role(roles[i])
            role_to_send = roles[i].get_embed()
            await user.send(file=role_to_send[0], embed=role_to_send[1])
            i += 1
        await self.text_channel.send("**Роли игроков в игре:**" + "\n\n" +
                                     f"Мирных жителей: {players_count}\n" +
                                     f"Мафий: {mafia_count}\n" +
                                     "Дон мафии\n" +
                                     "Комиссар\n" +
                                     "Доктор\n\n")
