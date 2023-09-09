import asyncio
from enum import Enum

import discord

from GameSession.Player import Player
from GameSettings.Settings import Settings
from Roles.Civilian import Civilian
from Roles.Commissioner import Commissioner
from Roles.Doctor import Doctor
from Roles.Don import Don
from Roles.Mafia import Mafia
from Roles.Role import Role


class Session:
    class Status(Enum):
        MEETING_SPEECH = "meeting speech"
        DAY_SPEECH = "day speech"
        JUSTIFICATION_SPEECH = "justification speech"
        VOTE = "vote"
        CONDEMNED_SPEECH = "condemned speech"
        SINGLE_ROLE_TURN = "single role"
        TEAM_ROLE_TURN = "team role"

    turns_sequence = [Mafia, Don, Commissioner, Doctor]
    turns_status = [Status.TEAM_ROLE_TURN, Status.SINGLE_ROLE_TURN, Status.SINGLE_ROLE_TURN, Status.SINGLE_ROLE_TURN]

    def __init__(self, text_channel: discord.TextChannel,
                 voice_channel: discord.VoiceChannel, user_to_player, settings: Settings):
        self.text_channel = text_channel
        # Check if needed later
        self.voice_channel = voice_channel
        self.user_to_player = user_to_player
        self.settings = settings
        self.action_targets = []
        self.votes = {}
        self.killed = []
        self.turn = None
        self.status = None
        self.current_role = None
        self.timer_break = False


    def get_time(self):
        return self.settings.time_limits.get(self.status.value)


    async def mute(self, user, mute=True):
        if self.settings.mutes:
            try:
                await user.edit(mute=mute)
            except discord.HTTPException:
                pass

    async def mute_alive(self, user, mute=True):
        if self.settings.mutes:
            try:
                player = self.user_to_player[user]
                if player.status == Player.Status.ALIVE:
                    await user.edit(mute=mute)
            except discord.HTTPException:
                pass

    async def mute_all(self, mute=True):
        if self.settings.mutes:
            for user in self.user_to_player.keys():
                try:
                    await user.edit(mute=mute)
                except discord.HTTPException:
                    pass

    async def mute_all_alive(self, mute=True):
        if self.settings.mutes:
            for user, player in self.user_to_player.items():
                try:
                    if player.status == Player.Status.ALIVE:
                        await user.edit(mute=mute)
                except discord.HTTPException:
                    pass

    async def end(self, interaction: discord.Interaction):
        if ((self.status == self.Status.MEETING_SPEECH or
             self.status == self.Status.DAY_SPEECH or
             self.status == self.Status.JUSTIFICATION_SPEECH or
             self.status == self.Status.CONDEMNED_SPEECH)
                and self.turn == interaction.user):
            self.timer_break = True
            await interaction.response.send_message("Вы досрочно завершили свою речь.", ephemeral=True)
        else:
            await interaction.response.send_message("Вы не можете завершить речь в данный момент.", ephemeral=True)

    async def timer(self, time):
        self.timer_break = False
        time_message = await self.text_channel.send(f"{time // 60}:{(time % 60) // 10}{(time % 60) % 10}")
        for i in range(time - 1, -1, -1):
            if self.timer_break:
                break
            await asyncio.sleep(1)
            try:
                await time_message.edit(content=f"{i // 60}:{(i % 60) // 10}{(i % 60) % 10}")
            except discord.NotFound:
                pass
        try:
            await time_message.delete()
        except discord.NotFound:
            pass

    async def day_timer(self, time, user):
        message = await self.text_channel.send(f"Ваш ход {user.mention}")
        await self.timer(time)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    async def vote_timer(self, time, user):
        message = await self.text_channel.send(f"Кто голосует за игрока {user.mention}?")
        await self.timer(time)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    async def night_timer(self, time):
        message = await self.text_channel.send(f"Ходит {self.current_role.name}")
        await self.timer(time)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    async def action(self, interaction: discord.Interaction, target: discord.User):
        if target not in self.user_to_player:
            await interaction.response.send_message(f"В игре нет игрока с именем {target.mention}.",
                                                    ephemeral=True)
            return
        if self.user_to_player[target].status != Player.Status.ALIVE:
            await interaction.response.send_message(f"Игрок с именем {target.mention} уже мертв.",
                                                    ephemeral=True)
            return
        player = self.user_to_player[interaction.user]
        if player.status != Player.Status.ALIVE:
            await interaction.response.send_message("Вы не можете совершать действия, будучи мертвым.", ephemeral=True)
            return
        if not player.action_available:
            await interaction.response.send_message("Вы не можете совершать действия в данный момент.", ephemeral=True)
            return
        if player.action_performed:
            await interaction.response.send_message("Вы уже совершили свое действие.",
                                                    ephemeral=True)
            return
        if self.status == Session.Status.TEAM_ROLE_TURN or self.status == Session.Status.SINGLE_ROLE_TURN:
            if player.role == Doctor:
                if target == interaction.user and player.special == 0:
                    await interaction.response.send_message("Доктор может вылечить себя лишь раз за игру.",
                                                            ephemeral=True)
                    return
                if target == player.last_target:
                    await interaction.response.send_message("Доктор не может лечить одного и того же человека"
                                                            " два хода подряд.", ephemeral=True)
                    return
            player.last_target = target
        if self.current_role == Civilian:
            if target in self.action_targets:
                await interaction.response.send_message("Этот игрок уже выставлен на голосование.", ephemeral=True)
                return
        self.action_targets.append(target)
        player.action_performed = True
        if issubclass(player.role, self.current_role):
            await self.current_role.role_info(interaction, target.mention, self.user_to_player[target])
        else:
            await player.role.role_info(interaction, target.mention, self.user_to_player[target])

    async def whisper(self, interaction: discord.Interaction, message: discord.Message):
        player = self.user_to_player[interaction.user]
        if player.status != Player.Status.ALIVE:
            await interaction.response.send_message("Вы не можете шептать, будучи мертвым.", ephemeral=True)
            return
        if not player.action_available:
            await interaction.response.send_message("Дождитесь своего хода, чтобы шепнуть.", ephemeral=True)
            return
        if self.status != self.Status.TEAM_ROLE_TURN:
            await interaction.response.send_message("Шепот доступен только командным ролям во время ночи.",
                                                    ephemeral=True)
            return
        await interaction.response.send_message("Вы отправили сообщение своей команде.", ephemeral=True)
        for user, active_player in self.user_to_player.items():
            if (active_player.role == self.current_role or
                    issubclass(active_player.role, self.current_role) and interaction.user != user):
                await user.send(f"{interaction.user.name}({player.role.name}): {message}")

    async def vote(self, interaction: discord.Interaction):
        player = self.user_to_player[interaction.user]
        if player.status != Player.Status.ALIVE:
            await interaction.response.send_message("Вы не можете голосовать, будучи мертвым.", ephemeral=True)
            return
        if self.status != self.Status.VOTE:
            await interaction.response.send_message("Вы не можете голосовать в данный момент.",
                                                    ephemeral=True)
            return
        if player.action_performed:
            await interaction.response.send_message("Вы уже голосовали.", ephemeral=True)
            return
        await interaction.response.send_message(f"Вы проголосовали против игрока {self.turn.mention}.", ephemeral=True)
        player.action_performed = True
        self.votes[self.turn].append(interaction.user)

    async def prepare_night_turn(self):
        for player in self.user_to_player.values():
            if player.role == self.current_role or issubclass(player.role, self.current_role):
                player.action_available = True
                player.action_performed = False

    async def end_night_turn(self):
        for player in self.user_to_player.values():
            if player.role == self.current_role or issubclass(player.role, self.current_role):
                player.action_available = False

    async def mafia_turn(self):
        user_count = {}
        for user in self.action_targets:
            if user in user_count:
                user_count[user] += 1
            else:
                user_count[user] = 1
        top_users = sorted(user_count.items(), key=lambda x: x[1], reverse=True)[:2]
        if len(top_users) == 1 or (len(top_users) == 2 and top_users[0][1] != top_users[1][1]):
            self.killed.append(top_users[0][0])

    async def doctor_turn(self):
        for target in self.action_targets:
            for i in range(len(self.killed)):
                if target == self.killed[i]:
                    self.killed.pop(i)
                    break

    async def turn_result(self, case):
        if case == 0:
            await self.mafia_turn()
        elif case == 3:
            await self.doctor_turn()

    async def end_game(self):
        emb = discord.Embed(title=f"Роли игроков:", colour=discord.Color.darker_grey())
        for user, player in self.user_to_player.items():
            emb.add_field(name=f"{user.name} — {player.role.name}", value="", inline=False)
        await self.text_channel.send(embed=emb)

    async def win_condition(self):
        mafia = 0
        red = 0
        total = 0
        for player in self.user_to_player.values():
            if player.status == Player.Status.ALIVE:
                if player.role == Mafia or issubclass(player.role, Mafia):
                    mafia += 1
                elif player.role.team == Role.RoleTeam.RED:
                    red += 1
                total += 1
        if total == 0:
            await self.text_channel.send("**Игра окончена! Ничья. В городе не осталось живых** 💀")
            return True
        elif mafia >= red and mafia > 0:
            await self.text_channel.send("**Игра окончена! Победа мафии** 🕵️")
            return True
        elif mafia == 0 and red > 0:
            await self.text_channel.send("**Игра окончена! Победа мирного города** 👥")
            return True
        return False

    async def kill_players(self):
        for user in self.killed:
            self.user_to_player[user].status = Player.Status.DEAD
            if self.settings.hide:
                await self.text_channel.send(f"💀 **Ночью был убит игрок {user.mention}** 💀")
            else:
                await self.text_channel.send(f"💀 **Ночью был убит игрок {user.mention} —"
                                             f" {self.user_to_player[user].role.name}** 💀")
            try:
                await user.edit(nick=user.name + ' 💀')
            except discord.Forbidden:
                pass
            break
        else:
            await self.text_channel.send(f"🚫 **Ночью никто не был убит** 🚫")
        self.killed.clear()

    async def day_speech(self):
        await self.text_channel.send("🗣️ **Начинается обсуждение и выставление кандидатур на голосование** 🗣️")
        self.action_targets.clear()
        self.current_role = Civilian
        self.status = Session.Status.DAY_SPEECH
        for user, player in self.user_to_player.items():
            if player.status == Player.Status.ALIVE:
                self.turn = user
                player.action_available = True
                await self.mute(user, False)
                await self.day_timer(self.get_time(), user)
                await self.mute(user)
                player.action_available = False
        self.turn = None

    async def voting(self):
        self.votes.clear()
        for user in self.action_targets:
            self.votes[user] = []
        self.status = Session.Status.VOTE
        for player in self.user_to_player.values():
            player.action_performed = False
        for user in self.action_targets:
            self.turn = user
            await self.vote_timer(self.get_time(), user)
            message = f"Против игрока никто не проголосовал."
            if len(self.votes[self.turn]) != 0:
                message = f"Против игрока {self.turn.mention} проголосовало {len(self.votes[self.turn])}:\n"
                for i, voted_player in enumerate(self.votes[self.turn]):
                    message += f"{i+1}. {voted_player.mention}\n"
            await self.text_channel.send(message)
        self.turn = None

    async def justification_speech(self):
        await self.text_channel.send("👨‍⚖️ **Обвиняемым предоставляется оправдательная речь** 👨‍⚖️")
        self.status = Session.Status.JUSTIFICATION_SPEECH
        for user in self.action_targets:
            self.turn = user
            await self.mute(user, False)
            await self.day_timer(self.get_time(), user)
            await self.mute(user)
        self.turn = None

    async def day(self):
        await self.text_channel.send("⏰ **Город просыпается** ⏰")
        await asyncio.sleep(5)
        await self.text_channel.send("🌇 **Наступает день** 🌇")
        await self.kill_players()
        #if await self.win_condition():
           # await self.end_game()
            #return
        await asyncio.sleep(5)
        await self.day_speech()
        if len(self.action_targets) == 0:
            await self.text_channel.send("🚫 **Было принято решение никого не выставлять на голосование** 🚫")
        else:
            await self.justification_speech()
            await self.voting()

            if await self.win_condition():
                await self.end_game()
                return
        await self.night()

    async def night(self):
        await self.text_channel.send("💤 **Город засыпает** 💤")
        await asyncio.sleep(5)
        await self.text_channel.send("🌃 **Наступает ночь** 🌃")
        for i, role in enumerate(Session.turns_sequence):
            self.action_targets.clear()
            self.current_role = role
            self.status = Session.turns_status[i]
            await self.prepare_night_turn()
            await self.night_timer(self.get_time())
            await self.end_night_turn()
            await self.turn_result(i)
        await self.day()

    async def meeting_day(self):
        self.status = self.Status.MEETING_SPEECH
        await self.mute_all()
        await self.text_channel.send("🤝 **Начинается день знакомств** 🤝")
        for user in self.user_to_player.keys():
            self.turn = user
            await self.mute(user, False)
            await self.day_timer(self.get_time(), user)
            await self.mute(user)
        self.turn = None
        await self.night()

    async def start(self):
        await self.text_channel.send("💠 **ИГРА НАЧАЛАСЬ** 💠")
        await self.meeting_day()
