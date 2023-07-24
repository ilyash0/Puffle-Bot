import disnake


class FundraisingModal(disnake.ui.Modal):
    def __init__(self, function, title):
        self.function = function
        self.title = title

        components = [
            disnake.ui.TextInput(label="Перевести монеты", required=True,
                                 placeholder="Введите сумму", custom_id="payInput")]

        super().__init__(title=self.title, components=components, custom_id="fundraising")

    async def callback(self, inter: disnake.ModalInteraction):
        coins = inter.text_values["payInput"]
        try:
            coins = int(coins)
        except ValueError:
            return await inter.send("Пожалуйста введите правильное число монет", ephemeral=True)

        await self.function(inter, int(coins))
