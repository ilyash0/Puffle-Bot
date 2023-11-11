import ast
from datetime import datetime

from bs4 import BeautifulSoup
from disnake import ApplicationCommandInteraction, Localized
from loguru import logger
import disnake
from disnake.ext.commands import Cog, Param, slash_command
from requests import Session

from bot.data import db_pb
from bot.data.clubpenguin.stamp import PenguinStamp
from bot.handlers.button import TopMinutesButton, TopCoinsButton, TopStampsButton
from bot.handlers.notification import notifyCoinsReceive
from bot.misc.constants import online_url, headers, emojiCuteSad, emojiCoin, emojiGame, emojiStamp
from bot.misc.penguin import Penguin
from bot.misc.utils import getMyPenguinFromUserId, getPenguinOrNoneFromUserId, transferCoins, \
    getPenguinFromPenguinId


class UserCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} public users app commands")

    @slash_command()
    async def ilyash(self, inter: ApplicationCommandInteraction):
        """
        Best command in the world! {{ILYASH}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        await inter.send(self.bot.i18n.get("ILYASH_RESPONSE")[inter.locale.value])

    @slash_command()
    async def card(self, inter: ApplicationCommandInteraction,
                   user: disnake.User = None):
        """
        Show info about your Penguin in the game {{CARD}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        user: Optional[disnake.User]
            The Discord user {{USER}}
        """
        if user:
            p = await getPenguinOrNoneFromUserId(user.id)
            if p is None:
                return await inter.send(self.bot.i18n.get("USER_PENGUIN_NOT_FOUND")[inter.locale.value], ephemeral=True)
        else:
            p = await getMyPenguinFromUserId(inter.author.id)

        if p.get_custom_attribute("mood") and p.get_custom_attribute("mood") != " ":
            mood = f'`{p.get_custom_attribute("mood")}`'
        else:
            mood = None

        embed = disnake.Embed(title=p.safe_name(),
                              description=mood,
                              color=disnake.Color(0x035BD1))
        embed.set_thumbnail(url=f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
        embed.add_field(name="ID", value=p.id)
        embed.add_field(name=self.bot.i18n.get("SPENT_IN_GAME")[inter.locale.value],
                        value=f'{p.minutes_played} {self.bot.i18n.get("MINUTES_ABBR")[inter.locale.value]}')
        embed.add_field(name=self.bot.i18n.get("COINS")[inter.locale.value].capitalize(),
                        value=p.coins)
        embed.add_field(name=self.bot.i18n.get("STAMPS")[inter.locale.value].capitalize(),
                        value=len(p.stamps) + p.count_epf_awards())
        embed.add_field(name=self.bot.i18n.get("PENGUIN_AGE")[inter.locale.value].capitalize(),
                        value=f"{(datetime.now() - p.registration_date).days} "
                              f"{self.bot.i18n.get('DAYS')[inter.locale.value]}")
        embed.add_field(name=self.bot.i18n.get("STAFF")[inter.locale.value].capitalize(),
                        value=self.bot.i18n.get("YES")[inter.locale.value] if p.moderator else self.bot.i18n.get("NO")[
                            inter.locale.value])
        await inter.send(embed=embed)

    @slash_command()
    async def pay(self, inter: ApplicationCommandInteraction,
                  nickname: str, coins: int, message: str = None):
        """
        Transfer your coins to another player {{PAY}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        nickname: disnake.User
            Penguin's nickname in game {{PLAYER}}
        coins: int
            Number of coins {{COINS}}
        message:  Optional[str]
            Message to recipient {{MESSAGE}}
        """
        await inter.response.defer()
        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        receiverId = await Penguin.select('id').where(Penguin.username == nickname.lower()).gino.first()
        if receiverId is None:
            return await inter.send(self.bot.i18n.get("PENGUIN_NOT_FOUND")[inter.locale.value], ephemeral=True)
        r: Penguin = await Penguin.get(int(receiverId[0]))

        await transferCoins(p, r, coins)
        await notifyCoinsReceive(p, r, coins, message, inter.data.name)
        await inter.send(
            self.bot.i18n.get("COINS_TRANSFERRED")[inter.locale.value].
            replace("%coins%", str(coins)).replace("%receiver%", r.safe_name()))

    @slash_command()
    async def pay2(self, inter: ApplicationCommandInteraction,
                   user: disnake.User, coins: int, message: str = None):
        """
        Transfer your coins to another Discord user {{PAY2}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        user: disnake.User
            The Discord user {{USER}}
        coins: int
            Number of coins {{COINS}}
        message:  Optional[str]
            Message to recipient {{MESSAGE}}
        """
        await inter.response.defer()
        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        r: Penguin = await getPenguinOrNoneFromUserId(user.id)
        if r is None:
            return await inter.send(self.bot.i18n.get("USER_PENGUIN_NOT_FOUND")[inter.locale.value], ephemeral=True)

        await transferCoins(p, r, coins)
        await notifyCoinsReceive(p, r, coins, message, inter.data.name)
        await inter.send(
            self.bot.i18n.get("COINS_TRANSFERRED")[inter.locale.value].
            replace("%coins%", str(coins)).replace("%receiver%", r.safe_name()))

    @slash_command()
    async def online(self, inter: ApplicationCommandInteraction):
        """
        Shows the number of players currently online {{ONLINE}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        with Session() as s:
            s.headers.update(headers)
            response = s.get(online_url)
            soup = BeautifulSoup(response.text, "html.parser")

        online = int(ast.literal_eval(soup.text)[0]['3104'])
        if online == 0:
            textMessage = self.bot.i18n.get("NO_ONLINE_RESPONSE")[inter.locale.value].replace("%emote%", emojiCuteSad)
        else:
            textMessage = self.bot.i18n.get("ONLINE_RESPONSE")[inter.locale.value].replace("%online%", str(online))
        await inter.send(textMessage)

    @slash_command()
    async def top(self, inter: ApplicationCommandInteraction,
                  category: str = Param(choices=[Localized("coins", key="COINS"), Localized("minutes", key="MINUTES"),
                                                 Localized("stamps", key="STAMPS")])):
        """
        Displays the top 10 players on the island {{TOP}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        category: str
            Top category {{TOP_CATEGORY}}
        """
        await inter.response.defer()
        if category == "coins":
            embed = disnake.Embed(title=f"{emojiCoin} {self.bot.i18n.get('RICH_ISLANDERS')[inter.locale.value]}",
                                  color=0x035BD1,
                                  description=f"## {self.bot.i18n.get('PENGUIN')[inter.locale.value].capitalize()} — {self.bot.i18n.get('COINS')[inter.locale.value]}\n")
            result = await Penguin.query \
                .where((Penguin.moderator == False) & (Penguin.permaban == False) & (Penguin.character == None)) \
                .order_by(Penguin.coins.desc()).limit(10).gino.all()
            for i, penguin in enumerate(result):
                embed.description += f"{i + 1}. {penguin.nickname} — {f'{penguin.coins:,}'.replace(',', ' ')}\n"
            view = TopCoinsButton(inter)

        elif category == "minutes":
            embed = disnake.Embed(title=f"{emojiGame} {self.bot.i18n.get('MOST_ACTIVE')[inter.locale.value]}",
                                  color=0x035BD1,
                                  description=f"## {self.bot.i18n.get('PENGUIN')[inter.locale.value].capitalize()} — {self.bot.i18n.get('MINUTES')[inter.locale.value]}\n")
            result = await Penguin.query.where((Penguin.permaban == False) & (Penguin.character == None)) \
                .order_by(Penguin.minutes_played.desc()).limit(10).gino.all()
            for i, penguin in enumerate(result):
                embed.description += f"{i + 1}. {penguin.nickname} — {f'{penguin.minutes_played:,}'.replace(',', ' ')}\n"
            view = TopMinutesButton(inter)

        elif category == "stamps":
            embed = disnake.Embed(title=f"{emojiStamp} {self.bot.i18n.get('STAMP_DETECTIVES')[inter.locale.value]}s",
                                  color=0x035BD1,
                                  description=f"## {self.bot.i18n.get('PENGUIN')[inter.locale.value].capitalize()} — {self.bot.i18n.get('STAMPS')[inter.locale.value]}\n")
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
            view = TopStampsButton(inter)

        else:
            embed = disnake.Embed(title=f"{emojiCuteSad} error occurred", color=0x035BD1)
            view = None

        await inter.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(UserCommands(bot))
