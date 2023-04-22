import disnake
from loguru import logger
from bot.data import db
from bot.core.puffleBot import PuffleBot


class Server:
    def __init__(self, config):
        self.bot = None
        self.config = config
        self.db = db
        self.peers_by_ip = {}

        self.attributes = {}

        # self.client_class = Penguin

        self.penguins_by_id = {}
        self.penguins_by_username = {}

    async def start(self):
        logger.add("logs/log.log")

        await self.db.set_bind(
            "postgresql://{}:{}@{}/{}".format(
                self.config.database_username,
                self.config.database_password,
                self.config.database_address,
                self.config.database_name,
            )
        )

        logger.info("Booting discord bot")
        intents = disnake.Intents.default()
        # noinspection PyDunderSlots,PyUnresolvedReferences
        intents.message_content = True

        self.bot = PuffleBot(command_prefix="!", intents=intents,
                             test_guilds=[755445822920982548], owner_id=527140180696629248)
        self.bot.load_cogs()

        try:
            await self.bot.start(self.config.token)
        finally:
            if not self.bot.is_closed():
                await self.bot.close()
