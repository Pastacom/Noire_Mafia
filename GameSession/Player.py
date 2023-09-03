import asyncio

import discord


class Player:

    def __init__(self, user: discord.Member):
        self.user = user
        self.role = None
        self.ready = False

