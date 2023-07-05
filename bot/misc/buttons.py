import disnake

from bot.misc.constants import embedRuleImageRu, embedRuleRu, embedRuleImageEn, embedRuleEn, embedRolesRu, embedRolesEn, \
    enFullRulesLink, ruFullRulesLink


class Buttons(disnake.ui.View):
    def __init__(self, inter, function, timeout=900):
        super().__init__(timeout=timeout)
        self.inter = inter
        self.userID = inter.user.id if inter is not None else None
        self.function = function

    async def disableAllItems(self):
        for item in self.children:
            item.disabled = True
        await self.inter.edit_original_response(view=self)

    async def on_timeout(self):
        await self.disableAllItems()


class Question(Buttons):
    def __init__(self, inter, function):
        super().__init__(inter, function)

    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.green, custom_id="yes")
    async def yesButton(self, _, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await self.function(inter)

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red, custom_id="no")
    async def noButton(self, _, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await inter.response.send_message(content=f"Отменено")


class Logout(Buttons):
    def __init__(self, inter: disnake.CommandInteraction, function):
        super().__init__(inter, function)

    @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.gray, custom_id="no")
    async def noButton(self, _, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await inter.response.send_message(content=f"Отменено")

    @disnake.ui.button(label="Выйти", style=disnake.ButtonStyle.red, custom_id="yes")
    async def yesButton(self, _, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await self.function(inter)


class Continue(Buttons):
    def __init__(self, inter: disnake.CommandInteraction, function):
        super().__init__(inter, function)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.blurple, custom_id="continue")
    async def continueButton(self, _, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.function(inter)


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
