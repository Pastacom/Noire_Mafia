import discord

from Roles.Role import Role
from GameSession.Player import Player


class Mafia(Role):

    team = Role.RoleTeam.BLACK
    name = "Мафия"
    description = "Вы играете за черных. Ваша задача - избавиться от всех красных игроков в городе." \
                  " Ночью вы просыпаетесь вместе с другими представителями мафии." \
                  " Мафия убивает одного игрока за ночь, выбранного общим решением." \
                  " Если возникают разногласия, то финальное решение принимается Доном мафии." \
                  " При смерти Дона, убивается цель, за которую проголосовало большее кол-во игроков."
    image = "Data/civilian.jpg"
    multiplier = 1.5
    night_answer = ["Вы проголосовали за убийство игрока {}"]

    @staticmethod
    async def night_info(interaction: discord.Interaction, target: str, player: Player):
        await interaction.response.send_message(Mafia.night_answer[0].format(target), ephemeral=True)




