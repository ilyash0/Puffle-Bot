from loguru import logger
from disnake.ext.commands import Bot, Cog, command, is_owner


class AdminCommands(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

        logger.info("Admin commands ready")

    @command()
    @is_owner()
    async def load(self, context, extension):
        self.bot.load_extension(f'cogs.admin{extension}')
        context.reply("load_extension successful")

    @command()
    @is_owner()
    async def unload(self, context, extension):
        self.bot.unload_extension(f'cogs.admin{extension}')
        context.reply("unload_extension successful")

    @command()
    @is_owner()
    async def reload(self, context, extension):
        self.bot.reload_extension(f'cogs.admin{extension}')
        context.reply("reload_extension successful")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
