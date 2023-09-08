import discord

from Roles.Role import Role
from GameSession.Player import Player


class Civilian(Role):
    team = Role.RoleTeam.RED
    name = "Мирный житель"
    description = "Вы играете за красных. Ваша задача состоит в том, чтобы вычислить представителей мафии" \
                  " и посадить в тюрьму." \
                  " Сделать это вы можете только на дневном голосовании."
    image = "Data/civilian.jpg"
    multiplier = 1.4
    role_answer = ["Вы выставили игрока {} на голосование."]

    @staticmethod
    async def role_info(interaction: discord.Interaction, target: str, player: Player):
        await interaction.response.send_message(Civilian.role_answer[0].format(target), ephemeral=True)
