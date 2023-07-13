import disnake
from disnake import Embed

from bot.data.pufflebot.users import PenguinIntegrations
from bot.misc.constants import embedRuleImageRu, embedRuleRu, embedRuleImageEn, embedRuleEn, embedRolesRu, \
    embedRolesEn, enFullRulesLink, ruFullRulesLink, switchCommand
from bot.misc.penguin import Penguin
from bot.misc.utils import getPenguinFromInter, transferCoinsAndReturnStatus


class Buttons(disnake.ui.View):
    def __init__(self, original_inter, timeout=900):
        super().__init__(timeout=timeout)
        self.original_inter = original_inter

    async def disableAllItems(self):
        for item in self.children:
            item.disabled = True
        await self.original_inter.edit_original_response(view=self)

    async def on_timeout(self):
        await self.disableAllItems()


class Question(Buttons):
    def __init__(self, inter, function):
        super().__init__(inter, function)

    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.green, custom_id="yes")
    async def yesButton(self, _, inter: disnake.CommandInteraction):
        ...

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red, custom_id="no")
    async def noButton(self, _, inter: disnake.CommandInteraction):
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


class Continue(Buttons):
    def __init__(self, inter: disnake.CommandInteraction, function):
        super().__init__(inter, function)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.blurple, custom_id="continue")
    async def continueButton(self, _, inter: disnake.CommandInteraction):
        ...


class FundraisingButtons(disnake.ui.View):
    # TODO: Make the "other amount" button
    def __init__(self, fundraising: Fundraising, message: disnake.Message, receiver: Penguin, backers: int):
        super().__init__(timeout=None)
        self.fundraising = fundraising
        self.message = message
        self.receiver = receiver
        self.raised = fundraising.raised
        self.goal = fundraising.goal
        self.backers = backers

    async def donate(self, inter: disnake.CommandInteraction, coins: int):
        p: Penguin = await getPenguinFromInter(inter)
        statusDict = await transferCoinsAndReturnStatus(p, self.receiver, int(coins))
        if statusDict["code"] == 400:
            return await inter.send(statusDict["message"], ephemeral=True)

        self.raised += int(coins)
        embed = Embed(color=0x2B2D31, title=self.message.embeds[0].title)
        embed.add_field("Собрано монет", f"{self.raised}{f' из {self.goal}' if self.goal else ''}")
        embed.set_footer(text=f"Спонсоры: {self.backers + 1}")

        if not await FundraisingBackers.get([self.message.id, p.id]):
            self.backers += 1
            await FundraisingBackers.create(message_id=self.message.id, receiver_penguin_id=self.receiver.id,
                                            backer_penguin_id=p.id)

        embed.set_footer(text=f"Спонсоры: {self.backers}")

        await self.message.edit(embed=embed)
        await self.fundraising.update(raised=self.raised).apply()
        await inter.send(statusDict["message"], ephemeral=True)

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


class Login(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Войти", url="https://cpps.app/discord/login")
    async def loginButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class Rules(disnake.ui.View):
    def __init__(self, massage):
        super().__init__(timeout=None)
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


class RulesEphemeral(disnake.ui.View):
    def __init__(self, inter):
        super().__init__(timeout=None)
        self.inter = inter
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if self.language == "En":
            self.language = "Ru"
            button.label = "Translate"
            button.emoji = "🇺🇸"
            self.children[1].label = "Полные правила"
            self.children[1].url = ruFullRulesLink
            await self.inter.edit_original_response(embeds=[embedRuleImageRu, embedRuleRu], view=self)
        elif self.language == "Ru":
            self.language = "En"
            button.label = "Перевести"
            button.emoji = "🇷🇺"
            self.children[1].label = "Full rules"

            self.children[1].url = enFullRulesLink
            await self.inter.edit_original_response(embeds=[embedRuleImageEn, embedRuleEn], view=self)
        await inter.response.defer()

    @disnake.ui.button(label="Полные правила", style=disnake.ButtonStyle.link,
                       url="https://wiki.cpps.app/index.php?title=Правила")
    async def FullRules(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        ...


class Roles(disnake.ui.View):
    def __init__(self, inter):
        super().__init__(timeout=None)
        self.inter = inter
        self.language = "Ru"

    @disnake.ui.button(label="Translate", style=disnake.ButtonStyle.primary, emoji="🇺🇸", custom_id="translate")
    async def translate(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if self.language == "En":
            self.language = "Ru"
            button.label = "Translate"
            button.emoji = "🇺🇸"
            await self.inter.edit_original_response(embeds=[embedRolesRu], view=self)
        elif self.language == "Ru":
            self.language = "En"
            button.label = "Перевести"
            button.emoji = "🇷🇺"
            await self.inter.edit_original_response(embeds=[embedRolesEn], view=self)
        await inter.response.defer()
