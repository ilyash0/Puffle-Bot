import disnake

import bot.data.pufflebot.user
from bot.misc.penguin import Penguin
from bot.misc.utils import getPenguinOrNoneFromUserId


class NewUser(disnake.User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    async def penguin(self) -> Penguin or None:
        return await getPenguinOrNoneFromUserId(self.id)

    @property
    async def db(self) -> bot.data.pufflebot.user.User:
        return await bot.data.pufflebot.user.User.get(self.id)


class NewMember(disnake.Member):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    async def penguin(self) -> Penguin or None:
        return await getPenguinOrNoneFromUserId(self.id)

    @property
    async def db(self) -> bot.data.pufflebot.user.User:
        return await bot.data.pufflebot.user.User.get(self.id)
