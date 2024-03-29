import discord

from Roles.Civilian import Civilian
from Roles.Role import Role
from GameSession.Player import Player


class Courtesan(Civilian):
    team = Role.RoleTeam.RED
    name = "Куртизанка"
    description = "Вы играете за красных. Ваша задача - спасать красных." \
                  " Когда вы просыпаетесь ночью, вы можете выбрать любого игрока." \
                  " Выбранный игрок не может быть убит в эту ночь, но при этом теряет" \
                  " возможность использовать свою способность в эту ночь, если она у него есть." \
                  " Нельзя выбирать одного и того же игрока две ночи подряд." \
                  " Погибает, если выбирает ночным клиентом Маньяка." \
                  " Если мафиози остается один и вы выбираете его, то мафиози не убивают этой ночью."
    image = "Data/civilian.jpg"
    multiplier = 1.5
    role_answer = ["(N/I) {}"]

    @staticmethod
    async def role_info(interaction: discord.Interaction, target: str, player: Player):
        await interaction.response.send_message(Courtesan.role_answer[0].format(target), ephemeral=True)
