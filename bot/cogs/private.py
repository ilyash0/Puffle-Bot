from datetime import timedelta, datetime
from statistics import mean

import disnake
from disnake import ApplicationCommandInteraction, AllowedMentions, Webhook
from disnake.ext.commands import Cog, slash_command, Param
from loguru import logger

from bot.data.clubpenguin.penguin import Login
from bot.handlers.buttons import Rules
from bot.misc.constants import (
    embedRuleImageRu,
    embedRuleRu,
    embedAboutImage,
    embedAbout,
    guild_ids,
    avatarImageBytearray)
from bot.handlers.select import About


class PrivateCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} private app commands")

    @slash_command(name="transfer", description="Transfer images from the current channel to the forum",
                   guild_ids=guild_ids)
    async def transfer(self, inter: ApplicationCommandInteraction, channel_id: str):
        await inter.response.defer()
        source_channel = inter.channel
        destination_channel = disnake.utils.get(inter.guild.channels, id=int(channel_id))

        async for message in source_channel.history(limit=None):
            if message.attachments:
                content = f", комментарий: {message.content}" if message.content else ''
                await destination_channel.create_thread(name=f"{message.author.display_name}",
                                                        content=f'Автор: {message.author.mention}{content}',
                                                        files=[await attachment.to_file() for attachment in
                                                               message.attachments],
                                                        allowed_mentions=AllowedMentions(users=False)
                                                        )
        await inter.edit_original_response(f"Успешно перенесено в <#{channel_id}>!")

    @slash_command(name="rules", description="Send rules embed", guild_ids=guild_ids)
    async def rules(self, inter: ApplicationCommandInteraction):
        webhook: Webhook = await inter.channel.create_webhook(name="CPPS.APP", avatar=avatarImageBytearray)
        message = await webhook.send(embeds=[embedRuleImageRu, embedRuleRu], wait=True)
        await message.edit(view=Rules(message))
        await inter.send("Success", ephemeral=True)

    @slash_command(name="about", description="Send about embed", guild_ids=guild_ids)
    async def about(self, inter: ApplicationCommandInteraction):
        view = disnake.ui.View(timeout=None)
        view.add_item(About())
        webhook = await inter.channel.create_webhook(name="CPPS.APP", avatar=avatarImageBytearray)
        await webhook.send(embeds=[embedAboutImage, embedAbout], view=view)
        await inter.send("Success", ephemeral=True)

    @slash_command(name="statistics", description="Показывает статистику онлайна", guild_ids=guild_ids)
    async def online(self, inter: ApplicationCommandInteraction,
                     start_date: str = Param(description='Дата отсчёта, формата ДД.ММ.ГГГГ'),
                     end_date: str = Param(default=None, description='Дата окончания, формата ДД.ММ.ГГГГ')):
        await inter.response.defer()
        try:
            start_date_obj = datetime.strptime(start_date, "%d.%m.%Y").date()
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%d.%m.%Y").date()
                title = f"# с {start_date_obj.strftime('%d.%m.%Y')} по {end_date_obj.strftime('%d.%m.%Y')} \n"
            else:
                end_date_obj = start_date_obj + timedelta(days=1)
                title = f"# {start_date_obj.strftime('%d.%m.%Y')} \n"
        except ValueError:
            return await inter.send(f"Дата `{start_date}` невалидна. Ожидается формат `ДД.ММ.ГГГГ`.")

        logins_list = await Login.query.where((Login.date >= start_date_obj) & (Login.date <= end_date_obj)).gino.all()
        online_list = {}
        for login in logins_list:
            if login.minutes_played == 0: continue

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
            minutes=float(next(key for key, value in online_list.items() if value == max_online))) + datetime(1970, 1, 1)

        await inter.send(
            f"{title}*Максимальный онлайн:* {max_online} ({max_online_date.strftime('%d.%m.%Y %H:%M')})"
            f" \n*Средний онлайн:* {round(mean(online_list.values()), 3)}")



def setup(bot):
    bot.add_cog(PrivateCommands(bot))
