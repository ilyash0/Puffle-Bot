import discord


class Question(discord.ui.View):
    def __init__(self, userID, function):
        super().__init__(timeout=None)
        self.userID = userID
        self.function = function

    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.userID:
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        self.function()

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.userID:
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(content=f"Это кнопка не для вас", ephemeral=True)
            return
        self.function()
        # noinspection PyUnresolvedReferences
        await interaction.response.edit_message(content=f"Отменено")
