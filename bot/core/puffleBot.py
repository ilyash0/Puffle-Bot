import os

import disnake
from disnake import Webhook, Game
from disnake.ext.commands import InteractionBot, MissingPermissions
from loguru import logger
import bot.cogs
from bot.misc.buttons import Rules
from bot.misc.constants import rules_message_id, about_message_id, rules_webhook_id
from bot.misc.select import About


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

    async def on_error(self, event_method: str, *args, **kwargs):
        logger.error(f"{event_method}.{args}.{kwargs}")

    async def on_slash_command_error(self, inter, exception):
        logger.error(exception)

        if isinstance(exception, MissingPermissions):
            await inter.response.send(f"У вас недостаточно прав для выполнения данной команды!", ephemeral=True)
