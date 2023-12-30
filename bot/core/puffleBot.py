import os
import traceback
from datetime import datetime, timedelta

import disnake
from disnake import Webhook, Game, AppCommandInter
from disnake.ext.commands import InteractionBot, CommandError, CommandOnCooldown
from loguru import logger
import bot.locale
import bot.handlers.cogs
from bot.core.disnaleOverride import NewUser, NewMember, NewAppInter
from bot.data.pufflebot.fundraising import Fundraising, FundraisingBackers
from bot.data.pufflebot.user import User
from bot.handlers.button import Rules, FundraisingButtons
from bot.misc.constants import rules_message_id, about_message_id, rules_webhook_id, non_deferred_commands, \
    commands_without_penguin_requirement
from bot.handlers.select import AboutSelect
from bot.misc.penguin import Penguin


class PuffleBot(InteractionBot):
    def __init__(self, defer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defer = defer
        if self.defer:
            logger.info("Defer enabled")

    @staticmethod
    def override_disnake_classes():
        disnake.User.penguin = NewUser.penguin
        disnake.User.db = NewUser.db
        disnake.Member.penguin = NewMember.penguin
        disnake.Member.db = NewMember.db
        disnake.Interaction.avail_lang = NewAppInter.avail_lang

    def load_cogs(self):
        for file in os.listdir(bot.handlers.cogs.__path__[0]):
            if file.endswith(".py"):
                self.load_extension(f"bot.handlers.cogs.{file[:-3]}")

    def load_langs(self):
        self.i18n.load(bot.locale.__path__[0])
        logger.info(f'Loaded {len(os.listdir(bot.locale.__path__[0]))} languages')

    async def on_ready(self):
        await self.change_presence(activity=Game(name="CPPS.APP"))
        logger.info(f"Bot {self.user} ready")

    async def on_slash_command(self, inter: AppCommandInter):
        if not len(inter.data.options):
            logger.debug(
                f"{inter.author} use slash command /{inter.data.name} in #{inter.channel} in guild {inter.guild}")
        else:
            logger.debug(
                f"{inter.author} use slash command /{inter.data.name} in #{inter.channel} in guild {inter.guild} with options: {inter.data.options} ")
        if self.defer and inter.data.name not in non_deferred_commands:
            try:
                await inter.response.defer()
            except disnake.errors.HTTPException:
                logger.debug("Defer is not required")

        user_penguin = await inter.user.penguin
        user_db = await inter.user.db
        command_requires_penguin = inter.data.name not in commands_without_penguin_requirement

        if command_requires_penguin and user_penguin is None:
            raise KeyError("MY_PENGUIN_NOT_FOUND")

        if not user_db:
            await User.create(id=inter.user.id)

        if user_db.language != str(inter.avail_lang):
            await user_db.update(language=str(inter.avail_lang)).apply()

    async def on_connect(self):
        logger.info(f'Bot connected')

        try:
            if rules_message_id is not None:
                rules_webhook: Webhook = await self.fetch_webhook(rules_webhook_id)
                rules_message = await rules_webhook.fetch_message(rules_message_id)
                self.add_view(Rules(rules_message), message_id=rules_message_id)

            if about_message_id is not None:
                view = disnake.ui.View(timeout=None)
                view.add_item(AboutSelect())
                self.add_view(view, message_id=about_message_id)
        except disnake.errors.Forbidden:
            logger.error("Forbidden: no access to rules or about messages")

        for fundraising in await Fundraising.query.gino.all():
            try:
                channel = await self.fetch_channel(fundraising.channel_id)
                message = await channel.fetch_message(fundraising.message_id)
                p = await Penguin.get(fundraising.penguin_id)
                backers = len(
                    await FundraisingBackers.query.where(FundraisingBackers.message_id == message.id).gino.all())
                self.add_view(FundraisingButtons(fundraising, message, p, backers), message_id=message.id)
            except disnake.NotFound:
                await fundraising.delete()
            except disnake.errors.Forbidden:
                pass
            # except asyncpg.exceptions.UndefinedTableError:
            #     pass

    async def on_slash_command_error(self, inter: AppCommandInter, exception: CommandError or CommandOnCooldown):
        try:
            if isinstance(exception, CommandOnCooldown):
                end_time = f"<t:{int((datetime.now() + timedelta(seconds=exception.retry_after)).timestamp())}:R>"
                await inter.send(
                    f"{self.i18n.get('COMMAND_COOLDOWN_RESPONSE')[str(inter.avail_lang)].replace('%time%',end_time)}",
                    ephemeral=True)
                logger.error(f"User error: {exception.args[0]}")
            elif (exception.args[0] ==
                  "Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions"):
                await inter.send(f"{self.i18n.get('BOT_DOESNT_HAVE_PERMISSION')[str(inter.avail_lang)]}",
                                 ephemeral=True)
                logger.error(f"403 Forbidden: Missing Permissions")
            else:
                await inter.send(f"{self.i18n.get(exception.args[0])[str(inter.avail_lang)]}", ephemeral=True)
                logger.error(f"User error: {exception.args[0]}")

        except (KeyError, TypeError, AttributeError):
            await inter.send(f"Unknown error", ephemeral=True)
            logger.error(exception)
            traceback.print_exception(type(exception), exception, exception.__traceback__)

    async def on_error(self, event_method: str, *args, **kwargs):
        logger.error(f"Ignoring exception in {event_method}")
        traceback.print_exc()
