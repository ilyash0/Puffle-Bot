from datetime import timedelta, datetime
from statistics import mean

import disnake
from disnake import AppCommandInter, AllowedMentions, Webhook, Embed, Localized
from disnake.ext.commands import Cog, slash_command, Param
from loguru import logger

from bot.data.clubpenguin.penguin import Login, Penguin
from bot.data.clubpenguin.transactions import Transactions
from bot.handlers.button import Rules
from bot.misc.constants import (
    embedRuleImageRu,
    embedRuleRu,
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
    async def transfer(self, inter: AppCommandInter, forum_id: str):
        """
        Transfer images from the current channel to the forum {{TRANSFER}}

        Parameters
        ----------
        inter: AppCommandInter
        forum_id: str
            ID of the target forum chanel {{FORUM_ID}}

        """
        await inter.response.defer()
        source_channel = inter.channel
        destination_channel = disnake.utils.get(inter.guild.channels, id=int(forum_id))

        async for message in source_channel.history(limit=None):
            if message.attachments:
                content = f", comment: {message.content}" if message.content else ''
                await destination_channel.create_thread(name=f"{message.author.display_name}",
                                                        content=f'Author: {message.author.mention}{content}',
                                                        files=[await attachment.to_file() for attachment in
                                                               message.attachments],
                                                        allowed_mentions=AllowedMentions(users=False)
                                                        )
        await inter.edit_original_response(f"Success transferred in <#{forum_id}>!")

    @slash_command(guild_ids=guild_ids)
    async def rules(self, inter: AppCommandInter):
        """
        Send rules embed {{RULES}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        webhook: Webhook = await inter.channel.create_webhook(name="CPPS.APP", avatar=avatarImageBytearray)
        message = await webhook.send(embeds=[embedRuleImageRu, embedRuleRu], wait=True)
        await message.edit(view=Rules(message))
        await inter.send("Success", ephemeral=True)

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
                         start_date: str, end_date: str = None,
                         detail: str = Param(default="No",
                                             choices=[Localized("Yes", key="YES"), Localized("No", key="NO")])):
        """
        Shows game statistics {{STATISTIC}}

        Parameters
        ----------
        inter: AppCommandInter
        start_date: str
            Start date, format DD.MM.YYYY {{START_DATE}}
        end_date:  Optional[str]
            End date, format DD.MM.YYYY {{END_DATE}}
        detail:  Optional[str]
            Show additional information {{DETAIL}}
        """
        await inter.response.defer()
        try:
            start_date_obj = datetime.strptime(start_date, "%d.%m.%Y").date()
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%d.%m.%Y").date()
                title = f"с {start_date_obj.strftime('%d.%m.%Y')} по {end_date_obj.strftime('%d.%m.%Y')}"
            else:
                end_date_obj = start_date_obj + timedelta(days=1)
                title = f"{start_date_obj.strftime('%d.%m.%Y')} \n"
        except ValueError:
            return await inter.send(f"Дата `{start_date}` невалидна. Ожидается формат `ДД.ММ.ГГГГ`.")

        if start_date_obj < datetime(2020, 9, 28).date():
            return await inter.send(
                f"За указанный период данные отсутствуют. Самая ранняя доступная дата — `28.09.2020`")

        embed = Embed(color=0x2B2D31, title=title)
        embed.set_footer(text="Если день ещё не закончился, то данные могут быть не верные")
        # embed.set_thumbnail("https://static10.tgstat.ru/channels/_0/49/49155b0c3f227c470ffa63db3f8923a2.jpg")
        embed.description = "## Активность игроков\n"
        embed.set_image(url=placeholderImageLink)

        logins_list = await Login.query.where((Login.date >= start_date_obj) & (Login.date <= end_date_obj)).gino.all()
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

        embed.description += f"""Максимальный онлайн: **{max_online}** ({max_online_date.strftime('%d.%m.%Y %H:%M')})
        Средний онлайн: **{round(mean(online_list.values()), 3)}**
        Среднее время на игрока: **{round(total_time_played / max(len(active_players), 1), 3)}** минут"""

        if detail == "Yes":
            new_accounts = await Penguin.query.where(
                (Penguin.registration_date >= start_date_obj) & (Penguin.registration_date <= end_date_obj)).gino.all()
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
                (Transactions.time >= start_date_obj) & (Transactions.time <= end_date_obj)).gino.all()
            all_rub = 0
            paying_accounts = set()
            for transaction in transactions_list:
                all_rub += transaction.rub
                paying_accounts.add(transaction.penguin_id)

            embed.description += f"""
            Зарегистрировано новых аккаунтов: **{f'{len(new_accounts):,}'.replace(',', ' ')}**
            Удержание пользователей: **{round((len(returning_players) / len(new_accounts) * 100), 1)}**%\n"""
            embed.description += f"""## Экономические данные
            Общая выручка от микротранзакций: **||{f'{max(all_rub, 0):,}'.replace(',', ' ')}||** ₽
            ARPU: **||{round(all_rub / all_accounts, 3) if all_rub > 0 else 0}||** ₽
            ARPPU: **||{round(all_rub / len(paying_accounts), 3) if all_rub > 0 else 0}||** ₽\n"""

        await inter.send(embeds=[embed])


def setup(bot):
    bot.add_cog(PrivateCommands(bot))
