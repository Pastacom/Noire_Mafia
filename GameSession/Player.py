from enum import Enum

import discord

from Roles import Role


class Player:

    class Status(Enum):
        ALIVE = "alive"
        DEAD = "dead"
        DISCONNECTED = "disconnected"

    def __init__(self):
        self.role = None
        self.ready = False
        self.action_available = False
        self.action_performed = False
        self.status = self.Status.ALIVE
        self.last_target = None
        self.special = 1

    def set_role(self, role: Role):
        self.role = role
