import discord

from Roles.Role import Role
from Roles.Mafia import Mafia
from GameSession.Player import Player


class Commissioner(Role):
    team = Role.RoleTeam.RED
    name = "Комиссар"
    description = "Вы играете за красных. Ваша задача - искать мафиози ночью." \
                  " Когда вы просыпаетесь, вы можете выбрать любого игрока, если это черный игрок," \
                  " ведущий даст соответсвующий ответ. При проверке маньяка, ведущий скажет, что он играет за мирных." \
                  " Результаты проверки известны только вам, но вы всегда можете огласить их днем для всех остальных."
    image = "Data/civilian.jpg"
    multiplier = 1.75
    night_answer = ["Игрок {} является мафией", "Игрок {} не является мафией"]

    @staticmethod
    async def night_info(interaction: discord.Interaction, target: str, player: Player):
        if player.role == Mafia or issubclass(player.role, Mafia):
            await interaction.response.send_message(Commissioner.night_answer[0].format(target), ephemeral=True)
        else:
            await interaction.response.send_message(Commissioner.night_answer[1].format(target), ephemeral=True)
