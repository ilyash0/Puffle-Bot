from datetime import datetime
from random import sample

from disnake import ApplicationCommandInteraction
from loguru import logger
import disnake
from disnake.ext.commands import Cog, Param, slash_command

from bot.data import db
from bot.data.moderator import Logs
from bot.misc.penguin import Penguin
from bot.data.penguin import PenguinIntegrations
from bot.misc.buttons import Logout, Continue
from bot.misc.modals import LoginModal
from bot.misc.select import SelectPenguins
from bot.misc.utils import getPenguinFromInter, getPenguinOrNoneFromInter


class UserCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info("Users commands ready")

    @slash_command(name="ilyash", description=":D")
    async def ilyash(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(content=f"Теперь вы пешка иляша!")

    @slash_command(name="card", description="Показывает полезную информацию о твоём аккаунте")
    async def card(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinFromInter(inter)
        if p.get_custom_attribute("mood") and p.get_custom_attribute("mood") != " ":
            mood = f'*{p.get_custom_attribute("mood")}*'
        else:
            mood = None

        embed = disnake.Embed(title=p.safe_name(),
                              description=mood,
                              color=disnake.Color(0x035BD1))
        embed.set_thumbnail(url=f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
        embed.add_field(name="ID", value=p.id)
        embed.add_field(name="Проведено в игре", value=f'{p.minutes_played} минут')
        embed.add_field(name="Монеты", value=p.coins)
        embed.add_field(name="Марки", value=len(p.stamps) + p.count_epf_awards())
        embed.add_field(name="Возраст пингвина", value=f"{(datetime.now() - p.registration_date).days} дней")
        embed.add_field(name="Сотрудник", value="Да" if p.moderator else "Нет")
        await inter.response.send_message(embed=embed)

    @slash_command(name="login", description="Привязать свой Discord аккаунт к пингвину")
    async def login(self, inter: ApplicationCommandInteraction,
                    penguin: str = Param(description='Имя вашего пингвина')):
        user = inter.user
        penguinId = await Penguin.select('id').where(Penguin.username == penguin.lower()).gino.first()
        penguinId = int(penguinId[0])
        p: Penguin = await Penguin.get(penguinId)

        symbols = "QWERTYUIOPASDFGHJKLZXCVBNM0123456789"
        authCode = "".join(sample(symbols, 8))

        await p.add_inbox(302, details=authCode)

        async def authApprove(modalInter, authCodeInput):
            await view.disableAllItems()
            if authCodeInput.upper() == authCode:
                currentPenguin: Penguin = await getPenguinOrNoneFromInter(inter)
                if currentPenguin is not None:
                    await modalInter.response.send_message(
                        f'Аккаунты успешно привязаны! Ваш текущий аккаунт `{currentPenguin.safe_name()}`')
                    await p.set_integration(str(user.id))
                    return

                await modalInter.response.send_message('Аккаунты успешно привязаны!')
                await p.set_integration(str(user.id), True)
                return

            await modalInter.response.send_message('Не верный код авторизации')

        async def sendModal(buttonInter):
            await buttonInter.response.send_modal(loginModal)

        loginModal = LoginModal(authApprove)
        view = Continue(inter, sendModal)

        await inter.response.send_message(
            content=f"На ваш аккаунт была отправлена открытка с кодом *(если нет - перезайдите в игру)*. \n"
                    f"*Код действителен в течении 15 минут*. \n"
                    f"Нажмите «Продолжить», что бы ввести одноразовый код", view=view)

    @slash_command(name="logout", description="Отвязать свой Discord аккаунт от своего пингвина")
    async def logout(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinFromInter(inter)

        async def run(buttonInter):
            await p.delete_integration(str(inter.user.id))

            penguin_ids = await db.select([PenguinIntegrations.penguin_id]).where(
                (PenguinIntegrations.discord_id == str(inter.user.id))).gino.all()

            if len(penguin_ids) == 1:
                newCurrentPenguin: Penguin = await Penguin.get(penguin_ids[0][0])
                await newCurrentPenguin.set_integration_current_status(inter.user.id, True)
                await buttonInter.response.send_message(
                    content=f"Ваш аккаунт `{p.safe_name()}` успешно отвязан. "
                            f"Теперь ваш текущий аккаунт `{newCurrentPenguin.safe_name()}`")
                return

            if len(penguin_ids) == 0:
                await buttonInter.response.send_message(
                    content=f"Ваш аккаунт `{p.safe_name()}` успешно отвязан.")
                return

            await buttonInter.response.send_message(
                content=f"Ваш аккаунт `{p.safe_name()}` успешно отвязан. "
                        f"Чтобы выбрать текущий аккаунт воспользуйтесь командой `/switch`")
            return

        view = Logout(inter, run)

        await inter.response.send_message(content=f"Вы уверены, что хотите выйти с аккаунта `{p.safe_name()}`?",
                                          view=view)

    @slash_command(name="guiderole", description="Получить роль экскурсовода")
    async def guideRole(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinFromInter(inter)
        role: disnake.Role = inter.guild.get_role(860124814827061278)

        if inter.guild_id != 755445822920982548:
            await inter.response.send_message(
                content=f"Мы не нашли здесь нужную роль, перейдите на официальный сервер CPPS.app")
            return

        if 428 in p.inventory:
            if role not in inter.user.roles:
                await inter.user.add_roles(role)
                await inter.response.send_message(
                    content=f"Вы получили роль {role.mention}! Теперь вы можете писать в канале <#860201914334576650>")
            else:
                await inter.response.send_message(content=f"У вас уже есть роль {role.mention}")
        else:
            await inter.response.send_message(content=f"Мы не нашли у вас шапку экскурсовода")

    @slash_command(name="pay", description="Перевести свои монеты другому игроку")
    async def pay(self, inter: ApplicationCommandInteraction,
                  receiver: str = Param(description='Получатель (его ник в игре)'),
                  amount: int = Param(description='Количество монет')):
        p: Penguin = await getPenguinFromInter(inter)

        receiverId = await Penguin.select('id').where(Penguin.username == receiver.lower()).gino.first()
        receiverId = int(receiverId[0])
        r: Penguin = await Penguin.get(receiverId)

        if amount <= 0:
            return await inter.response.send_message(
                content='Пожалуйста введите правильное число монет')

        if p.id == r.id:
            return await inter.response.send_message(
                content="Вы не можете передать монеты самому себе!")

        if p.coins < amount:
            return await inter.response.send_message(
                content='У вас недостаточно монет для перевода')

        await p.update(coins=p.coins - amount).apply()
        await r.update(coins=r.coins + amount).apply()
        await Logs.create(penguin_id=int(r.id), type=4,
                          text=f"Получил от {p.username} {int(amount)} монет. Через Discord бота", room_id=0,
                          server_id=8000)
        await Logs.create(penguin_id=int(p.id), type=4,
                          text=f"Перевёл игроку {r.username} {int(amount)} монет. Через Discord бота", room_id=0,
                          server_id=8000)

        await inter.response.send_message(
            content=f"Вы успешно передали `{amount}` монет игроку `{receiver}`!")

    @slash_command(name="switch", description="Сменить текущий аккаунт")
    async def switch(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinOrNoneFromInter(inter)

        penguin_ids = await db.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == str(inter.user.id))).gino.all()

        if len(penguin_ids) == 0:
            await inter.response.send_message(
                content=f"У вас не привязан ни один аккаунт. "
                        f"Это можно исправить с помощью команды `/login`")
            return

        if len(penguin_ids) == 1:
            await inter.response.send_message(
                content=f"У вас привязан только один аккаунт. "
                        f"Вы можете привязать ещё несколько с помощью команды `/login`")
            return

        async def run(selectInter, penguin_id):
            newCurrentPenguin: Penguin = await Penguin.get(penguin_id)

            try:
                await p.set_integration_current_status(inter.user.id, False)
            except AttributeError:
                pass
            await newCurrentPenguin.set_integration_current_status(inter.user.id, True)

            await selectInter.response.send_message(
                content=f"Успешно. Теперь ваш текущий аккаунт `{newCurrentPenguin.safe_name()}`")
            return

        view = disnake.ui.View()
        penguinsList = [{"safe_name": (await Penguin().get(penguin_id[0])).safe_name(), "id": penguin_id[0]} for
                        penguin_id in penguin_ids]
        view.add_item(SelectPenguins(penguinsList, run, inter.user.id))

        if p is None:
            await inter.response.send_message(
                content=f"Ваш текущий аккаунт не выбран. Какой аккаунт вы хотите сделать текущим?",
                view=view)
            return

        await inter.response.send_message(
            content=f"Ваш текущий аккаунт: `{p.safe_name()}`. Какой аккаунт вы хотите сделать текущим?",
            view=view)
        return


def setup(bot):
    bot.add_cog(UserCommands(bot))
