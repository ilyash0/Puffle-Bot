import disnake


class LoginModal(disnake.ui.Modal):
    def __init__(self, function):
        self.function = function

        components = [
            disnake.ui.TextInput(label="Одноразовый код аутентификации", required=True,
                                 placeholder="Введите код, который вы получили в открытке", custom_id="authCodeInput")]

        super().__init__(title="Привяжите свои аккаунты", components=components, custom_id="login")

    async def callback(self, inter: disnake.ModalInteraction):
        authCode = inter.text_values["authCodeInput"]
        await self.function(inter, authCode)
