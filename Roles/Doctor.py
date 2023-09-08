import discord

from Roles.Civilian import Civilian
from Roles.Role import Role
from GameSession.Player import Player


class Doctor(Civilian):
    team = Role.RoleTeam.RED
    name = "Доктор"
    description = "Вы играете за красных. Ваша задача - спасать от покушения игроков." \
                  " Когда вы просыпаетесь ночью, вы можете выбрать любого игрока(включая себя)," \
                  " если его пытались убить этой ночью, то он выживает, благодаря вам." \
                  " Нельзя лечить одного и того же игрока две ночи подряд." \
                  " Доктор может вылечить себя один раз за игру."
    image = "Data/civilian.jpg"
    multiplier = 1.6
    role_answer = ["Вы лечите игрока {}"]

    @staticmethod
    async def role_info(interaction: discord.Interaction, target: str, player: Player):
        await interaction.response.send_message(Doctor.role_answer[0].format(target), ephemeral=True)