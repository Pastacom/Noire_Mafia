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
    night_answer = ["Вы перевернулись на другой бок. Мирные жители не ходят ночью!"]

    @staticmethod
    async def night_info(interaction: discord.Interaction, target: str, player: Player):
        await interaction.response.send_message(Civilian.night_answer[0], ephemeral=True)
