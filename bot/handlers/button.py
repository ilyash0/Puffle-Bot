import sys
import traceback

import disnake
from disnake import MessageInteraction, ApplicationCommandInteraction
from disnake.ui import Item
from loguru import logger

from bot.data.pufflebot.fundraising import Fundraising, FundraisingBackers
from bot.data.pufflebot.user import User, PenguinIntegrations
from bot.handlers.modal import FundraisingModal
from bot.handlers.notification import notifyCoinsReceive
from bot.misc.constants import embedRuleImageRu, embedRuleRu, embedRuleImageEn, embedRuleEn, embedRolesRu, \
    embedRolesEn, enFullRulesLink, ruFullRulesLink, embedRoles2Ru, embedRoles2En
from bot.misc.penguin import Penguin
from bot.misc.utils import getMyPenguinFromUserId, transferCoins


class Buttons(disnake.ui.View):
    def __init__(self, original_inter=None, timeout=None):
        super().__init__(timeout=timeout)
        self.original_inter: ApplicationCommandInteraction or None = original_inter
        if self.original_inter is None:
            return

        for item in self.children:
            try:
                item.label = self.original_inter.bot.i18n.get(item.label)[self.original_inter.locale.value]
            except KeyError and TypeError:
                pass

    async def disableAllItems(self):
        if self.original_inter is None:
            return
        for item in self.children:
            item.disabled = True
        await self.original_inter.edit_original_response(view=self)

    async def on_timeout(self):
        await self.disableAllItems()

    async def on_error(self, error: Exception, item: Item, inter: MessageInteraction):
        logger.error(f"Ignoring exception in view {self} for item {item}:", file=sys.stderr)
        traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)
        await inter.send(f"{inter.bot.i18n.get(error.args[0])[inter.locale.value]}", ephemeral=True)


class FundraisingButtons(Buttons):
    def __init__(self, fundraising: Fundraising, message: disnake.Message, receiver: Penguin, backers: int,
                 original_inter=None):
        super().__init__(original_inter)
        self.fundraising = fundraising
        self.message = message
        self.receiver = receiver
        self.raised = fundraising.raised
        self.goal = fundraising.goal
        self.backers = backers
        self.command = "fundraising"

    async def donate(self, inter: disnake.CommandInteraction, coins: int):
        await inter.response.defer()
        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        await transferCoins(p, self.receiver, int(coins))
        await notifyCoinsReceive(p, self.receiver, coins, None, self.command)
        await inter.send(
            inter.bot.i18n.get("COINS_TRANSFERRED")[inter.locale.value].
            replace("%coins%", str(coins)).replace("%receiver%", self.receiver.safe_name()))

        self.raised += int(coins)
        embed = self.message.embeds[0]
        embed.add_field(embed.fields[0].name,
                        f"{self.raised:,}{f' / {self.goal:,}' if self.goal else ''}".replace(',', ' '))
        embed.remove_field(0)

        if not await FundraisingBackers.get([self.message.id, p.id]):
            self.backers += 1
            await FundraisingBackers.create(message_id=self.message.id, receiver_penguin_id=self.receiver.id,
                                            backer_penguin_id=p.id)

        embed.set_footer(text=f"{embed.footer.text.split()[0]} {self.backers}")

        await self.message.edit(embed=embed)
        await self.fundraising.update(raised=self.raised).apply()
        await notifyCoinsReceive(p, self.receiver, int(coins), command="fundraising")

    @disnake.ui.button(label="100", style=disnake.ButtonStyle.blurple, emoji="<:coin:788877461588279336>",
                       custom_id="100")
    async def coins100Button(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await self.donate(inter, int(button.label))

    @disnake.ui.button(label="500", style=disnake.ButtonStyle.blurple, emoji="<:coin:788877461588279336>",
                       custom_id="500")
    async def coins500Button(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await self.donate(inter, int(button.label))

    @disnake.ui.button(label="1000", style=disnake.ButtonStyle.blurple, emoji="<:coin:788877461588279336>",
                       custom_id="1000")
    async def coins1000Button(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await self.donate(inter, int(button.label))

    @disnake.ui.button(label="OTHER_AMOUNT", style=disnake.ButtonStyle.gray,
                       custom_id="other")
    async def otherSumButton(self, _, inter: disnake.CommandInteraction):
        await inter.response.send_modal(
            modal=FundraisingModal(self.donate,
                                   inter.bot.i18n.get("FR_MODAL_TITLE")[inter.locale.value].replace("%nickname%",
                                                                                                    self.receiver.safe_name()),
                                   inter))


class Rules(Buttons):
    def __init__(self, massage):
        super().__init__()
        self.massage = massage
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if self.language == "En":
            self.language = "Ru"
            button.label = "Translate"
            button.emoji = "🇺🇸"
            self.children[1].label = "Полные правила"
            self.children[1].url = ruFullRulesLink
            await self.massage.edit(embeds=[embedRuleImageRu, embedRuleRu], view=self)
        elif self.language == "Ru":
            self.language = "En"
            button.label = "Перевести"
            button.emoji = "🇷🇺"
            self.children[1].label = "Full rules"
            self.children[1].url = enFullRulesLink

            await self.massage.edit(embeds=[embedRuleImageEn, embedRuleEn], view=self)
        await inter.response.defer()

    @disnake.ui.button(label="Полные правила", style=disnake.ButtonStyle.link,
                       url="https://wiki.cpps.app/index.php?title=Правила")
    async def FullRules(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class RulesEphemeral(Buttons):
    def __init__(self, inter):
        super().__init__()
        self.original_inter = inter
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if self.language == "En":
            self.language = "Ru"
            button.label = "Translate"
            button.emoji = "🇺🇸"
            self.children[1].label = "Полные правила"
            self.children[1].url = ruFullRulesLink
            await self.original_inter.edit_original_response(embeds=[embedRuleImageRu, embedRuleRu], view=self)
        elif self.language == "Ru":
            self.language = "En"
            button.label = "Перевести"
            button.emoji = "🇷🇺"
            self.children[1].label = "Full rules"

            self.children[1].url = enFullRulesLink
            await self.original_inter.edit_original_response(embeds=[embedRuleImageEn, embedRuleEn], view=self)
        await inter.response.defer()

    @disnake.ui.button(label="Полные правила", style=disnake.ButtonStyle.link,
                       url="https://wiki.cpps.app/index.php?title=Правила")
    async def FullRules(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class Roles(Buttons):
    def __init__(self, original_inter):
        super().__init__()
        self.original_inter = original_inter
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if self.language == "En":
            self.language = "Ru"
            button.label = "Translate"
            button.emoji = "🇺🇸"
            await self.original_inter.edit_original_response(embeds=[embedRolesRu, embedRoles2Ru], view=self)
        elif self.language == "Ru":
            self.language = "En"
            button.label = "Перевести"
            button.emoji = "🇷🇺"
            await self.original_inter.edit_original_response(embeds=[embedRolesEn, embedRoles2En], view=self)
        await inter.response.defer()


class Login(Buttons):
    def __init__(self, original_inter):
        super().__init__(original_inter=original_inter)

    @disnake.ui.button(label="LOGIN", url="https://cpps.app/discord/login")
    async def loginButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class Logout(Buttons):
    def __init__(self, p, user, penguin_ids, original_inter):
        super().__init__(original_inter)
        self.p = p
        self.user = user
        self.penguin_ids = penguin_ids

    @disnake.ui.button(label="CANCEL", style=disnake.ButtonStyle.gray, custom_id="cancel")
    async def cancelButton(self, _, inter: disnake.CommandInteraction):
        await self.disableAllItems()
        await inter.send(inter.bot.i18n.get("CANCELLED")[inter.locale.value], ephemeral=True)

    @disnake.ui.button(label="LOGOUT", style=disnake.ButtonStyle.red, custom_id="logout")
    async def logoutButton(self, _, inter: disnake.CommandInteraction):
        await self.disableAllItems()
        await PenguinIntegrations.delete.where(PenguinIntegrations.penguin_id == self.p.id).gino.status()
        if len(self.penguin_ids) == 1:
            await self.user.update(penguin_id=None).apply()
            return await inter.send(
                inter.bot.i18n.get("LOGOUT_SUCCESS")[inter.locale.value].replace("%nickname%", self.p.safe_name()),
                ephemeral=True)

        if len(self.penguin_ids) == 2:
            newCurrentPenguin: Penguin = await Penguin.get(self.penguin_ids[0][0])
            await self.user.update(penguin_id=self.penguin_ids[0][0]).apply()
            message = inter.bot.i18n.get("LOGOUT_SUCCESS_ALT")[inter.locale.value]
            message.replace("%nickname%", self.p.safe_name())
            message.replace("%new_nickname%", newCurrentPenguin.safe_name())
            return await inter.send(message, ephemeral=True)

        return await inter.send(
            inter.bot.i18n.get("LOGOUT_SUCCESS_ALT2")[inter.locale.value].replace("%nickname%", self.p.safe_name()),
            ephemeral=True)


class Settings(Buttons):
    def __init__(self, original_inter, user):
        super().__init__(original_inter)
        self.user: User = user

    @disnake.ui.button(label="ALL", style=disnake.ButtonStyle.green, custom_id="allNotify")
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

    @disnake.ui.button(label="TOP-UP", style=disnake.ButtonStyle.green,
                       custom_id="coinsNotify")
    async def coinsNotify(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.defer()
        if self.user.enabled_coins_notify:
            button.style = disnake.ButtonStyle.gray
        else:
            button.style = disnake.ButtonStyle.green
        self.user.enabled_coins_notify = not self.user.enabled_coins_notify
        await self.original_inter.edit_original_response(view=self)

    @disnake.ui.button(label="END_MEMBERSHIP", style=disnake.ButtonStyle.green,
                       custom_id="membershipNotify")
    async def membershipNotify(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        await inter.response.defer()
        if self.user.enabled_membership_notify:
            button.style = disnake.ButtonStyle.gray
        else:
            button.style = disnake.ButtonStyle.green
        self.user.enabled_membership_notify = not self.user.enabled_membership_notify
        await self.original_inter.edit_original_response(view=self)


class TopMinutesButton(Buttons):
    def __init__(self, original_inter):
        super().__init__(original_inter)

    @disnake.ui.button(label="TOP_50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=online")
    async def top(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class TopCoinsButton(Buttons):
    def __init__(self, original_inter):
        super().__init__(original_inter)

    @disnake.ui.button(label="TOP_50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=coins")
    async def top(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class TopStampsButton(Buttons):
    def __init__(self, original_inter):
        super().__init__(original_inter)

    @disnake.ui.button(label="TOP_50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=stamp")
    async def top(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...
