import os

import disnake
from disnake.ext.commands import InteractionBot, MissingPermissions
from loguru import logger
import bot.cogs


class PuffleBot(InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_cogs(self):
        for file in os.listdir(bot.cogs.__path__[0]):
            if file.endswith(".py"):
                self.load_extension(f"bot.cogs.{file[:-3]}")

    async def on_ready(self):
        await self.change_presence(activity=disnake.Game(name="CPPS.APP"))

        logger.info(f"Bot {self.user} ready")

    async def on_error(self, event_method: str, *args, **kwargs):
        logger.error(f"{event_method}.{args}.{kwargs}")

    async def on_slash_command_error(self, inter, exception):
        logger.error(exception)

        if isinstance(exception, MissingPermissions):
            await inter.response.send(f"У вас недостаточно прав для выполнения данной команды!", ephemeral=True)
