import disnake

import bot.data.pufflebot.user
from bot.misc.penguin import Penguin
from bot.misc.utils import getPenguinOrNoneFromUserId


class NewUser(disnake.User):
    @property
    async def penguin(self) -> Penguin or None:
        return await getPenguinOrNoneFromUserId(self.id)

    @property
    async def db(self) -> bot.data.pufflebot.user.User:
        return await bot.data.pufflebot.user.User.get(self.id)

    @property
    async def lang(self) -> str:
        return (await self.db).language


class NewMember(disnake.Member):
    def __init__(self, *, data, guild, state, user_data=None):
        super().__init__(data=data, guild=guild, state=state, user_data=user_data)

    @property
    async def penguin(self) -> Penguin or None:
        return await getPenguinOrNoneFromUserId(self.id)

    @property
    async def db(self) -> bot.data.pufflebot.user.User:
        return await bot.data.pufflebot.user.User.get(self.id)

    @property
    async def lang(self) -> str:
        return (await self.db).language
