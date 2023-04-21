import discord


class Question(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, function):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.userID = interaction.user.id
        self.function = function

    async def disableAllItems(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

    async def on_timeout(self):
        await self.disableAllItems()

    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def yesButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.userID:
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        await self.function(interaction)

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def noButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.userID:
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.disableAllItems()
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(content=f"Отменено")


class Continue(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, function):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.userID = interaction.user.id
        self.function = function

    async def disableAllItems(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

    async def on_timeout(self):
        await self.disableAllItems()

    @discord.ui.button(label="Продолжить", style=discord.ButtonStyle.blurple)
    async def continueButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.userID:
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        await self.function(interaction)
