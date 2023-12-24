import asyncio
import disnake
from disnake.ext.commands import CommandSyncFlags
from loguru import logger

from bot.core.client import Client
from bot.data import db_cp, db_pb
from bot.core.puffleBot import PuffleBot
from bot.events import event
from bot.events.module import hot_reload_module
import bot.handlers


class Server:
    def __init__(self, config):
        self.server = None
        self.bot = None
        self.config = config
        self.db_cp = db_cp
        self.db_pb = db_pb

        self.client_class = Client
        self.client_object = None

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

        self.server = await asyncio.start_server(
            self.client_connected, self.config.address,
            self.config.port
        )

        logger.info("Booting discord bot")

        await self.connect_to_houdini()

        intents = disnake.Intents.default()
        intents.message_content = True
        command_sync_flags = CommandSyncFlags.default()
        command_sync_flags.sync_commands = True

        self.bot = PuffleBot(defer=self.config.defer, intents=intents, command_sync_flags=command_sync_flags,
                             owner_id=527140180696629248)  # test_guilds=[755445822920982548],

        await hot_reload_module(bot.handlers)
        await event.emit("boot", self)
        self.bot.load_langs()
        self.bot.load_cogs()
        self.bot.override_disnake_classes()

        try:
            await self.bot.start(self.config.token)
        finally:
            if not self.bot.is_closed():
                await self.bot.close()

    async def client_connected(self, reader, writer):
        ...

    async def connect_to_houdini(self):
        try:
            reader, writer = await asyncio.open_connection(self.config.houdini_address, self.config.houdini_port)
        except ConnectionRefusedError:
            logger.error("The remote computer refused the network connection")
            return
        logger.info(f"Server ('{self.config.houdini_address}', {self.config.houdini_port}) connected")
        self.client_object = self.client_class(self, reader, writer)
