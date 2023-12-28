import ast
from datetime import datetime

from asyncio import sleep
from random import randrange

from bs4 import BeautifulSoup
from disnake import AppCommandInter, Localized
from loguru import logger
import disnake
from disnake.ext.commands import Cog, Param, slash_command, CommandError
from requests import Session

from bot.data import db_pb
from bot.data.clubpenguin.stamp import PenguinStamp
from bot.handlers.button import TopMinutesButton, TopCoinsButton, TopStampsButton, Gift
from bot.handlers.censure import is_message_valid
from bot.handlers.notification import notify_coins_receive
from bot.misc.constants import online_url, headers, emojiCuteSad, emojiCoin, emojiGame, emojiStamp
from bot.misc.penguin import Penguin
from bot.misc.utils import transfer_coins, get_penguin_from_penguin_id


class UserCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} public users app commands")

    @slash_command()
    async def ilyash(self, inter: AppCommandInter):
        """
        Best command in the world! {{ILYASH}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        await inter.send(self.bot.i18n.get("ILYASH_RESPONSE")[str(inter.avail_lang)])

    @slash_command()
    async def card(self, inter: AppCommandInter,
                   user: disnake.User = None):
        """
        Show info about your Penguin in the game {{CARD}}

        Parameters
        ----------
        inter: AppCommandInter
        user: Optional[disnake.User]
            The Discord user {{USER}}
        """
        # TODO: replace the embed with a picture.
        lang: str = str(inter.avail_lang)
        if user:
            p = await user.penguin
            if p is None:
                await inter.send(self.bot.i18n.get("USER_PENGUIN_NOT_FOUND")[lang], ephemeral=True)
                return
        else:
            p = await inter.user.penguin

        if p.get_custom_attribute("mood") and not p.get_custom_attribute("mood").isspace():
            mood = f'_' + p.get_custom_attribute("mood").replace("#", "\#").replace("*", "\*").replace("_", "\_") + '_'
        else:
            mood = None

        embed = disnake.Embed(title=p.safe_name(),
                              description=mood,
                              color=disnake.Color(0x035BD1))
        embed.set_thumbnail(url=f"https://play.cpps.app/avatar/{p.id}/cp?size=600")
        embed.add_field(name="ID", value=p.id)
        embed.add_field(name=self.bot.i18n.get("SPENT_IN_GAME")[lang],
                        value=f'{p.minutes_played} {self.bot.i18n.get("MINUTES_ABBR")[lang]}')
        embed.add_field(name=self.bot.i18n.get("COINS")[lang].capitalize(),
                        value=p.coins)
        embed.add_field(name=self.bot.i18n.get("STAMPS")[lang].capitalize(),
                        value=len(p.stamps) + p.count_epf_awards())
        embed.add_field(name=self.bot.i18n.get("PENGUIN_AGE")[lang].capitalize(),
                        value=f"{(datetime.now() - p.registration_date).days} {self.bot.i18n.get('DAYS')[lang]}")
        embed.add_field(name=self.bot.i18n.get("STAFF")[lang].capitalize(),
                        value=self.bot.i18n.get("YES")[lang] if p.moderator else self.bot.i18n.get("NO")[lang])
        await inter.send(embed=embed)

    @slash_command()
    async def pay(self, inter: AppCommandInter,
                  nickname: str, coins: int, message: str = None):
        """
        Transfer your coins to another player {{PAY}}

        Parameters
        ----------
        inter: AppCommandInter
        nickname: disnake.User
            Penguin's nickname in game {{PLAYER}}
        coins: int
            Number of coins {{COINS}}
        message:  Optional[str]
            Message to recipient {{MESSAGE}}
        """
        await inter.response.defer()
        p: Penguin = await inter.user.penguin
        receiver_id, = await Penguin.select('id').where(Penguin.username == nickname.lower()).gino.first()
        if receiver_id is None:
            return await inter.send(self.bot.i18n.get("PENGUIN_NOT_FOUND")[str(inter.avail_lang)], ephemeral=True)
        r: Penguin = await Penguin.get(int(receiver_id))

        await transfer_coins(p, r, coins)
        await notify_coins_receive(p, r, coins, message, inter.data.name)
        await inter.send(
            self.bot.i18n.get("COINS_TRANSFERRED")[str(inter.avail_lang)].
            replace("%coins%", str(coins)).replace("%receiver%", r.safe_name()))

    @slash_command()
    async def pay2(self, inter: AppCommandInter,
                   user: disnake.User, coins: int, message: str = None):
        """
        Transfer your coins to another Discord user {{PAY2}}

        Parameters
        ----------
        inter: AppCommandInter
        user: disnake.User
            The Discord user {{USER}}
        coins: int
            Number of coins {{COINS}}
        message:  Optional[str]
            Message to recipient {{MESSAGE}}
        """
        await inter.response.defer()
        p: Penguin = await inter.user.penguin
        r: Penguin = await user.penguin
        if r is None:
            return await inter.send(self.bot.i18n.get("USER_PENGUIN_NOT_FOUND")[str(inter.avail_lang)], ephemeral=True)

        await transfer_coins(p, r, coins)
        await notify_coins_receive(p, r, coins, message, inter.data.name)
        await inter.send(
            self.bot.i18n.get("COINS_TRANSFERRED")[str(inter.avail_lang)].
            replace("%coins%", str(coins)).replace("%receiver%", r.safe_name()))

    @slash_command()
    async def online(self, inter: AppCommandInter):
        """
        Shows the number of players currently online {{ONLINE}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        # await inter.response.defer()
        lang = str(inter.avail_lang)
        with Session() as s:
            s.headers.update(headers)
            response = s.get(online_url)
            soup = BeautifulSoup(response.text, "html.parser")

        online = int(ast.literal_eval(soup.text)[0]['3104'])
        if online == 0:
            text_message = self.bot.i18n.get("NO_ONLINE_RESPONSE")[lang].replace("%emote%", emojiCuteSad)
        else:
            text_message = self.bot.i18n.get("ONLINE_RESPONSE")[lang].replace("%online%", str(online))
        await inter.send(text_message)

    @slash_command()
    async def top(self, inter: AppCommandInter,
                  category: str = Param(choices=[Localized("coins", key="COINS"), Localized("minutes", key="MINUTES"),
                                                 Localized("stamps", key="STAMPS")])):
        """
        Displays the top 10 players on the island {{TOP}}

        Parameters
        ----------
        inter: AppCommandInter
        category: str
            Top category {{TOP_CATEGORY}}
        """
        lang = str(inter.avail_lang)
        await inter.response.defer()
        description = f"## {self.bot.i18n.get('PENGUIN')[lang].capitalize()} — "
        if category == "coins":
            description += f"{self.bot.i18n.get('COINS')[lang]}\n"
            embed = disnake.Embed(title=f"{emojiCoin} {self.bot.i18n.get('RICH_ISLANDERS')[lang]}",
                                  color=0x035BD1,
                                  description=description)
            result = await Penguin.query \
                .where((Penguin.moderator == False) & (Penguin.permaban == False) & (Penguin.character == None)) \
                .order_by(Penguin.coins.desc()).limit(10).gino.all()
            for i, p in enumerate(result):
                embed.description += f"{i + 1}. {p.nickname} — {f'{p.coins:,}'.replace(',', ' ')}\n"
            view = TopCoinsButton(inter)

        elif category == "minutes":
            description += f"{self.bot.i18n.get('MINUTES')[lang]}\n"
            embed = disnake.Embed(title=f"{emojiGame} {self.bot.i18n.get('MOST_ACTIVE')[lang]}",
                                  color=0x035BD1,
                                  description=description)
            result = await Penguin.query.where((Penguin.permaban == False) & (Penguin.character == None)) \
                .order_by(Penguin.minutes_played.desc()).limit(10).gino.all()
            for i, p in enumerate(result):
                embed.description += f"{i + 1}. {p.nickname} — {f'{p.minutes_played:,}'.replace(',', ' ')}\n"
            view = TopMinutesButton(inter)

        elif category == "stamps":
            description += f"{self.bot.i18n.get('STAMPS')[lang]}\n"
            embed = disnake.Embed(title=f"{emojiStamp} {self.bot.i18n.get('STAMP_DETECTIVES')[lang]}s",
                                  color=0x035BD1,
                                  description=description)
            penguins_ids_list = await PenguinStamp.select('penguin_id') \
                .group_by(PenguinStamp.penguin_id) \
                .order_by(db_pb.func.count(PenguinStamp.stamp_id).desc()) \
                .limit(10).gino.all()
            result = []
            for penguin_id in penguins_ids_list:
                p = await get_penguin_from_penguin_id(int(penguin_id[0]))
                result.append({"nickname": p.nickname, "stamps": len(p.stamps) + p.count_epf_awards()})
            result.sort(key=lambda x: x["stamps"], reverse=True)
            for i, p in enumerate(result):
                embed.description += f"{i + 1}. {p['nickname']} — {p['stamps']}\n"
            view = TopStampsButton(inter)

        else:
            embed = disnake.Embed(title=f"{emojiCuteSad} error occurred", color=0x035BD1)
            view = None

        await inter.send(embed=embed, view=view)

    @slash_command()
    async def gift(self, inter: AppCommandInter, channel: disnake.TextChannel, coins: int, message: str = None):
        """
        Gift coins to users in a specific channel {{GIFT}}

        Parameters
        ----------
        inter: AppCommandInter
        channel: disnake.TextChannel
            Target text channel on the current server {{CHANNEL}}
        coins: int
            Number of coins {{COINS}}
        message: Optional[str]
            A message to send with the gift {{GIFT_MESSAGE}}
        """
        lang = str(inter.avail_lang)
        p = await inter.user.penguin
        if message is None:
            message = self.bot.i18n.get("GIFT_DEFAULT_RESPONSE")[lang]
        elif not is_message_valid(message):
            return await inter.send(self.bot.i18n.get("KEEP_RULES")[lang], ephemeral=True)

        if coins <= 0:
            raise CommandError("INCORRECT_COINS_AMOUNT")

        if p.coins < coins:
            raise CommandError("NOT_ENOUGH_COINS")

        message_object = await channel.send(f"{message} {self.bot.i18n.get('WAIT_A_FEW_SECONDS')[lang]}")
        await inter.send(self.bot.i18n.get("SUCCESS")[lang], ephemeral=True)
        await sleep(randrange(3, 15))
        await message_object.edit(message, view=Gift(inter, message_object, coins, p))


def setup(bot):
    bot.add_cog(UserCommands(bot))
