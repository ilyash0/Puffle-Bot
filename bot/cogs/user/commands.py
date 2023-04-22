from datetime import datetime
from random import sample

from loguru import logger
import disnake
from disnake.ext.commands import Cog, Param, slash_command
from bot.data.moderator import Logs
from bot.misc.penguin import Penguin
from bot.data.penguin import PenguinIntegrations
from bot.misc.buttons import Question, Continue
from bot.misc.modals import LoginModal
from bot.misc.utils import getPenguinFromInteraction


class UserCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info("Users commands ready")

    @slash_command(name="ilyash", description=":D")
    async def ilyash(self, interaction):
        await interaction.response.send_message(content=f"Теперь вы пешка иляша!")

    @slash_command(name="card", description="Показывает полезную информацию о твоём аккаунте")
    async def card(self, interaction):
        user = interaction.user
        p: Penguin = await getPenguinFromInteraction(interaction)

        embed = disnake.Embed(title="Карточка пингвина",
                              description=f"Знакомьтесь, этот пингвин принадлежит {user.mention}",
                              color=disnake.Color.from_rgb(3, 91, 209))
        embed.set_thumbnail(url=f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
        embed.add_field(name="ID", value=p.id)
        embed.add_field(name="Имя", value=p.safe_name())
        embed.add_field(name="Монеты", value=p.coins)
        embed.add_field(name="Марки", value=len(p.stamps) + p.countEpfAwards())
        embed.add_field(name="Возраст пингвина", value=f"{(datetime.now() - p.registration_date).days} дней")
        embed.add_field(name="Сотрудник", value="Да" if p.moderator else "Нет")
        await interaction.response.send_message(embed=embed)

    @slash_command(name="login", description="Привязать свой Discord аккаунт к пингвину")
    async def login(self, interaction, penguin: str = Param(description='Имя вашего пингвина')):
        user = interaction.user
        penguinId = await Penguin.select('id').where(Penguin.username == penguin.lower()).gino.first()
        penguinId = int(penguinId[0])
        p: Penguin = await Penguin.get(penguinId)

        symbols = "QWERTYUIOPASDFGHJKLZXCVBNM0123456789"
        authCode = "".join(sample(symbols, 8))

        await p.add_inbox(302, details=authCode)

        async def authApprove(modalInteraction, authCodeInput):
            await view.disableAllItems()
            if authCodeInput.upper() == authCode:
                await modalInteraction.response.send_message('Аккаунты успешно привязаны!')
                await PenguinIntegrations.create(penguin_id=p.id, discord_id=str(user.id))
                return

            await modalInteraction.response.send_message('Не верный код авторизации')

        async def sendModal(buttonInteraction):
            await buttonInteraction.response.send_modal(loginModal)

        loginModal = LoginModal(authApprove)
        view = Continue(interaction, sendModal)

        await interaction.response.send_message(
            content=f"На ваш аккаунт была отправлена открытка с кодом *(если нет - перезайдите в игру)*. \n"
                    f"Нажмите «Продолжить», что бы ввести одноразовый код", view=view)

    @slash_command(name="logout", description="Отвязать свой Discord аккаунт от своего пингвина")
    async def logout(self, interaction):
        p: Penguin = await getPenguinFromInteraction(interaction)

        async def run(newInteraction):
            await PenguinIntegrations.delete.where(PenguinIntegrations.penguin_id == p.id).gino.status()

            await newInteraction.response.send_message(content=f"Ваш аккаунт `{p.safe_name()}` успешно отвязан")
            return

        view = Question(interaction, run)

        await interaction.response.send_message(content=f"Вы уверены, что хотите отвязать аккаунт `{p.safe_name()}`?",
                                                view=view)

    @slash_command(name="guiderole", description="Получить роль экскурсовода")
    async def guideRole(self, interaction):
        p: Penguin = await getPenguinFromInteraction(interaction)
        role: disnake.Role = interaction.guild.get_role(860124814827061278)

        if interaction.guild_id != 755445822920982548:
            await interaction.response.send_message(
                content=f"Мы не нашли здесь нужную роль, перейдите на официальный сервер CPPS.app")
            return

        if 428 in p.inventory:
            if role not in interaction.user.roles:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    content=f"Вы получили роль {role.mention}! Теперь вы можете писать в канале <#860201914334576650>")
            else:
                await interaction.response.send_message(content=f"У вас уже есть роль {role.mention}")
        else:
            await interaction.response.send_message(content=f"Мы не нашли у вас шапку экскурсовода")

    @slash_command(name="pay", description="Перевести свои монеты другому игроку")
    async def pay(self, interaction,
                  receiver: str = Param(description='Получатель (его ник в игре)'),
                  amount: int = Param(description='Количество монет')):
        p: Penguin = await getPenguinFromInteraction(interaction)

        receiver.lower()
        receiverId = await Penguin.select('id').where(Penguin.username == receiver).gino.first()
        receiverId = int(receiverId[0])
        r: Penguin = await Penguin.get(receiverId)

        if amount <= 0:
            return await interaction.response.send_message(
                content='Пожалуйста введите правильное число монет')

        if p.id == r.id:
            return await interaction.response.send_message(
                content="Вы не можете передать монеты самому себе!")

        if p.coins < amount:
            return await interaction.response.send_message(
                content='У вас недостаточно монет для перевода')

        await p.update(coins=p.coins - amount).apply()
        await r.update(coins=r.coins + amount).apply()
        await Logs.create(penguin_id=int(r.id), type=4,
                          text=f"Получил от {p.username} {int(amount)} монет. Через Discord бота", room_id=0,
                          server_id=8000)
        await Logs.create(penguin_id=int(p.id), type=4,
                          text=f"Перевёл игроку {r.username} {int(amount)} монет. Через Discord бота", room_id=0,
                          server_id=8000)

        await interaction.response.send_message(
            content=f"Вы успешно передали `{amount}` монет игроку `{receiver}`!")


def setup(bot):
    bot.add_cog(UserCommands(bot))
