from datetime import timedelta, datetime
from statistics import mean

import disnake
from disnake import AppCommandInter, Embed, Localized
from disnake.ext.commands import Cog, slash_command, Param
from loguru import logger

from bot.data.clubpenguin.penguin import Login, Penguin
from bot.data.clubpenguin.transactions import Transactions
from bot.misc.constants import (
    embedAboutImage,
    embedAbout,
    guild_ids,
    avatarImageBytearray, placeholderImageLink)
from bot.handlers.select import AboutSelect


class PrivateCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} private app commands")

    @slash_command(guild_ids=guild_ids)
    async def about(self, inter: AppCommandInter):
        """
        Send about embed {{ABOUT}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        view = disnake.ui.View(timeout=None)
        view.add_item(AboutSelect())
        webhook = await inter.channel.create_webhook(name="CPPS.APP", avatar=avatarImageBytearray)
        await webhook.send(embeds=[embedAboutImage, embedAbout], view=view)
        await inter.send("Success", ephemeral=True)

    @slash_command(guild_ids=guild_ids)
    async def statistics(self, inter: AppCommandInter,
                         start_date_str: str, end_date_str: str = None,
                         detail: str = Param(default="No",
                                             choices=[Localized("Yes", key="YES"), Localized("No", key="NO")])):
        """
        Shows game statistics {{STATISTIC}}

        Parameters
        ----------
        inter: AppCommandInter
        start_date_str: str
            Start date, format DD/MM/YYYY {{START_DATE}}
        end_date_str:  Optional[str]
            End date, format DD/MM/YYYY {{END_DATE}}
        detail:  Optional[str]
            Show additional information {{DETAIL}}
        """
        lang = str(inter.avail_lang)
        date_format: str = self.bot.i18n.get('DATE_FORMAT')[lang]
        await inter.response.defer()

        try:
            start_datetime = datetime.strptime(start_date_str, date_format)
            if end_date_str:
                end_datetime = datetime.strptime(end_date_str, date_format)
                title = (self.bot.i18n.get('STATISTIC_TITLE')[lang]
                         .replace("%start%", f"<t:{int(start_datetime.timestamp())}:d>")
                         .replace("%end%", f"<t:{int(end_datetime.timestamp())}:d>"))
            else:
                end_datetime = start_datetime + timedelta(days=1)
                title = f"<t:{int(start_datetime.timestamp())}:d>\n"
        except ValueError:
            return await inter.send(self.bot.i18n.get('INVALID_DATE')[lang].replace("%date%", start_date_str))

        if start_datetime < datetime(2020, 9, 28):
            return await inter.send(self.bot.i18n.get('TOO_EARLY_DATE')[lang])

        embed = Embed(color=0x2B2D31, title=title)
        embed.set_footer(text=self.bot.i18n.get('STATISTIC_FOOTER')[lang])
        # embed.set_thumbnail("https://static10.tgstat.ru/channels/_0/49/49155b0c3f227c470ffa63db3f8923a2.jpg")
        embed.description = f"## {self.bot.i18n.get('PLAYERS_ACTIVITY')[lang]}\n"
        embed.set_image(url=placeholderImageLink)

        logins_list = await Login.query.where((Login.date >= start_datetime) & (Login.date <= end_datetime)).gino.all()
        online_list = {}
        active_players = set()
        total_time_played = 0
        for login in logins_list:
            if login.minutes_played == 0:
                continue

            active_players.add(login.penguin_id)
            total_time_played += login.minutes_played
            time_int = (login.date.replace(second=0, microsecond=0) - datetime(1970, 1, 1)).total_seconds() / 60
            for i in range(login.minutes_played):
                try:
                    if not online_list.get(str(time_int + i)):
                        online_list[str(time_int + i)] = 1
                    else:
                        online_list[str(time_int + i)] += 1
                except KeyError:
                    pass

        max_online = max(online_list.values())
        max_online_date = timedelta(
            minutes=float(next(key for key, value in online_list.items() if value == max_online))) + datetime(1970, 1,
                                                                                                              1)

        embed.description += f"""{self.bot.i18n.get('MAX_ONLINE')[lang]}: **{max_online}** (<t:{int(max_online_date.timestamp())}:f>)
        {self.bot.i18n.get('AVERAGE_ONLINE')[lang]}: **{round(mean(online_list.values()), 3)}**
        {self.bot.i18n.get('AVERAGE_PLAYER_TIME')[lang]}: **{round(total_time_played / max(len(active_players), 1), 3)}** {self.bot.i18n.get('MINUTES_ABBR')[lang]}"""

        if detail == "Yes":
            new_accounts = await Penguin.query.where(
                (Penguin.registration_date >= start_datetime) & (Penguin.registration_date <= end_datetime)).gino.all()
            returning_players = set()
            for p in new_accounts:
                if p.minutes_played > 30:
                    returning_players.add(p.id)
            # for p in new_accounts:
            #     count = sum(1 for login in logins_list if login.penguin_id == p.id)
            #     if count > 2:
            #         returning_players.add(p.id)

            all_accounts = len(await Penguin.query.gino.all())
            transactions_list = await Transactions.query.where(
                (Transactions.time >= start_datetime) & (Transactions.time <= end_datetime)).gino.all()
            all_rub = 0
            paying_accounts = set()
            for transaction in transactions_list:
                all_rub += transaction.rub
                paying_accounts.add(transaction.penguin_id)

            embed.description += f"""
            {self.bot.i18n.get('NEW_REGISTERED')[lang]}: **{f'{len(new_accounts):,}'.replace(',', ' ')}**
            {self.bot.i18n.get('PLAYER_RETENTION')[lang]}: **{round((len(returning_players) / len(new_accounts) * 100), 1)}**%
            
            ## {self.bot.i18n.get('ECONOMIC_DATA')[lang]}
            {self.bot.i18n.get('MICROTRANSACTION_REVENUE')[lang]}: **||{f'{max(all_rub, 0):,}'.replace(',', ' ')}||** ₽
            ARPU: **||{round(all_rub / all_accounts, 3) if all_rub > 0 else 0}||** ₽
            ARPPU: **||{round(all_rub / len(paying_accounts), 3) if all_rub > 0 else 0}||** ₽"""

        await inter.send(embeds=[embed])


def setup(bot):
    bot.add_cog(PrivateCommands(bot))
