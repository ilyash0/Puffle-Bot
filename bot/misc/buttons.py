import disnake


class Buttons(disnake.ui.View):
    def __init__(self, inter, function, timeout: int = 90):
        super().__init__(timeout=timeout)
        self.inter = inter
        self.userID = inter.user.id
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
    async def yesButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await self.function(inter)

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red, custom_id="no")
    async def noButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await inter.response.send_message(content=f"Отменено")


class Logout(Buttons):
    def __init__(self, inter: disnake.CommandInteraction, function):
        super().__init__(inter, function)

    @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.gray, custom_id="no")
    async def noButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await inter.response.send_message(content=f"Отменено")

    @disnake.ui.button(label="Выйти", style=disnake.ButtonStyle.red, custom_id="yes")
    async def yesButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await self.function(inter)


class Continue(Buttons):
    def __init__(self, inter: disnake.CommandInteraction, function):
        super().__init__(inter, function)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.blurple, custom_id="continue")
    async def continueButton(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
        if inter.user.id != self.userID:
            await inter.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.function(inter)
