import os

import disnake
from disnake.ext.commands import Bot, MissingPermissions
from loguru import logger
import bot.cogs.admin
import bot.cogs.user


class PuffleBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_cogs(self):
        for file in os.listdir(bot.cogs.admin.__path__[0]):
            if file.endswith(".py"):
                self.load_extension(f"bot.cogs.admin.{file[:-3]}")
        for file in os.listdir(bot.cogs.user.__path__[0]):
            if file.endswith(".py"):
                self.load_extension(f"bot.cogs.user.{file[:-3]}")

    async def on_ready(self):
        await self.change_presence(activity=disnake.Game(name="CPPS.app | Клуб Пингвинов"))

        logger.info("Bot ready")

    async def on_error(self, event_method: str, *args, **kwargs):
        logger.error(f"{event_method}.{args}.{kwargs}")

    async def on_command_error(self, context, exception):
        logger.error(exception)

        if isinstance(exception, MissingPermissions):
            await context.send(f"{context.author}, у вас недостаточно прав для выполнения данной команды!")

    async def on_slash_command_error(self, interaction, exception):
        logger.error(exception)
