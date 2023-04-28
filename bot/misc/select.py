import disnake
from disnake.ui import Select


class SelectPenguins(Select):
    def __init__(self, penguinsList, function, userID):
        self.disabled = False
        self.function = function
        self.userID = userID

        options = []
        for penguin in penguinsList:
            options.append(disnake.SelectOption(label=penguin["safe_name"], value=penguin["id"]))
        super().__init__(placeholder="Выберите пингвина", options=options, custom_id="penguins")

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.userID:
            await interaction.response.send_message(content=f"Ай-ай-ай,не суй пальцы в розетку", ephemeral=True)
            return
        if self.disabled:
            await interaction.response.send_message(content=f"Вы уже сменили аккаунт", ephemeral=True)
            return
        self.disabled = True

        penguin_id = int(interaction.values[0])
        await self.function(interaction, penguin_id)
