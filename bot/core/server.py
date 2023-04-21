from loguru import logger

# from bot.penguin import Penguin
from bot.data import db
from bot.handlers import commands


class Server:
    def __init__(self, config):
        self.server = None
        self.redis = None
        self.cache = None
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

        logger.info(f"Listening on {self.config.address}:{self.config.port}")

        async with commands.bot:
            await commands.bot.start(self.config.token, reconnect=True)
