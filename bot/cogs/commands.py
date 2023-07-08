import ast
from datetime import datetime

from bs4 import BeautifulSoup
from disnake import ApplicationCommandInteraction
from loguru import logger
import disnake
from disnake.ext.commands import Cog, Param, slash_command
from requests import Session

from bot.data import db_pb
from bot.data.clubpenguin.moderator import Logs
from bot.misc.constants import online_url, headers, loginCommand, emojiCuteSad
from bot.misc.penguin import Penguin
from bot.data.pufflebot.users import Users, PenguinIntegrations
from bot.misc.buttons import Logout, Login
from bot.misc.select import SelectPenguins
from bot.misc.utils import getPenguinFromInter, getPenguinOrNoneFromId, transferCoinsAndReturnStatus


class UserCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loads {len(self.get_slash_commands())} public users commands")

    @slash_command(name="ilyash", description=":D")
    async def ilyash(self, inter: ApplicationCommandInteraction):
        await inter.send(f"Теперь вы пешка иляша!")

    @slash_command(name="card", description="Показывает полезную информацию о твоём аккаунте")
    async def card(self, inter: ApplicationCommandInteraction,
                   user: disnake.User = Param(default=None, description='Пользователь, чью карточку нужно показать')):
        if user:
            p = await getPenguinOrNoneFromId(user.id)
            if p is None:
                return await inter.send(f"Мы не нашли пингвина у указанного пользователя.", ephemeral=True)
        else:
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
        await inter.send(embed=embed)

    @slash_command(name="login", description="Привязать свой Discord аккаунт к пингвину")
    async def login(self, inter: ApplicationCommandInteraction):
        return await inter.send(f"Перейдите на сайт и пройдите авторизацию", view=Login())

    @slash_command(name="logout", description="Отвязать свой Discord аккаунт от своего пингвина")
    async def logout(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinFromInter(inter)
        user: Users = await Users.get(inter.user.id)
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        await inter.send(f"Вы уверены, что хотите выйти с аккаунта `{p.safe_name()}`?",
                         view=Logout(inter, p, user, penguin_ids), ephemeral=True)

    @slash_command(name="pay", description="Перевести свои монеты другому игроку")
    async def pay(self, inter: ApplicationCommandInteraction,
                  receiver: str = Param(description='Получатель (его ник в игре)'),
                  amount: int = Param(description='Количество монет')):
        p: Penguin = await getPenguinFromInter(inter)

        receiverId = await Penguin.select('id').where(Penguin.username == receiver.lower()).gino.first()
        receiverId = int(receiverId[0])
        r: Penguin = await Penguin.get(receiverId)

        await inter.send((await transferCoinsAndReturnStatus(p, r, amount)))

    @slash_command(name="switch", description="Сменить текущий аккаунт")
    async def switch(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinOrNoneFromId(inter.user.id)
        user: Users = await Users.get(inter.user.id)
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        if len(penguin_ids) == 0:
            return await inter.send(
                f"У вас не привязан ни один аккаунт. "
                f"Это можно исправить с помощью команды {loginCommand}", ephemeral=True)

        if len(penguin_ids) == 1:
            return await inter.send(
                f"У вас привязан только один аккаунт. "
                f"Вы можете привязать ещё несколько с помощью команды {loginCommand}", ephemeral=True)

        penguinsList = [{"safe_name": (await Penguin.get(penguin_id[0])).safe_name(), "id": penguin_id[0]} for
                        penguin_id in penguin_ids]
        view = disnake.ui.View()
        view.add_item(SelectPenguins(penguinsList, user))

        if p is None:
            return await inter.send(
                f"Ваш текущий аккаунт не выбран. Какой аккаунт вы хотите сделать текущим?",
                view=view, ephemeral=True)

        return await inter.send(
            f"Ваш текущий аккаунт: `{p.safe_name()}`. Какой аккаунт вы хотите сделать текущим?",
            view=view, ephemeral=True)

    @slash_command(name="online", description="Показывает количество игроков которые сейчас онлайн")
    async def online(self, inter: ApplicationCommandInteraction):
        with Session() as s:
            s.headers.update(headers)
            response = s.get(online_url)
            soup = BeautifulSoup(response.text, "html.parser")

        online = int(ast.literal_eval(soup.text)[0]['3104'])
        if online == 0:
            textMessage = f"В нашей игре сейчас никого нет {emojiCuteSad}"
        else:
            textMessage = f"В нашей игре сейчас `{online}` человек/а онлайн"
        await inter.send(textMessage)


def setup(bot):
    bot.add_cog(UserCommands(bot))
