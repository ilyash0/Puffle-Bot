from disnake import ApplicationCommandInteraction
from loguru import logger
import disnake
from disnake.ext.commands import Cog, slash_command

from bot.data import db_pb
from bot.misc.penguin import Penguin
from bot.data.pufflebot.user import User, PenguinIntegrations
from bot.handlers.button import Settings, Logout, Login
from bot.handlers.select import ChoosePenguin
from bot.misc.utils import getMyPenguinFromUserId, getPenguinOrNoneFromUserId


class AccountManagementCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} account management app commands")

    @slash_command()
    async def login(self, inter: ApplicationCommandInteraction):
        """
        Log in to your current penguin {{LOGIN}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        return await inter.send(self.bot.i18n.get("LOGIN_RESPONSE")[inter.locale.value], view=Login(inter))

    @slash_command()
    async def logout(self, inter: ApplicationCommandInteraction):
        """
        Log out from your current penguin {{LOGOUT}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        user: User = await User.get(inter.user.id)
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        await inter.send(self.bot.i18n.get("LOGOUT_RESPONSE")[inter.locale.value].replace("%nickname%", p.safe_name()),
                         view=Logout(p, user, penguin_ids, inter), ephemeral=True)

    @slash_command()
    async def switch(self, inter: ApplicationCommandInteraction):
        """
        Switch the current penguin {{SWITCH}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        p: Penguin = await getPenguinOrNoneFromUserId(inter.user.id)
        user: User = await User.get(inter.user.id)
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        if len(penguin_ids) == 0:
            raise KeyError("MY_PENGUIN_NOT_FOUND")

        if len(penguin_ids) == 1:
            raise KeyError("ONLY_ONE_PENGUIN_LINKED")

        penguinsList = [{"safe_name": (await Penguin.get(penguin_id[0])).safe_name(), "id": penguin_id[0]} for
                        penguin_id in penguin_ids]
        view = disnake.ui.View()
        view.add_item(ChoosePenguin(penguinsList, user, inter))

        if p is None:
            return await inter.send(
                self.bot.i18n.get("SWITCH_RESPONSE_ALT")[inter.locale.value],
                view=view, ephemeral=True)

        return await inter.send(
            self.bot.i18n.get("SWITCH_RESPONSE")[inter.locale.value].replace("%nickname%", p.safe_name()),
            view=view, ephemeral=True)

    @slash_command()
    async def settings(self, inter: ApplicationCommandInteraction):
        """
        Your personal settings {{SETTINGS}}

        Parameters
        ----------
        inter: ApplicationCommandInteraction
        """
        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        user: User = await User.get(inter.user.id)

        await inter.send(self.bot.i18n.get("SETTINGS_RESPONSE")[inter.locale.value], view=Settings(inter, user),
                         ephemeral=True)


def setup(bot):
    bot.add_cog(AccountManagementCommands(bot))
