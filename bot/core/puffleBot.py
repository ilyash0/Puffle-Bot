import os
import traceback

import disnake
from disnake import Webhook, Game, ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot, CommandError
from loguru import logger
import bot.locale
import bot.cogs
from bot.core.disnaleOverride import NewUser, NewMember
from bot.data.pufflebot.fundraising import Fundraising, FundraisingBackers
from bot.handlers.button import Rules, FundraisingButtons
from bot.misc.constants import rules_message_id, about_message_id, rules_webhook_id
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
        disnake.User.lang = NewUser.lang
        disnake.Member.penguin = NewMember.penguin
        disnake.Member.db = NewMember.db
        disnake.Member.lang = NewMember.lang

    def load_cogs(self):
        for file in os.listdir(bot.cogs.__path__[0]):
            if file.endswith(".py"):
                self.load_extension(f"bot.cogs.{file[:-3]}")

    def load_langs(self):
        self.i18n.load(bot.locale.__path__[0])
        logger.info(f'Loaded {len(os.listdir(bot.locale.__path__[0]))} languages')

    async def on_ready(self):
        await self.change_presence(activity=Game(name="CPPS.APP"))

        logger.info(f"Bot {self.user} ready")

    async def on_slash_command(self, inter: ApplicationCommandInteraction):
        logger.debug(f"{inter.author} use slash command /{inter.data.name} in #{inter.channel}")
        if self.defer:
            try:
                await inter.response.defer()
            except disnake.errors.HTTPException:
                logger.debug("Defer is not required")
        if await inter.user.lang != inter.locale.value:
            new_lang = inter.locale.value
            if new_lang not in ["ru", "en-GB", "en-US"]:
                new_lang = "en-GB"
            await inter.user.db.update(language=new_lang).apply()
        if inter.data.name not in ["ilyash", "online", "login", "top"] and (await inter.user.penguin) is None:
            raise KeyError("MY_PENGUIN_NOT_FOUND")

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

    async def on_slash_command_error(self, inter: ApplicationCommandInteraction, exception: CommandError):
        try:
            logger.error(f"User error: {exception.original.args[0]}")
            await inter.send(f"{self.i18n.get(exception.original.args[0])[inter.locale.value]}", ephemeral=True)
        except KeyError and TypeError and AttributeError:
            logger.error(exception)
            traceback.print_exception(type(exception), exception, exception.__traceback__)
            await inter.send(f"Unknown error", ephemeral=True)

    async def on_error(self, event_method: str, *args, **kwargs):
        # logger.error(f"ERROR: {event_method}")
        logger.error(f"Ignoring exception in {event_method}")
        traceback.print_exc()
