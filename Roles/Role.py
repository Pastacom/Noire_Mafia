from enum import Enum
from abc import ABC, abstractmethod

import discord


class Role(ABC):
    class RoleTeam(Enum):
        RED = "red",
        BLACK = "black",
        NEUTRAL = "neutral"

    @property
    @abstractmethod
    def team(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def image(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def multiplier(self):
        raise NotImplementedError

    @classmethod
    def get_embed(cls):
        file = discord.File(f"{cls.image}", filename="image.png")
        emb = discord.Embed(title=f"Your role is {cls.name}.", colour=discord.Color.darker_grey())
        emb.add_field(name="Role description:", value=cls.description)
        emb.set_image(url=f"attachment://image.png")
        return [file, emb]
