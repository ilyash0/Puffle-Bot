from disnake import AppCommandInter
from loguru import logger
import disnake
from disnake.ext.commands import Cog, slash_command, CommandError

from bot.data import db_pb
from bot.misc.penguin import Penguin
from bot.data.pufflebot.user import User, PenguinIntegrations
from bot.handlers.button import Settings, Logout, Login
from bot.handlers.select import ChoosePenguin


class AccountManagementCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

        logger.info(f"Loaded {len(self.get_application_commands())} account management app commands")

    @slash_command()
    async def login(self, inter: AppCommandInter):
        """
        Log in to your current penguin {{LOGIN}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        await inter.send(self.bot.i18n.get("LOGIN_RESPONSE")[str(inter.avail_lang)],
                         view=Login(inter))

    @slash_command()
    async def logout(self, inter: AppCommandInter):
        """
        Log out from your current penguin {{LOGOUT}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        p: Penguin = await inter.user.penguin
        user: User = await inter.user.db
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        await inter.send(self.bot.i18n.get("LOGOUT_RESPONSE")[str(inter.avail_lang)].replace("%nickname%", p.safe_name()),
                         view=Logout(p, user, penguin_ids, inter), ephemeral=True)

    @slash_command()
    async def switch(self, inter: AppCommandInter):
        """
        Switch the current penguin {{SWITCH}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        p: Penguin = await inter.user.penguin
        user: User = await inter.user.db
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        if len(penguin_ids) == 0:
            raise CommandError("MY_PENGUIN_NOT_FOUND")

        if len(penguin_ids) == 1:
            raise CommandError("ONLY_ONE_PENGUIN_LINKED")

        penguins_list = [{"safe_name": (await Penguin.get(penguin_id[0])).safe_name(), "id": penguin_id[0]} for
                         penguin_id in penguin_ids]
        view = disnake.ui.View()
        view.add_item(ChoosePenguin(penguins_list, user, inter))

        if p is None:
            return await inter.send(
                self.bot.i18n.get("SWITCH_RESPONSE_ALT")[str(inter.avail_lang)],
                view=view, ephemeral=True)

        return await inter.send(
            self.bot.i18n.get("SWITCH_RESPONSE")[str(inter.avail_lang)].replace("%nickname%", p.safe_name()),
            view=view, ephemeral=True)

    @slash_command()
    async def settings(self, inter: AppCommandInter):
        """
        Your personal settings {{SETTINGS}}

        Parameters
        ----------
        inter: AppCommandInter
        """
        user: User = await inter.user.db
        if user is None:
            user: User = await User.create(inter.user.id)
        await inter.send(self.bot.i18n.get("SETTINGS_RESPONSE")[str(inter.avail_lang)], view=Settings(inter, user),
                         ephemeral=True)


def setup(bot):
    bot.add_cog(AccountManagementCommands(bot))
