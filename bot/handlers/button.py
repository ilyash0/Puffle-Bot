import sys
import traceback

import disnake
from disnake import MessageInteraction, AppCommandInter, Message
from disnake.ui import Item
from loguru import logger

from bot.data.pufflebot.fundraising import Fundraising, FundraisingBackers
from bot.data.pufflebot.user import User, PenguinIntegrations
from bot.handlers.modal import FundraisingModal
from bot.handlers.notification import notify_gift_coins, notify_coins_receive
from bot.misc.constants import embedRuleImageRu, embedRuleRu, embedRuleImageEn, embedRuleEn, embedRolesRu, \
    embedRolesEn, enFullRulesLink, ruFullRulesLink, embedRoles2Ru, embedRoles2En
from bot.misc.penguin import Penguin
from bot.misc.utils import getMyPenguinFromUserId, transferCoins


class Buttons(disnake.ui.View):
    def __init__(self, original_inter=None, timeout=None):
        super().__init__(timeout=timeout)
        self.original_inter: AppCommandInter or None = original_inter
        if self.original_inter is None:
            return

        for item in self.children:
            try:
                item.label = self.original_inter.bot.i18n.get(item.label)[str(self.original_inter.avail_lang)]
            except KeyError and TypeError:
                pass

    async def disable_all_items(self):
        if self.original_inter is None:
            return
        for item in self.children:
            item.disabled = True
        await self.original_inter.edit_original_response(view=self)

    async def on_timeout(self):
        await self.disable_all_items()

    async def on_error(self, error: Exception, item: Item, inter: MessageInteraction):
        try:
            logger.error(f"User error: {error.args[0]}")
            await inter.send(f"{inter.bot.i18n.get(error.args[0])[str(inter.avail_lang)]}", ephemeral=True)
        except (KeyError, TypeError, AttributeError):
            logger.error(f"Ignoring exception in buttons {self} for item {item}:", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__)
            await inter.send(f"Unknown error", ephemeral=True)


class FundraisingButtons(Buttons):
    def __init__(self, fundraising: Fundraising, message: disnake.Message, receiver: Penguin, backers: int,
                 original_inter: AppCommandInter = None):
        super().__init__(original_inter=original_inter)
        self.fundraising = fundraising
        self.message = message
        self.receiver = receiver
        self.raised = fundraising.raised
        self.goal = fundraising.goal
        self.backers = backers
        self.command = "fundraising"

    async def donate(self, inter: MessageInteraction, coins: int):
        await inter.response.defer()
        p: Penguin = await getMyPenguinFromUserId(inter.author.id)
        await transferCoins(p, self.receiver, int(coins))
        await notify_coins_receive(p, self.receiver, coins, None, self.command)
        await inter.send(
            inter.bot.i18n.get("COINS_TRANSFERRED")[str(inter.avail_lang)].
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

    @disnake.ui.button(label="100", style=disnake.ButtonStyle.blurple, emoji="<:coin:788877461588279336>",
                       custom_id="100")
    async def coins100_button(self, button: disnake.ui.Button, inter: MessageInteraction):
        await self.donate(inter, int(button.label))

    @disnake.ui.button(label="500", style=disnake.ButtonStyle.blurple, emoji="<:coin:788877461588279336>",
                       custom_id="500")
    async def coins500_button(self, button: disnake.ui.Button, inter: MessageInteraction):
        await self.donate(inter, int(button.label))

    @disnake.ui.button(label="1000", style=disnake.ButtonStyle.blurple, emoji="<:coin:788877461588279336>",
                       custom_id="1000")
    async def coins1000_button(self, button: disnake.ui.Button, inter: MessageInteraction):
        await self.donate(inter, int(button.label))

    @disnake.ui.button(label="OTHER_AMOUNT", style=disnake.ButtonStyle.gray,
                       custom_id="other")
    async def other_sum_button(self, _, inter: MessageInteraction):
        modal = FundraisingModal(
            self.donate,
            inter.bot.i18n.get("FR_MODAL_TITLE")[str(inter.avail_lang)].replace("%nickname%",
                                                                                self.receiver.safe_name()),
            inter)
        await inter.response.send_modal(modal)


class Rules(Buttons):
    def __init__(self, massage):
        super().__init__()
        self.massage = massage
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: MessageInteraction):
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
    async def full_rules(self, button: disnake.ui.Button, inter: MessageInteraction):
        ...


class RulesEphemeral(Buttons):
    def __init__(self, inter):
        super().__init__()
        self.original_inter = inter
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: MessageInteraction):
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
    async def full_rules(self, button: disnake.ui.Button, inter: MessageInteraction):
        ...


class Roles(Buttons):
    def __init__(self, original_inter):
        super().__init__()
        self.original_inter = original_inter
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: MessageInteraction):
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
    def __init__(self, original_inter: AppCommandInter):
        super().__init__(original_inter=original_inter)

    @disnake.ui.button(label="LOGIN", url="https://cpps.app/discord/login")
    async def login_button(self, button: disnake.ui.Button, inter: MessageInteraction):
        ...


class Logout(Buttons):
    def __init__(self, p: Penguin, user: User, penguin_ids, original_inter: AppCommandInter):
        super().__init__(original_inter=original_inter)
        self.p: Penguin = p
        self.user: User = user
        self.penguin_ids = penguin_ids

    @disnake.ui.button(label="CANCEL", style=disnake.ButtonStyle.gray, custom_id="cancel")
    async def cancel_button(self, _, inter: MessageInteraction):
        await self.disable_all_items()
        await inter.send(inter.bot.i18n.get("CANCELLED")[str(inter.avail_lang)], ephemeral=True)

    @disnake.ui.button(label="LOGOUT", style=disnake.ButtonStyle.red, custom_id="logout")
    async def logout_button(self, _, inter: MessageInteraction):
        await self.disable_all_items()
        await PenguinIntegrations.delete.where(PenguinIntegrations.penguin_id == self.p.id).gino.status()
        if len(self.penguin_ids) == 1:
            await self.user.update(penguin_id=None).apply()
            return await inter.send(
                inter.bot.i18n.get("LOGOUT_SUCCESS")[str(inter.avail_lang)].replace("%nickname%", self.p.safe_name()),
                ephemeral=True)

        if len(self.penguin_ids) == 2:
            new_current_penguin: Penguin = await Penguin.get(self.penguin_ids[0][0])
            await self.user.update(penguin_id=self.penguin_ids[0][0]).apply()
            message = inter.bot.i18n.get("LOGOUT_SUCCESS_ALT")[str(inter.avail_lang)]
            message.replace("%nickname%", self.p.safe_name())
            message.replace("%new_nickname%", new_current_penguin.safe_name())
            return await inter.send(message, ephemeral=True)

        return await inter.send(
            inter.bot.i18n.get("LOGOUT_SUCCESS_ALT2")[str(inter.locale)].replace("%nickname%", self.p.safe_name()),
            ephemeral=True)


class Settings(Buttons):
    def __init__(self, original_inter: AppCommandInter, user: User):
        super().__init__(original_inter=original_inter)
        self.user: User = user

    async def toggle_button_color(self, button, param):
        if param:
            button.style = disnake.ButtonStyle.gray
        else:
            button.style = disnake.ButtonStyle.green
        await self.original_inter.edit_original_response(view=self)

    @disnake.ui.button(label="ALL", style=disnake.ButtonStyle.green, custom_id="allNotify")
    async def all_notify(self, button: disnake.ui.Button, inter: MessageInteraction):
        await inter.response.defer()
        if self.user.enabled_notify:
            button.style = disnake.ButtonStyle.gray
            self.children[1].disabled = True
            self.children[2].disabled = True
        else:
            button.style = disnake.ButtonStyle.green
            self.children[1].disabled = False
            self.children[2].disabled = False
        await self.user.update(enabled_notify=not self.user.enabled_notify).apply()
        await self.original_inter.edit_original_response(view=self)

    @disnake.ui.button(label="TOP-UP", style=disnake.ButtonStyle.green,
                       custom_id="coinsNotify")
    async def coins_notify(self, button: disnake.ui.Button, inter: MessageInteraction):
        await inter.response.defer()
        await self.toggle_button_color(button, self.user.enabled_coins_notify)
        await self.user.update(enabled_coins_notify=not self.user.enabled_coins_notify).apply()

    @disnake.ui.button(label="END_MEMBERSHIP", style=disnake.ButtonStyle.green,
                       custom_id="membershipNotify")
    async def membership_notify(self, button: disnake.ui.Button, inter: MessageInteraction):
        await inter.response.defer()
        await self.toggle_button_color(button, self.user.enabled_membership_notify)
        await self.user.update(enabled_membership_notify=not self.user.enabled_membership_notify).apply()


class TopMinutesButton(Buttons):
    def __init__(self, original_inter: AppCommandInter):
        super().__init__(original_inter=original_inter)

    @disnake.ui.button(label="TOP_50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=online")
    async def top(self, button: disnake.ui.Button, inter: MessageInteraction):
        ...


class TopCoinsButton(Buttons):
    def __init__(self, original_inter: AppCommandInter):
        super().__init__(original_inter=original_inter)

    @disnake.ui.button(label="TOP_50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=coins")
    async def top(self, button: disnake.ui.Button, inter: MessageInteraction):
        ...


class TopStampsButton(Buttons):
    def __init__(self, original_inter: AppCommandInter):
        super().__init__(original_inter=original_inter)

    @disnake.ui.button(label="TOP_50", style=disnake.ButtonStyle.link,
                       url="https://play.cpps.app/ru/top/?top=stamp")
    async def top(self, button: disnake.ui.Button, inter: MessageInteraction):
        ...


class MembershipButton(Buttons):
    def __init__(self, original_inter: AppCommandInter):
        super().__init__(original_inter=original_inter)

    @disnake.ui.button(label="PURCHASE_MEMBERSHIP", style=disnake.ButtonStyle.link,
                       url="https://cpps.app/membership")
    async def buy_membership(self, button: disnake.ui.Button, inter: MessageInteraction):
        ...


class Gift(Buttons):
    def __init__(self, original_inter: AppCommandInter, message: Message, coins: int, giver_penguin: Penguin):
        super().__init__(original_inter=original_inter)
        self.message = message
        self.coins = coins
        self.giver_penguin: Penguin = giver_penguin

    @disnake.ui.button(label="GIFT", style=disnake.ButtonStyle.blurple, custom_id="gift", emoji="🎁")
    async def gift(self, button, inter: MessageInteraction):
        button.disabled = True
        await self.message.edit(view=self)
        p = await getMyPenguinFromUserId(inter.user.id)
        if p.moderator or p.id == self.giver_penguin.id:
            await inter.send(inter.bot.i18n.get("NOT_FOR_YOU")[str(inter.locale)], ephemeral=True)
            button.disabled = False
            await self.message.edit(view=self)
            return

        button.disabled = True
        await self.message.edit(view=self)
        await transferCoins(self.giver_penguin, p, self.coins)
        await inter.send(f"Подарок в виде {self.coins} монет забирает {p.safe_name()}")
        await notify_gift_coins(inter.user, p, self.coins)
