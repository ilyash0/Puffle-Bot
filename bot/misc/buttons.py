import disnake


class Buttons(disnake.ui.View):
    def __init__(self, interaction, function, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.userID = interaction.user.id
        self.function = function

    async def disableAllItems(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

    async def on_timeout(self):
        await self.disableAllItems()


class Question(Buttons):
    def __init__(self, interaction: disnake.CommandInteraction, function):
        super().__init__(interaction, function)

    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.green)
    async def yesButton(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        if interaction.user.id != self.userID:
            await interaction.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await self.function(interaction)

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red)
    async def noButton(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        if interaction.user.id != self.userID:
            await interaction.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await interaction.response.send_message(content=f"Отменено")


class Continue(Buttons):
    def __init__(self, interaction: disnake.CommandInteraction, function):
        super().__init__(interaction, function)

    @disnake.ui.button(label="Продолжить", style=disnake.ButtonStyle.blurple)
    async def continueButton(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        if interaction.user.id != self.userID:
            await interaction.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.function(interaction)
