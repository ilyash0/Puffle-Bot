from disnake import ApplicationCommandInteraction
from loguru import logger
import disnake
from disnake.ext.commands import Cog, slash_command

from bot.data import db_pb
from bot.misc.constants import loginCommand, switchCommand
from bot.misc.penguin import Penguin
from bot.data.pufflebot.user import User, PenguinIntegrations
from bot.handlers.buttons import Buttons
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
        user: User = await User.get(inter.user.id)
        penguin_ids = await db_pb.select([PenguinIntegrations.penguin_id]).where(
            (PenguinIntegrations.discord_id == inter.user.id)).gino.all()

        await inter.send(f"Вы уверены, что хотите выйти с аккаунта `{p.safe_name()}`?",
                         view=Logout(inter, p, user, penguin_ids), ephemeral=True)

    @slash_command(name="switch", description="Сменить текущий аккаунт")
    async def switch(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinOrNoneFromUserId(inter.user.id)
        user: User = await User.get(inter.user.id)
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

    @slash_command(name="settings", description="Настройки пользователя бота")
    async def settings(self, inter: ApplicationCommandInteraction):
        p: Penguin = await getPenguinFromInter(inter)
        user: User = await User.get(inter.user.id)

        await inter.send("Можете изменить свои настройки здесь.\n# Уведомления", view=Settings(inter, user),
                         ephemeral=True)


class Login(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Войти", url="https://cpps.app/discord/login")
    async def loginButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class Logout(Buttons):
    def __init__(self, inter: disnake.CommandInteraction, p, user, penguin_ids):
        super().__init__(inter, timeout=None)
        self.p = p
        self.user = user
        self.penguin_ids = penguin_ids

    async def on_timeout(self):
        ...

    @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.gray, custom_id="cancel")
    async def cancelButton(self, _, inter: disnake.CommandInteraction):
        await self.disableAllItems()
        await inter.send(f"Отменено", ephemeral=True)

    @disnake.ui.button(label="Выйти", style=disnake.ButtonStyle.red, custom_id="logout")
    async def logoutButton(self, _, inter: disnake.CommandInteraction):
        await self.disableAllItems()
        await PenguinIntegrations.delete.where(PenguinIntegrations.penguin_id == self.p.id).gino.status()
        if len(self.penguin_ids) == 1:
            await self.user.update(penguin_id=None).apply()
            return await inter.send(f"Ваш аккаунт `{self.p.safe_name()}` успешно отвязан.", ephemeral=True)

        if len(self.penguin_ids) == 2:
            newCurrentPenguin: Penguin = await Penguin.get(self.penguin_ids[0][0])
            await self.user.update(penguin_id=self.penguin_ids[0][0]).apply()
            return await inter.send(
                f"Ваш аккаунт `{self.p.safe_name()}` успешно отвязан. "
                f"Сейчас ваш текущий аккаунт `{newCurrentPenguin.safe_name()}`", ephemeral=True)

        return await inter.send(
            f"Ваш аккаунт `{self.p.safe_name()}` успешно отвязан. "
            f"Чтобы выбрать текущий аккаунт воспользуйтесь командой {switchCommand}", ephemeral=True)


class Settings(disnake.ui.View):
    def __init__(self, original_inter, user):
        super().__init__()
        self.original_inter = original_inter
        self.user: User = user

    @disnake.ui.button(label="Все", style=disnake.ButtonStyle.green, custom_id="allNotify")
    async def allNotify(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.defer()
        if self.user.enabled_notify:
            button.style = disnake.ButtonStyle.gray
            self.children[1].disabled = True
            self.children[2].disabled = True
        else:
            button.style = disnake.ButtonStyle.green
            self.children[1].disabled = False
            self.children[2].disabled = False
        self.user.enabled_notify = not self.user.enabled_notify
        await self.original_inter.edit_original_response(view=self)

    @disnake.ui.button(label="О пополнении баланса", style=disnake.ButtonStyle.green,
                       custom_id="coinsNotify")
    async def coinsNotify(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.defer()
        if self.user.enabled_coins_notify:
            button.style = disnake.ButtonStyle.gray
        else:
            button.style = disnake.ButtonStyle.green
        self.user.enabled_coins_notify = not self.user.enabled_coins_notify
        await self.original_inter.edit_original_response(view=self)

    @disnake.ui.button(label="Об окончании подписки", style=disnake.ButtonStyle.green,
                       custom_id="membershipNotify")
    async def membershipNotify(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.defer()
        if self.user.enabled_membership_notify:
            button.style = disnake.ButtonStyle.gray
        else:
            button.style = disnake.ButtonStyle.green
        self.user.enabled_membership_notify = not self.user.enabled_membership_notify
        await self.original_inter.edit_original_response(view=self)


def setup(bot):
    bot.add_cog(AccountManagementCommands(bot))
