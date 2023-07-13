from disnake import ApplicationCommandInteraction
from loguru import logger
import disnake
from disnake.ext.commands import Cog, slash_command

from bot.data import db_pb
from bot.misc.constants import loginCommand
from bot.misc.penguin import Penguin
from bot.data.pufflebot.users import Users, PenguinIntegrations
from bot.handlers.buttons import Logout, Login
from bot.handlers.select import SelectPenguins
from bot.misc.utils import getPenguinFromInter, getPenguinOrNoneFromUserId


class AccountManagementCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} account management app commands")

    @slash_command(name="login", description="Привязать свой Discord аккаунт к пингвину")
    async def login(self, inter: ApplicationCommandInteraction):
        return await inter.send(f"Перейдите на сайт и пройдите авторизацию", view=Login())

    @slash_command(name="logout", description="Отвязать свой Discord аккаунт от своего пингвина")
    async def logout(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinFromInter(inter)
        user: Users = await Users.get(inter.user.id)
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        await inter.send(f"Вы уверены, что хотите выйти с аккаунта `{p.safe_name()}`?",
                         view=Logout(inter, p, user, penguin_ids), ephemeral=True)

    @slash_command(name="switch", description="Сменить текущий аккаунт")
    async def switch(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinOrNoneFromUserId(inter.user.id)
        user: Users = await Users.get(inter.user.id)
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        if len(penguin_ids) == 0:
            return await inter.send(
                f"У вас не привязан ни один аккаунт. "
                f"Это можно исправить с помощью команды {loginCommand}", ephemeral=True)

        if len(penguin_ids) == 1:
            return await inter.send(
                f"У вас привязан только один аккаунт. "
                f"Вы можете привязать ещё несколько с помощью команды {loginCommand}", ephemeral=True)

        penguinsList = [{"safe_name": (await Penguin.get(penguin_id[0])).safe_name(), "id": penguin_id[0]} for
                        penguin_id in penguin_ids]
        view = disnake.ui.View()
        view.add_item(SelectPenguins(penguinsList, user))

        if p is None:
            return await inter.send(
                f"Ваш текущий аккаунт не выбран. Какой аккаунт вы хотите сделать текущим?",
                view=view, ephemeral=True)

        return await inter.send(
            f"Ваш текущий аккаунт: `{p.safe_name()}`. Какой аккаунт вы хотите сделать текущим?",
            view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(AccountManagementCommands(bot))
