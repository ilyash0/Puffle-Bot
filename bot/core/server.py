import asyncio
import disnake
from disnake.ext.commands import CommandSyncFlags
from loguru import logger
from bot.data import db_cp, db_pb
from bot.core.puffleBot import PuffleBot


class Server:
    def __init__(self, config):
        self.server = None
        self.bot = None
        self.config = config
        self.db_cp = db_cp
        self.db_pb = db_pb
        self.peers_by_ip = {}

        self.attributes = {}

        self.penguins_by_id = {}
        self.penguins_by_username = {}

    async def start(self):
        logger.add("logs/log.log")

        await self.db_cp.set_bind(
            "postgresql://{}:{}@{}/{}".format(
                self.config.database_username,
                self.config.database_password,
                self.config.database_address,
                self.config.database_name_cp,
            )
        )

        await self.db_pb.set_bind(
            "postgresql://{}:{}@{}/{}".format(
                self.config.database_username,
                self.config.database_password,
                self.config.database_address,
                self.config.database_name_pb,
            )
        )

        # this need for kill server on port
        self.server = await asyncio.start_server(
            self.client_connected, self.config.address,
            self.config.port
        )

        logger.info("Booting discord bot")
        intents = disnake.Intents.default()
        intents.message_content = True
        command_sync_flags = CommandSyncFlags.default()
        command_sync_flags.sync_commands = True

        self.bot = PuffleBot(command_prefix="!", intents=intents, command_sync_flags=command_sync_flags,
                             owner_id=527140180696629248)  # test_guilds=[755445822920982548],
        self.bot.load_cogs()

        try:
            await self.bot.start(self.config.token)
        finally:
            if not self.bot.is_closed():
                await self.bot.close()

    async def client_connected(self, reader, writer):
        ...
