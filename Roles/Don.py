import discord

from Roles.Role import Role
from Roles.Mafia import Mafia
from Roles.Commissioner import Commissioner
from GameSession.Player import Player


class Don(Mafia):
    team = Role.RoleTeam.BLACK
    name = "Дон"
    description = "Вы играете за черных. Ваша задача - избавиться от всех красных игроков в городе и" \
                  " обнаружить комиссара, как можно скорее." \
                  " Ночью вы просыпаетесь дважды, сначала вместе с другими представителями мафии, затем отдельно." \
                  " Мафия убивает одного игрока за ночь, выбранного общим решением."
    image = "Data/civilian.jpg"
    multiplier = 1.75
    role_answer = ["Игрок {} является комиссаром", "Игрок {} не является комиссаром"]

    @staticmethod
    async def role_info(interaction: discord.Interaction, target: str, player: Player):
        if player.role == Commissioner:
            await interaction.response.send_message(Don.role_answer[0].format(target), ephemeral=True)
        else:
            await interaction.response.send_message(Don.role_answer[1].format(target), ephemeral=True)