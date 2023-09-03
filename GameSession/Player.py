import discord

from Roles import Role


class Player:

    def __init__(self, user: discord.Member):
        self.user = user
        self.role = None
        self.ready = False

    def set_role(self, role: Role):
        self.role = role
