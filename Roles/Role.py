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

    @property
    @abstractmethod
    def night_answer(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def night_info(interaction: discord.Interaction, target: str, player):
        raise NotImplementedError

    @classmethod
    def get_embed(cls):
        emb = discord.Embed(title=f"Ваша роль — {cls.name}.", colour=discord.Color.darker_grey())
        emb.add_field(name="Описание роли:", value=cls.description)
        file = discord.File(f"{cls.image}", filename="image.png")
        emb.set_image(url=f"attachment://image.png")
        return [file, emb]
