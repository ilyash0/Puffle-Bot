import ast
from datetime import datetime

from bs4 import BeautifulSoup
from disnake import ApplicationCommandInteraction
from loguru import logger
import disnake
from disnake.ext.commands import Cog, Param, slash_command
from requests import Session

from bot.data import db_pb
from bot.data.clubpenguin.stamp import PenguinStamp
from bot.handlers.notification import notifyCoinsReceive
from bot.misc.constants import online_url, headers, emojiCuteSad, emojiCoin, emojiGame, emojiStamp
from bot.misc.penguin import Penguin
from bot.misc.utils import getPenguinFromInter, getPenguinOrNoneFromUserId, transferCoinsAndReturnStatus, \
    getPenguinFromPenguinId


class UserCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} public users app commands")

    @slash_command(name="ilyash", description=":D")
    async def ilyash(self, inter: ApplicationCommandInteraction):
        await inter.send(f"Теперь вы пешка иляша!")

    @slash_command(name="card", description="Показывает полезную информацию о твоём аккаунте")
    async def card(self, inter: ApplicationCommandInteraction,
                   user: disnake.User = Param(default=None, description='Пользователь, чью карточку нужно показать')):
        if user:
            p = await getPenguinOrNoneFromUserId(user.id)
            if p is None:
                return await inter.send(f"Мы не нашли пингвина у указанного вами+ пользователя.", ephemeral=True)
        else:
            p: Penguin = await getPenguinFromInter(inter)

        if p.get_custom_attribute("mood") and p.get_custom_attribute("mood") != " ":
            mood = f'*{p.get_custom_attribute("mood")}*'.replace("\n", " ")
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

    @slash_command(name="pay", description="Перевести свои монеты другому игроку")
    async def pay(self, inter: ApplicationCommandInteraction,
                  receiver: str = Param(description='Получатель (его ник в игре)'),
                  amount: int = Param(description='Количество монет'),
                  message: str = Param(default=None, description='Сообщение получателю')):
        p: Penguin = await getPenguinFromInter(inter)
        receiverId = await Penguin.select('id').where(Penguin.username == receiver.lower()).gino.first()

        if receiverId is None:
            return await inter.send(f"Мы не нашли указанного пингвина", ephemeral=True)

        r: Penguin = await Penguin.get(int(receiverId[0]))
        statusDict = await transferCoinsAndReturnStatus(p, r, amount)
        if statusDict["code"] == 400:
            return await inter.send(statusDict["message"], ephemeral=True)

        await inter.send(statusDict["message"])
        await notifyCoinsReceive(p, r, amount, message)

    @slash_command(name="pay2", description="Перевести свои монеты другому пользователю")
    async def pay2(self, inter: ApplicationCommandInteraction,
                   receiver: disnake.User = Param(description='Получатель'),
                   amount: int = Param(description='Количество монет'),
                   message: str = Param(default=None, description='Сообщение получателю')):
        p: Penguin = await getPenguinFromInter(inter)
        r: Penguin = await getPenguinOrNoneFromUserId(receiver.id)
        if r is None:
            return await inter.send(f"Мы не нашли пингвина у указанного вами пользователя.", ephemeral=True)

        statusDict = await transferCoinsAndReturnStatus(p, r, amount)
        if statusDict["code"] == 400:
            return await inter.send(statusDict["message"], ephemeral=True)

        await inter.send(statusDict["message"])
        await notifyCoinsReceive(p, r, amount, message)

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

    @slash_command(name="top", description="Топ 10 игроков острова")
    async def top(self, inter: ApplicationCommandInteraction,
                  category=Param(description="Категория топа", choices=["coins", "online", "stamps"])):
        await inter.response.defer()
        if category == "coins":
            embed = disnake.Embed(title=f"{emojiCoin} Богачи острова", color=0x035BD1,
                                  description="## Пингвин — монеты\n")
            result = await Penguin.query \
                .where((Penguin.moderator == False) & (Penguin.permaban == False) & (Penguin.character == None)) \
                .order_by(Penguin.coins.desc()).limit(10).gino.all()
            for i, penguin in enumerate(result):
                embed.description += f"{i + 1}. {penguin.nickname} — {'{0:,}'.format(penguin.coins).replace(',', ' ')}\n"
            view = TopCoinsButton()

        elif category == "online":
            embed = disnake.Embed(title=f"{emojiGame} Самые активные на острове", color=0x035BD1,
                                  description="## Пингвин — минуты\n")
            result = await Penguin.query.where((Penguin.permaban == False) & (Penguin.character == None)) \
                .order_by(Penguin.minutes_played.desc()).limit(10).gino.all()
            for i, penguin in enumerate(result):
                embed.description += f"{i + 1}. {penguin.nickname} — {'{0:,}'.format(penguin.minutes_played).replace(',', ' ')}\n"
            view = TopOnlineButton()

        elif category == "stamps":
            embed = disnake.Embed(title=f"{emojiStamp} Лучшие сыщики марок", color=0x035BD1,
                                  description="## Пингвин — марки\n")
            penguins_ids_list = await PenguinStamp.select('penguin_id') \
                .group_by(PenguinStamp.penguin_id) \
                .order_by(db_pb.func.count(PenguinStamp.stamp_id).desc()) \
                .limit(10).gino.all()
            result = []
            for penguin_id in penguins_ids_list:
                p = await getPenguinFromPenguinId(int(penguin_id[0]))
                result.append({"nickname": p.nickname, "stamps": len(p.stamps) + p.count_epf_awards()})
            result.sort(key=lambda x: x["stamps"], reverse=True)
            for i, p in enumerate(result):
                embed.description += f"{i + 1}. {p['nickname']} — {p['stamps']}\n"
            view = TopStampsButton()

        else:
            embed = disnake.Embed(title=f"{emojiCuteSad} произошла ошибка", color=0x035BD1)
            view = None

        await inter.send(embed=embed, view=view)


class TopOnlineButton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Топ 50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=online")
    async def top(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class TopCoinsButton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Топ 50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=coins")
    async def top(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class TopStampsButton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Топ 50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=stamp")
    async def top(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


def setup(bot):
    bot.add_cog(UserCommands(bot))
