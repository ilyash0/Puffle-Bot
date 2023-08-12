import os

import disnake
from disnake import Webhook, Game
from disnake.ext.commands import InteractionBot
from loguru import logger
import bot.cogs
from bot.data.pufflebot.fundraising import Fundraising, FundraisingBackers
from bot.handlers.buttons import Rules, FundraisingButtons
from bot.misc.constants import rules_message_id, about_message_id, rules_webhook_id
from bot.handlers.select import About
from bot.misc.penguin import Penguin


class PuffleBot(InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_cogs(self):
        for file in os.listdir(bot.cogs.__path__[0]):
            if file.endswith(".py"):
                self.load_extension(f"bot.cogs.{file[:-3]}")

    async def on_ready(self):
        await self.change_presence(activity=Game(name="CPPS.APP"))

        logger.info(f"Bot {self.user} ready")

    async def on_connect(self):
        logger.info(f'Bot connected')

        if rules_message_id is not None:
            rules_webhook: Webhook = await self.fetch_webhook(rules_webhook_id)
            rules_message = await rules_webhook.fetch_message(rules_message_id)
            self.add_view(Rules(rules_message), message_id=rules_message_id)

        if about_message_id is not None:
            view = disnake.ui.View(timeout=None)
            view.add_item(About())
            self.add_view(view, message_id=about_message_id)

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
