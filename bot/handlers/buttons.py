import disnake
from disnake import Embed

from bot.data.pufflebot.fundraising import Fundraising, FundraisingBackers
from bot.handlers.notification import notifyCoinsReceive
from bot.misc.constants import embedRuleImageRu, embedRuleRu, embedRuleImageEn, embedRuleEn, embedRolesRu, \
    embedRolesEn, enFullRulesLink, ruFullRulesLink
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
        await inter.send(statusDict["message"], ephemeral=True)
        if statusDict["code"] == 400:
            return

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
        await notifyCoinsReceive(p, self.receiver, int(coins))

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
